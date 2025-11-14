# -*- coding: utf-8 -*-
import math
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from agrifarma.services.security import admin_required as admin_only
from agrifarma.services import email as email_service
from agrifarma.services import payment as payment_service
from sqlalchemy import or_, func

from agrifarma.extensions import db
from agrifarma.models.ecommerce import Product, Review, CartItem, Order, OrderItem
from agrifarma.forms.ecommerce import ProductForm, AddToCartForm, UpdateCartItemForm, CheckoutForm, ReviewForm

bp = Blueprint('shop', __name__)

# Helpers

def is_admin():
    return current_user.is_authenticated and current_user.role == 'Admin'

# Product listing with search/sort/filter
@bp.route('/shop')
def shop_list():
    category = request.args.get('category','').strip()
    q = request.args.get('q','').strip()
    sort = request.args.get('sort','name')  # name|price|new|featured
    page = request.args.get('page', 1, type=int)
    per_page = 12

    base_query = Product.query.filter_by(status='Active')
    if category:
        base_query = base_query.filter(Product.category == category)
    if q:
        base_query = base_query.filter(or_(Product.name.ilike(f'%{q}%'), Product.description.ilike(f'%{q}%')))

    # Sorting at the DB level when possible (name/new); fallback to Python where needed
    if sort == 'new':
        base_query = base_query.order_by(Product.created_at.desc())
    elif sort == 'name':
        base_query = base_query.order_by(Product.name.asc())

    pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    # Python-side sort for price/featured on the page subset
    if products:
        if sort == 'price':
            products = sorted(products, key=lambda p: float(p.price))
        elif sort == 'featured':
            products = sorted(products, key=lambda p: (not p.featured, p.name.lower()))

    featured = [p for p in products if p.featured][:6]
    return render_template('shop.html', products=products, featured=featured, selected_category=category, search_query=q, sort=sort, pagination=pagination)

@bp.route('/product/<int:product_id>', methods=['GET','POST'])
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if not product or product.status != 'Active':
        abort(404)
    add_form = AddToCartForm()
    review_form = ReviewForm()
    # Reviews approved only
    approved_reviews = Review.query.filter_by(product_id=product.id, approved=True).order_by(Review.created_at.desc()).all()
    related = Product.query.filter(Product.category == product.category, Product.id != product.id, Product.status=='Active').limit(4).all()

    if add_form.validate_on_submit() and 'quantity' in request.form:
        if not current_user.is_authenticated:
            flash('Login required to add to cart.', 'warning')
            return redirect(url_for('auth.login'))
        existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        qty = add_form.quantity.data
        if existing:
            existing.quantity += qty
        else:
            db.session.add(CartItem(user_id=current_user.id, product_id=product.id, quantity=qty))
        db.session.commit()
        flash('Added to cart.', 'success')
        return redirect(url_for('shop.product_detail', product_id=product.id))

    if review_form.validate_on_submit() and 'rating' in request.form:
        if not current_user.is_authenticated:
            flash('Login required to review.', 'warning')
            return redirect(url_for('auth.login'))
        review = Review(product_id=product.id, user_id=current_user.id, rating=review_form.rating.data, comment=review_form.comment.data, approved=False)
        db.session.add(review)
        db.session.commit()
        flash('Review submitted for approval.', 'info')
        return redirect(url_for('shop.product_detail', product_id=product.id))

    return render_template('product_detail.html', product=product, add_form=add_form, review_form=review_form, reviews=approved_reviews, related=related)

@bp.route('/product/<int:product_id>/quick-add', methods=['POST'])
@login_required
def quick_add_to_cart(product_id):
    """Quick add to cart from product listing page."""
    product = db.session.get(Product, product_id)
    if not product or product.status != 'Active':
        flash('Product not available.', 'danger')
        return redirect(url_for('shop.shop_list'))
    
    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    qty = 1
    if existing:
        existing.quantity += qty
        flash(f'{product.name} quantity updated in cart!', 'success')
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=product.id, quantity=qty))
        flash(f'{product.name} added to cart!', 'success')
    
    db.session.commit()
    
    # Return to previous page or shop list
    return redirect(request.referrer or url_for('shop.shop_list'))

# Cart operations
@bp.route('/cart')
@login_required
def cart_view():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum([(i.product.price * i.quantity) for i in items]) if items else 0
    update_forms = {i.id: UpdateCartItemForm(quantity=i.quantity) for i in items}
    return render_template('cart.html', items=items, total=total, update_forms=update_forms)

@bp.route('/cart/item/<int:item_id>', methods=['POST'])
@login_required
def cart_update(item_id):
    item = db.session.get(CartItem, item_id)
    if not item or item.user_id != current_user.id:
        abort(404)
    form = UpdateCartItemForm()
    if form.validate_on_submit():
        if form.quantity.data == 0:
            db.session.delete(item)
            flash('Item removed.', 'info')
        else:
            item.quantity = form.quantity.data
            flash('Item updated.', 'success')
        db.session.commit()
    return redirect(url_for('shop.cart_view'))

