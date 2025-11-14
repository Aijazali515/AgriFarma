# -*- coding: utf-8 -*-
from __future__ import annotations
from datetime import datetime, timedelta, UTC
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from agrifarma.services.security import admin_required
from sqlalchemy import func, or_, and_

from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.ecommerce import Product, Order, OrderItem, Review
from agrifarma.models.blog import BlogPost, Comment
from agrifarma.models.forum import Thread, Post
from agrifarma.models.consultancy import Consultant
from agrifarma.services import analytics

bp = Blueprint('admin', __name__, url_prefix='/admin')


# Error handlers only for admin blueprint routes
@bp.errorhandler(400)
@bp.errorhandler(403)
@bp.errorhandler(404)
def handle_errors(error):
    code = getattr(error, 'code', 500)
    return render_template('admin_error.html', code=code, message=str(error)), code

@bp.route('/')
@login_required
@admin_required
def dashboard():
    # Quick stats
    users_count = db.session.query(func.count(User.id)).scalar() or 0
    products_count = db.session.query(func.count(Product.id)).scalar() or 0
    orders_count = db.session.query(func.count(Order.id)).scalar() or 0
    pending_posts = BlogPost.query.filter_by(approved=False).count()

    # Recent users
    recent_users = User.query.order_by(User.join_date.desc()).limit(10).all()

    # Additional system metrics displayed as cards
    forum_threads = Thread.query.count()
    approved_posts = BlogPost.query.filter_by(approved=True).count()
    consultants_count = Consultant.query.filter(Consultant.approval_status == 'Approved').count()
    reviews_count = Review.query.count()

    # Registration trend (last N days, default 14)
    trend_days = request.args.get('reg_days', 14, type=int)
    start_window = datetime.now(UTC) - timedelta(days=trend_days - 1)
    window_users = User.query.filter(User.join_date >= start_window).all()
    reg_trend = analytics.registration_trend(window_users, trend_days) if window_users else analytics.registration_trend([], trend_days)

    # Orders by status (pie)
    status_rows = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    orders_by_status = {row[0] or 'Unknown': int(row[1]) for row in status_rows}

    # Revenue over time (last 30 days) - consider Paid orders only
    days = 30
    start_revenue = datetime.now(UTC) - timedelta(days=days-1)
    paid_orders = Order.query.filter(Order.created_at >= start_revenue).all()
    revenue_series = {}
    for o in paid_orders:
        # Treat Confirmed/Paid as revenue; fall back to total_amount if present
        if getattr(o, 'payment_status', None) == 'Paid' or getattr(o, 'status', '') in ('Confirmed', 'Completed'):
            d = o.created_at.date().isoformat()
            revenue_series[d] = float(revenue_series.get(d, 0.0) + float(getattr(o, 'total_amount', 0) or 0))
    # Ensure contiguous days for charting
    series_labels = []
    series_values = []
    cur_date = start_revenue.date()
    end_date = datetime.now(UTC).date()
    while cur_date <= end_date:
        k = cur_date.isoformat()
        series_labels.append(k)
        series_values.append(round(revenue_series.get(k, 0.0), 2))
        cur_date += timedelta(days=1)

    # Top products by revenue (last 30 days)
    top_rows = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
    ).join(OrderItem, OrderItem.product_id == Product.id)
    top_rows = top_rows.join(Order, OrderItem.order_id == Order.id)
    top_rows = top_rows.filter(Order.created_at >= start_revenue)
    top_rows = top_rows.group_by(Product.name).order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc()).limit(5).all()
    top_products = [{'name': r[0], 'revenue': float(r[1] or 0)} for r in top_rows]

    return render_template(
        'admin_analytics_dashboard.html',
        users_count=users_count,
        products_count=products_count,
        orders_count=orders_count,
        pending_posts=pending_posts,
        recent_users=recent_users,
        reg_trend=reg_trend,
        trend_days=trend_days,
        # additional metrics
        forum_threads=forum_threads,
        approved_posts=approved_posts,
        consultants_count=consultants_count,
        reviews_count=reviews_count,
        orders_by_status=orders_by_status,
        revenue_labels=series_labels,
        revenue_values=series_values,
        top_products=top_products,
    )

