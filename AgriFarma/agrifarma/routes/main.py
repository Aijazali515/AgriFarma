# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request
from flask_login import current_user
from agrifarma.extensions import db
from agrifarma.models.forum import Thread
from agrifarma.models.blog import BlogPost
from agrifarma.models.consultancy import Consultant
from agrifarma.models.ecommerce import Product, Order
from agrifarma.models.user import User
from sqlalchemy import func

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """
    Role-based dashboard:
    - Admins see analytics dashboard with system metrics
    - Regular users see community dashboard with recent activity
    """
    from flask import current_app
    # Quick diagnostic path: return simple OK if ?raw=1
    if request.args.get('raw') == '1':
        return "OK", 200
    current_app.logger.debug("[index] Entered index route")
    if current_user.is_authenticated and current_user.role == 'Admin':
        current_app.logger.debug("[index] Rendering admin analytics dashboard")
        # Admin Dashboard - Analytics and moderation
        users_count = db.session.query(func.count(User.id)).scalar()
        if users_count is None:
            users_count = 0
        products_count = db.session.query(func.count(Product.id)).scalar()
        if products_count is None:
            products_count = 0
        orders_count = db.session.query(func.count(Order.id)).scalar()
        if orders_count is None:
            orders_count = 0
        pending_posts = BlogPost.query.filter_by(approved=False).count()
        if pending_posts is None:
            pending_posts = 0

        # Recent users
        recent_users = User.query.order_by(User.join_date.desc()).limit(10).all()
        if recent_users is None:
            recent_users = []

        # Pending items for moderation
        pending_blog_posts = BlogPost.query.filter_by(approved=False).order_by(BlogPost.created_at.desc()).limit(5).all()
        if pending_blog_posts is None:
            pending_blog_posts = []
        pending_items = []
        for post in pending_blog_posts:
            pending_items.append({
                'type': 'blog',
                'title': post.title or '',
                'author': post.author.email.split('@')[0] if post.author and post.author.email else 'Unknown',
                'date': post.created_at.strftime('%b %d, %Y') if post.created_at else ''
            })

        # System metrics
        forum_threads = db.session.query(func.count(Thread.id)).scalar()
        if forum_threads is None:
            forum_threads = 0
        approved_posts = BlogPost.query.filter_by(approved=True).count()
        if approved_posts is None:
            approved_posts = 0
        consultants_count = Consultant.query.filter_by(approval_status='Approved').count()
        if consultants_count is None:
            consultants_count = 0
        reviews_count = 0  # Placeholder for future review count

        # Safe defaults for analytics charts expected by the admin template
        # These avoid Jinja Undefined values being passed to `tojson`.
        trend_days = 14
        reg_trend = []
        orders_by_status = {}
        revenue_labels = []
        revenue_values = []
        top_products = []

        return render_template(
            'admin_analytics_dashboard.html',
            users_count=users_count,
            products_count=products_count,
            orders_count=orders_count,
            pending_posts=pending_posts,
            recent_users=recent_users,
            pending_items=pending_items,
            forum_threads=forum_threads,
            approved_posts=approved_posts,
            consultants_count=consultants_count,
            reviews_count=reviews_count,
            # analytics defaults
            reg_trend=reg_trend,
            trend_days=trend_days,
            orders_by_status=orders_by_status,
            revenue_labels=revenue_labels,
            revenue_values=revenue_values,
            top_products=top_products
        )
    else:
        current_app.logger.debug("[index] Rendering community dashboard")
        # Community Dashboard - For regular users and guests
        # Quick stats
        forum_count = db.session.query(func.count(Thread.id)).scalar()
        if forum_count is None:
            forum_count = 0
        blog_count = BlogPost.query.filter_by(approved=True).count()
        if blog_count is None:
            blog_count = 0
        consultant_count = Consultant.query.filter_by(approval_status='Approved').count()
        if consultant_count is None:
            consultant_count = 0
        product_count = Product.query.filter_by(status='Active').count()
        if product_count is None:
            product_count = 0
        
        # Recent forum discussions
        recent_threads = Thread.query.order_by(Thread.created_at.desc()).limit(5).all()
        if recent_threads is None:
            recent_threads = []
        
        # Popular blog articles (approved only)
        recent_posts = BlogPost.query.filter_by(approved=True).order_by(BlogPost.created_at.desc()).limit(5).all()
        if recent_posts is None:
            recent_posts = []
        
        # Featured consultants
        consultants = Consultant.query.filter_by(approval_status='Approved').order_by(Consultant.created_at.desc()).limit(4).all()
        if consultants is None:
            consultants = []
        
        # Trending products (active products with inventory)
        products = Product.query.filter_by(status='Active').filter(Product.inventory > 0).order_by(Product.created_at.desc()).limit(4).all()
        if products is None:
            products = []
        
        return render_template(
            'community_dashboard.html',
            forum_count=forum_count,
            blog_count=blog_count,
            consultant_count=consultant_count,
            product_count=product_count,
            recent_threads=recent_threads,
            recent_posts=recent_posts,
            consultants=consultants,
            products=products
        )


@bp.route('/health')
def health():
    """Simple health check returning JSON for uptime probes."""
    from flask import jsonify
    return jsonify({"status": "ok", "service": "agrifarma", "version": 1}), 200


@bp.route('/about')
def about():
    """About Us page - Company information and mission"""
    return render_template('info/about.html')


@bp.route('/contact')
def contact():
    """Contact Us page - Contact form and information"""
    return render_template('info/contact.html')


@bp.route('/faq')
def faq():
    """Frequently Asked Questions page"""
    return render_template('info/faq.html')


@bp.route('/terms')
def terms():
    """Terms of Use page - Legal terms and conditions"""
    return render_template('info/terms.html')


@bp.route('/privacy')
def privacy():
    """Privacy Policy page - Data protection and privacy information"""
    return render_template('info/privacy.html')


@bp.route('/team')
def team():
    """Our Team page - Team members and staff"""
    return render_template('info/team.html')


@bp.route('/partners')
def partners():
    """Partners page - Business partners and collaborators"""
    return render_template('info/partners.html')


@bp.route('/feedback')
def feedback():
    """Feedback page - User feedback form"""
    return render_template('info/feedback.html')


@bp.route('/sitemap')
def sitemap():
    """Site Map page - Complete site navigation"""
    return render_template('info/sitemap.html')