# Checkout & orders
@bp.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
    form = CheckoutForm()
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Cart is empty.', 'warning')
        return redirect(url_for('shop.shop_list'))
    if form.validate_on_submit():
        # Create order
        order = Order(
            user_id=current_user.id, 
            shipping_address=form.shipping_address.data, 
            payment_method=form.payment_method.data, 
            status='Pending',
            payment_status='Pending'
        )
        db.session.add(order)
        db.session.flush()
        
        # Add order items
        total = 0
        for item in items:
            db.session.add(OrderItem(
                order_id=order.id, 
                product_id=item.product_id, 
                quantity=item.quantity, 
                unit_price=item.product.price
            ))
            total += item.product.price * item.quantity
        
        order.total_amount = total
        
        # Process payment
        payment_result = payment_service.process_order_payment(
            order_id=order.id,
            amount=total,
            customer_email=current_user.email,
            payment_method=form.payment_method.data
        )
        
        if payment_result.success:
            order.payment_status = 'Paid'
            order.payment_transaction_id = payment_result.transaction_id
            order.status = 'Confirmed'
            
            # Clear cart
            for item in items:
                db.session.delete(item)
            
            db.session.commit()
            
            # Send order confirmation email
            email_service.send_order_confirmation_email(
                user_email=current_user.email,
                order_id=order.id,
                total_amount=float(total),
                user_name=current_user.profile.name if current_user.profile else None
            )
            
            flash(f'🎉 Payment Successful! Your order has been placed. Order ID: #{order.id} | Transaction ID: {payment_result.transaction_id} | Total: ${total:.2f}', 'success')
        else:
            order.payment_status = 'Failed'
            db.session.commit()
            flash(f'Payment failed: {payment_result.message}. Please try again.', 'danger')
            return redirect(url_for('shop.checkout'))
        
        return redirect(url_for('shop.order_history'))
    cart_total = sum([(i.product.price * i.quantity) for i in items]) if items else 0
    return render_template('checkout.html', form=form, items=items, cart_total=cart_total)

@bp.route('/orders')
@login_required
def order_history():
    """Order history with optional date range filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        if date_to_str:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
    except ValueError:
        date_from = None
        date_to = None

    base = Order.query.filter_by(user_id=current_user.id)
    if date_from:
        base = base.filter(func.date(Order.created_at) >= date_from)
    if date_to:
        base = base.filter(func.date(Order.created_at) <= date_to)

    pagination = base.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('order_history.html', orders=pagination.items, pagination=pagination, date_from=date_from_str, date_to=date_to_str)

# Admin product CRUD
@bp.route('/admin/shop', methods=['GET','POST'])
@login_required
@admin_only
def admin_dashboard():
    form = ProductForm()
    if form.validate_on_submit():
        featured_flag = form.featured.data == 'true'
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data, category=form.category.data, images=form.images.data, seller_id=current_user.id, status=form.status.data, featured=featured_flag, inventory=form.inventory.data or 0)
        db.session.add(product)
        db.session.commit()
        flash('Product created.', 'success')
        return redirect(url_for('shop.admin_dashboard'))
    products = Product.query.order_by(Product.created_at.desc()).limit(50).all()

    # Sales report with optional date filtering via GET args date_from/date_to
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        if date_to_str:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
    except ValueError:
        date_from = None
        date_to = None

    sales_query = db.session.query(
        Product.id,
        Product.name,
        func.sum(OrderItem.quantity),
        func.sum(OrderItem.quantity * OrderItem.unit_price)
    ).join(OrderItem, OrderItem.product_id == Product.id)\
     .join(Order, OrderItem.order_id == Order.id)

    if date_from:
        sales_query = sales_query.filter(func.date(Order.created_at) >= date_from)
    if date_to:
        sales_query = sales_query.filter(func.date(Order.created_at) <= date_to)

    sales_rows = sales_query.group_by(Product.id, Product.name).all()
    sales_data = None
    if sales_rows:
        from agrifarma.services import analytics
        prepared = [
            {'product_id': r[0], 'name': r[1], 'units': int(r[2] or 0), 'revenue': float(r[3] or 0)} for r in sales_rows
        ]
        sales_data = analytics.top_n(prepared, 'revenue', n=10)
    # Pending reviews for moderation
    pending_reviews = Review.query.filter_by(approved=False).order_by(Review.created_at.desc()).limit(50).all()
    return render_template('admin_dashboard.html', form=form, products=products, sales_data=sales_data, pending_reviews=pending_reviews, date_from=date_from_str, date_to=date_to_str)

@bp.route('/admin/product/<int:product_id>/edit', methods=['POST'])
@login_required
@admin_only
def admin_edit_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        product.images = form.images.data
        product.status = form.status.data
        product.featured = (form.featured.data == 'true')
        if hasattr(form, 'inventory') and form.inventory.data is not None:
            product.inventory = form.inventory.data
        db.session.commit()
        flash('Product updated.', 'info')
    return redirect(url_for('shop.admin_dashboard'))

@bp.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_only
def admin_delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('shop.admin_dashboard'))

# Review moderation
@bp.route('/admin/review/<int:review_id>/<action>', methods=['POST'])
@login_required
@admin_only
def admin_review_action(review_id, action):
    review = db.session.get(Review, review_id)
    if not review:
        abort(404)
    if action == 'approve':
        review.approved = True
    elif action == 'reject':
        review.approved = False
    elif action == 'delete':
        db.session.delete(review)
        db.session.commit()
        flash('Review deleted.', 'info')
        return redirect(url_for('shop.admin_dashboard'))
    db.session.commit()
    flash('Review updated.', 'success')
    return redirect(url_for('shop.admin_dashboard'))