@bp.route('/users', methods=['GET','POST'])
@login_required
@admin_required
def users():
    if request.method == 'POST':
        uid = request.form.get('user_id', type=int)
        action = request.form.get('action', '')
        user = db.session.get(User, uid)
        if not user:
            abort(404)
        if action == 'deactivate':
            user.is_active = False
        elif action == 'activate':
            user.is_active = True
        db.session.commit()
        flash('User status updated.', 'info')
        return redirect(url_for('admin.users'))
    # list users
    q = request.args.get('q','').strip()
    query = User.query
    if q:
        query = query.filter(User.email.ilike(f'%{q}%'))
    users = query.order_by(User.join_date.desc()).limit(100).all()
    return render_template('user_management.html', users=users, search_query=q)

@bp.route('/moderation', methods=['GET','POST'])
@login_required
@admin_required
def moderation():
    if request.method == 'POST':
        kind = request.form.get('kind')  # 'product' or 'blog'
        action = request.form.get('action')
        if kind == 'product':
            pid = request.form.get('product_id', type=int)
            p = db.session.get(Product, pid)
            if not p:
                abort(404)
            if action == 'approve':
                p.status = 'Active'
            elif action == 'deactivate':
                p.status = 'Inactive'
            elif action == 'delete':
                db.session.delete(p)
            db.session.commit()
        elif kind == 'blog':
            bid = request.form.get('post_id', type=int)
            bpst = db.session.get(BlogPost, bid)
            if not bpst:
                abort(404)
            if action == 'approve':
                bpst.approved = True
            elif action == 'delete':
                db.session.delete(bpst)
            db.session.commit()
        flash('Moderation action applied.', 'success')
        return redirect(url_for('admin.moderation'))
    # GET lists
    inactive_products = Product.query.filter_by(status='Inactive').order_by(Product.created_at.desc()).all()
    pending_posts = BlogPost.query.filter_by(approved=False).order_by(BlogPost.created_at.desc()).all()
    return render_template('product_moderation.html', products=inactive_products, posts=pending_posts)

@bp.route('/reports')
@login_required
@admin_required
def reports():
    # Date range filters
    fmt = '%Y-%m-%d'
    today = datetime.now(UTC).date()
    start_str = request.args.get('start', (today - timedelta(days=30)).strftime(fmt))
    end_str = request.args.get('end', today.strftime(fmt))
    try:
        start = datetime.strptime(start_str, fmt).replace(tzinfo=UTC)
        end = datetime.strptime(end_str, fmt).replace(tzinfo=UTC) + timedelta(days=1)
    except ValueError:
        abort(400)

    # Top selling products in range
    rows = db.session.query(
        Product.id, Product.name,
        func.sum(OrderItem.quantity).label('units'),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
    ).join(OrderItem, OrderItem.product_id == Product.id)
    rows = rows.join(Order, OrderItem.order_id == Order.id).filter(Order.created_at >= start, Order.created_at < end)
    rows = rows.group_by(Product.id, Product.name).all()
    top_revenue = None
    top_units = None
    if rows:
        prepped = [
            {'product_id': r[0], 'name': r[1], 'units': int(r[2] or 0), 'revenue': float(r[3] or 0)}
            for r in rows
        ]
        top_revenue = analytics.top_n(prepped, 'revenue', n=10)
        top_units = analytics.top_n(prepped, 'units', n=10)

    # Low inventory alerts
    low_threshold = request.args.get('low', None, type=int)
    if low_threshold is None:
        low_threshold = int(current_app.config.get('LOW_INVENTORY_THRESHOLD', 5))
    low_inventory = Product.query.filter(Product.inventory < low_threshold).order_by(Product.inventory.asc()).limit(50).all()

    # New user registrations by date range (counts per day)
    users_q = User.query.filter(User.join_date >= start, User.join_date < end, User.role == 'User').all()
    reg_data = analytics.count_registrations_by_day(users_q) if users_q else None

    # Order summaries and filter
    status = request.args.get('status','')
    customer = request.args.get('customer','').strip()
    orders_query = Order.query.filter(Order.created_at >= start, Order.created_at < end)
    if status:
        orders_query = orders_query.filter(Order.status == status)
    if customer:
        orders_query = orders_query.join(User, User.id == Order.user_id).filter(User.email.ilike(f'%{customer}%'))
    orders = orders_query.order_by(Order.created_at.desc()).limit(200).all()

    return render_template('reports.html',
                           start=start_str, end=end_str, status=status, customer=customer, low=low_threshold,
                           top_revenue=top_revenue, top_units=top_units, low_inventory=low_inventory, reg_data=reg_data, orders=orders)


