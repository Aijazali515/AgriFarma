# -*- coding: utf-8 -*-
"""
Global Search Blueprint
Provides unified search across Forum, Blog, Shop, and Consultancy modules
"""
from flask import Blueprint, render_template, request
from sqlalchemy import or_, func
from agrifarma.extensions import db
from agrifarma.models.forum import Thread, Post
from agrifarma.models.blog import BlogPost
from agrifarma.models.ecommerce import Product
from agrifarma.models.consultancy import Consultant

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/')
def global_search():
    """Global search across all modules"""
    query = request.args.get('q', '').strip()
    module = request.args.get('module', 'all').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    results = {
        'query': query,
        'module': module,
        'forum': [],
        'blog': [],
        'shop': [],
        'consultants': [],
        'total': 0
    }
    
    if not query or len(query) < 2:
        return render_template('search_results.html', results=results, page=page)
    
    search_pattern = f'%{query}%'
    
    # Search Forum
    if module in ['all', 'forum']:
        # Search threads by title or posts by content
        forum_threads = Thread.query.filter(
            Thread.title.ilike(search_pattern)
        ).order_by(Thread.created_at.desc()).limit(per_page if module == 'forum' else 5).all()
        
        # Also search in post content
        threads_from_posts = db.session.query(Thread).join(Post).filter(
            Post.content.ilike(search_pattern)
        ).distinct().order_by(Thread.created_at.desc()).limit(5).all()
        
        # Combine and deduplicate
        all_threads = list({t.id: t for t in (forum_threads + threads_from_posts)}.values())[:per_page if module == 'forum' else 5]
        
        results['forum'] = [{
            'id': t.id,
            'title': t.title,
            'body': t.posts[0].content[:200] + '...' if t.posts and len(t.posts[0].content) > 200 else (t.posts[0].content if t.posts else ''),
            'author': t.author.profile.name if t.author.profile else t.author.email,
            'created_at': t.created_at,
            'category': t.category.name if t.category else 'General',
            'replies': len(t.posts)
        } for t in all_threads]
    
    # Search Blog
    if module in ['all', 'blog']:
        blog_posts = BlogPost.query.filter(
            BlogPost.approved == True,
            or_(
                BlogPost.title.ilike(search_pattern),
                BlogPost.content.ilike(search_pattern),
                BlogPost.category.ilike(search_pattern)
            )
        ).order_by(BlogPost.created_at.desc()).limit(per_page if module == 'blog' else 5).all()
        
        results['blog'] = [{
            'id': p.id,
            'title': p.title,
            'content': p.content[:200] + '...' if len(p.content) > 200 else p.content,
            'author': p.author.profile.name if p.author.profile else p.author.email,
            'created_at': p.created_at,
            'category': p.category,
            'image': next((item['filename'] for item in p.media_items() if item['kind'] == 'image'), None)
        } for p in blog_posts]
    
    # Search Shop
    if module in ['all', 'shop']:
        products = Product.query.filter(
            Product.status == 'Active',
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Product.category.ilike(search_pattern)
            )
        ).order_by(Product.created_at.desc()).limit(per_page if module == 'shop' else 5).all()
        
        results['shop'] = [{
            'id': p.id,
            'name': p.name,
            'description': p.description[:200] + '...' if p.description and len(p.description) > 200 else p.description,
            'price': float(p.price),
            'category': p.category,
            'image': p.image_list()[0] if p.image_list() else None,
            'inventory': p.inventory
        } for p in products]
    
    # Search Consultants
    if module in ['all', 'consultants']:
        consultants = Consultant.query.filter(
            Consultant.approval_status == 'Approved',
            or_(
                Consultant.category.ilike(search_pattern),
                Consultant.expertise_level.ilike(search_pattern),
                Consultant.contact_email.ilike(search_pattern)
            )
        ).order_by(Consultant.created_at.desc()).limit(per_page if module == 'consultants' else 5).all()
        
        results['consultants'] = [{
            'id': c.id,
            'name': c.user.profile.name if c.user.profile else c.user.email,
            'category': c.category,
            'expertise_level': c.expertise_level,
            'email': c.contact_email
        } for c in consultants]
    
    # Calculate total results
    results['total'] = (
        len(results['forum']) + 
        len(results['blog']) + 
        len(results['shop']) + 
        len(results['consultants'])
    )
    
    return render_template('search_results.html', results=results, page=page)


@bp.route('/autocomplete')
def autocomplete():
    """AJAX endpoint for search autocomplete suggestions"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return {'suggestions': []}
    
    search_pattern = f'%{query}%'
    suggestions = []
    
    # Get top 5 matches from each module
    threads = Thread.query.filter(Thread.title.ilike(search_pattern)).limit(3).all()
    for t in threads:
        suggestions.append({
            'text': t.title,
            'type': 'forum',
            'url': f'/forum/thread/{t.id}'
        })
    
    posts = BlogPost.query.filter(
        BlogPost.approved == True,
        BlogPost.title.ilike(search_pattern)
    ).limit(3).all()
    for p in posts:
        suggestions.append({
            'text': p.title,
            'type': 'blog',
            'url': f'/blog/post/{p.id}'
        })
    
    products = Product.query.filter(
        Product.status == 'Active',
        Product.name.ilike(search_pattern)
    ).limit(3).all()
    for p in products:
        suggestions.append({
            'text': p.name,
            'type': 'shop',
            'url': f'/product/{p.id}'
        })
    
    return {'suggestions': suggestions[:10]}
