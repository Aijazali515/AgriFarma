# -*- coding: utf-8 -*-
from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app, abort
from sqlalchemy import or_
from agrifarma.extensions import db
from agrifarma.models.ecommerce import Product
from agrifarma.models.blog import BlogPost
from agrifarma.models.forum import Thread, Post
from agrifarma.models.consultancy import Consultant

bp = Blueprint('api', __name__, url_prefix='/api/v1')


def _auth_ok() -> bool:
    token = None
    # Support both Authorization: Bearer <token> and X-API-KEY
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth.split(' ', 1)[1].strip()
    if not token:
        token = request.headers.get('X-API-KEY')
    allowed = set()
    cfg_token = current_app.config.get('API_TOKEN')
    if cfg_token:
        allowed.add(cfg_token)
    cfg_tokens = current_app.config.get('API_TOKENS') or []
    for t in cfg_tokens:
        if t:
            allowed.add(t)
    return token in allowed if allowed else True  # if not configured, allow in dev


def require_api_key():
    if not _auth_ok():
        abort(401)


def paginate_query(query, page: int, per_page: int):
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    return items, total


@bp.before_request
def guard():
    # Basic guard for all API endpoints
    require_api_key()


@bp.get('/products')
def products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    q = Product.query.filter(Product.status == 'Active').order_by(Product.created_at.desc())
    items, total = paginate_query(q, page, per_page)
    data = [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price or 0),
            'category': p.category,
            'inventory': p.inventory,
            'images': p.image_list() if hasattr(p, 'image_list') else []
        }
        for p in items
    ]
    return jsonify({'items': data, 'page': page, 'per_page': per_page, 'total': total})


@bp.get('/blog_posts')
def blog_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    q = BlogPost.query.filter(BlogPost.approved == True).order_by(BlogPost.created_at.desc())
    items, total = paginate_query(q, page, per_page)
    data = [
        {
            'id': b.id,
            'title': b.title,
            'content': b.content[:300],
            'category': b.category,
            'author': b.author.profile.name if b.author and b.author.profile else b.author.email if b.author else None,
            'tags': b.tag_list(),
            'media': b.media_items(),
            'created_at': b.created_at.isoformat() if b.created_at else None
        }
        for b in items
    ]
    return jsonify({'items': data, 'page': page, 'per_page': per_page, 'total': total})


@bp.get('/forum_threads')
def forum_threads():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    q = Thread.query.order_by(Thread.created_at.desc())
    items, total = paginate_query(q, page, per_page)
    data = []
    for t in items:
        posts_count = Post.query.filter_by(thread_id=t.id).count()
        data.append({
            'id': t.id,
            'title': t.title,
            'category': t.category.name if t.category else None,
            'author': t.author.profile.name if t.author and t.author.profile else t.author.email if t.author else None,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'posts_count': posts_count
        })
    return jsonify({'items': data, 'page': page, 'per_page': per_page, 'total': total})


@bp.get('/consultants')
def consultants():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    q = Consultant.query.filter(Consultant.approval_status == 'Approved').order_by(Consultant.created_at.desc())
    items, total = paginate_query(q, page, per_page)
    data = [
        {
            'id': c.id,
            'name': c.user.profile.name if c.user and c.user.profile else c.user.email if c.user else None,
            'category': c.category,
            'expertise_level': c.expertise_level,
            'email': c.contact_email,
            'created_at': c.created_at.isoformat() if c.created_at else None
        }
        for c in items
    ]
    return jsonify({'items': data, 'page': page, 'per_page': per_page, 'total': total})


@bp.get('/search')
def search():
    qstr = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if len(qstr) < 2:
        return jsonify({'items': [], 'total': 0, 'page': page, 'per_page': per_page})
    # products
    products_q = Product.query.filter(
        or_(Product.name.ilike(f'%{qstr}%'), Product.description.ilike(f'%{qstr}%'))
    ).order_by(Product.created_at.desc())
    prod_items, prod_total = paginate_query(products_q, page, per_page)
    # blog
    blog_q = BlogPost.query.filter(
        BlogPost.approved == True,
        or_(BlogPost.title.ilike(f'%{qstr}%'), BlogPost.content.ilike(f'%{qstr}%'))
    ).order_by(BlogPost.created_at.desc())
    blog_items, blog_total = paginate_query(blog_q, page, per_page)
    # forum (by thread titles only for simplicity)
    thread_q = Thread.query.filter(Thread.title.ilike(f'%{qstr}%')).order_by(Thread.created_at.desc())
    thread_items, thread_total = paginate_query(thread_q, page, per_page)

    data = {
        'query': qstr,
        'products': [{'id': p.id, 'name': p.name, 'price': float(p.price or 0)} for p in prod_items],
        'blog_posts': [{'id': b.id, 'title': b.title} for b in blog_items],
        'forum_threads': [{'id': t.id, 'title': t.title} for t in thread_items],
        'totals': {
            'products': prod_total,
            'blog_posts': blog_total,
            'forum_threads': thread_total
        }
    }
    return jsonify(data)