@bp.route('/reports/sales.csv')
@login_required
@admin_required
def report_sales_csv():
    # optional date range
    fmt = '%Y-%m-%d'
    today = datetime.now(UTC).date()
    start_str = request.args.get('start', (today - timedelta(days=30)).strftime(fmt))
    end_str = request.args.get('end', today.strftime(fmt))
    try:
        start = datetime.strptime(start_str, fmt).replace(tzinfo=UTC)
        end = datetime.strptime(end_str, fmt).replace(tzinfo=UTC) + timedelta(days=1)
    except ValueError:
        abort(400)

    q = db.session.query(
        Order.id.label('order_id'),
        Order.created_at.label('order_date'),
        Order.status.label('order_status'),
        Order.payment_status.label('payment_status'),
        OrderItem.product_id,
        Product.name.label('product_name'),
        OrderItem.quantity,
        OrderItem.unit_price,
        (OrderItem.quantity * OrderItem.unit_price).label('line_total')
    ).join(OrderItem, OrderItem.order_id == Order.id).join(Product, Product.id == OrderItem.product_id)
    q = q.filter(Order.created_at >= start, Order.created_at < end)
    rows = q.all()

    try:
        import pandas as pd  # type: ignore
    except Exception:
        abort(500, description='pandas is required for CSV export')

    df = pd.DataFrame([{
        'order_id': r.order_id,
        'order_date': r.order_date.strftime('%Y-%m-%d %H:%M:%S') if r.order_date else '',
        'order_status': r.order_status,
        'payment_status': r.payment_status,
        'product_id': r.product_id,
        'product_name': r.product_name,
        'quantity': int(r.quantity or 0),
        'unit_price': float(r.unit_price or 0),
        'line_total': float(r.line_total or 0),
    } for r in rows])

    csv_bytes = df.to_csv(index=False).encode('utf-8')
    from flask import Response
    return Response(csv_bytes, mimetype='text/csv', headers={
        'Content-Disposition': f'attachment; filename=sales_{start_str}_to_{end_str}.csv'
    })


@bp.route('/reports/sales.xlsx')
@login_required
@admin_required
def report_sales_xlsx():
    # optional date range
    fmt = '%Y-%m-%d'
    today = datetime.now(UTC).date()
    start_str = request.args.get('start', (today - timedelta(days=30)).strftime(fmt))
    end_str = request.args.get('end', today.strftime(fmt))
    try:
        start = datetime.strptime(start_str, fmt).replace(tzinfo=UTC)
        end = datetime.strptime(end_str, fmt).replace(tzinfo=UTC) + timedelta(days=1)
    except ValueError:
        abort(400)

    q = db.session.query(
        Order.id.label('order_id'),
        Order.created_at.label('order_date'),
        Order.status.label('order_status'),
        Order.payment_status.label('payment_status'),
        OrderItem.product_id,
        Product.name.label('product_name'),
        OrderItem.quantity,
        OrderItem.unit_price,
        (OrderItem.quantity * OrderItem.unit_price).label('line_total')
    ).join(OrderItem, OrderItem.order_id == Order.id).join(Product, Product.id == OrderItem.product_id)
    q = q.filter(Order.created_at >= start, Order.created_at < end)
    rows = q.all()

    try:
        import pandas as pd  # type: ignore
    except Exception:
        abort(500, description='pandas is required for Excel export')

    import io
    buf = io.BytesIO()
    df = pd.DataFrame([{
        'order_id': r.order_id,
        'order_date': r.order_date,
        'order_status': r.order_status,
        'payment_status': r.payment_status,
        'product_id': r.product_id,
        'product_name': r.product_name,
        'quantity': int(r.quantity or 0),
        'unit_price': float(r.unit_price or 0),
        'line_total': float(r.line_total or 0),
    } for r in rows])
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:  # type: ignore
        df.to_excel(writer, index=False, sheet_name='Sales')
        # Summary sheet
        summary = df.groupby('order_status')['line_total'].sum().reset_index()
        summary.to_excel(writer, index=False, sheet_name='Summary')
    buf.seek(0)
    from flask import send_file
    return send_file(buf, as_attachment=True, download_name=f'sales_{start_str}_to_{end_str}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
