# -*- coding: utf-8 -*-
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from agrifarma.services.security import admin_required as admin_only
from agrifarma.extensions import db, media
from agrifarma.services import uploads
from agrifarma.models.blog import BlogPost, Comment
from agrifarma.models.likes import BlogLike
from agrifarma.forms.blog import BlogPostForm, CommentForm
from sqlalchemy import or_

bp = Blueprint('blog', __name__, url_prefix='/blog')

@bp.app_context_processor
def inject_latest_trending():
    latest = BlogPost.query.filter_by(approved=True).order_by(BlogPost.created_at.desc()).limit(5).all()
    # Trending stub: latest with most comments (simplified)
    trending = BlogPost.query.filter_by(approved=True).outerjoin(Comment).group_by(BlogPost.id).order_by(db.func.count(Comment.id).desc()).limit(5).all()
    return dict(latest_blog_posts=latest, trending_blog_posts=trending)

@bp.route('/')
def list_posts():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    query = BlogPost.query.filter_by(approved=True)
    if q:
        query = query.filter(or_(BlogPost.title.ilike(f'%{q}%'), BlogPost.tags.ilike(f'%{q}%')))
    pagination = query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('blog_list.html', posts=pagination.items, pagination=pagination, search_query=q)

@bp.route('/post/<int:post_id>', methods=['GET','POST'])
def detail(post_id):
    post = db.session.get(BlogPost, post_id)
    if not post:
        abort(404)
    if not post.approved and (not current_user.is_authenticated or current_user.role != 'Admin'):
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Login required to comment.', 'warning')
            return redirect(url_for('auth.login'))
        comment = Comment(blog_id=post.id, author_id=current_user.id, content=form.content.data)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted.', 'success')
        return redirect(url_for('blog.detail', post_id=post.id))
    comments = Comment.query.filter_by(blog_id=post.id, approved=True).order_by(Comment.created_at.asc()).all()
    return render_template('blog_detail.html', post=post, comments=comments, form=form)

@bp.route('/new', methods=['GET','POST'])
@login_required
def new_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        # Use service helper for robust saving with fallback when flask-uploads is absent
        filenames = uploads.save_files(form.media_files.data)
        post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            author_id=current_user.id,
            tags=form.tags.data or '',
            media_files=','.join(filenames) if filenames else ''
        )
        # Non-admin posts auto-approved (or set to False if moderation required)
        if current_user.role != 'Admin':
            post.approved = True
        db.session.add(post)
        db.session.commit()
        flash('Blog post published.', 'success')
        return redirect(url_for('blog.detail', post_id=post.id))
    return render_template('new_blog.html', form=form)

# Admin moderation
@bp.route('/admin/post/<int:post_id>/approve', methods=['POST'])
@login_required
@admin_only
def approve_post(post_id):
    post = db.session.get(BlogPost, post_id)
    if not post:
        abort(404)
    post.approved = True
    db.session.commit()
    flash('Post approved.', 'info')
    return redirect(url_for('blog.detail', post_id=post.id))

@bp.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_only
def delete_post(post_id):
    post = db.session.get(BlogPost, post_id)
    if not post:
        abort(404)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('blog.list_posts'))

@bp.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_only
def delete_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if not comment:
        abort(404)
    post_id = comment.blog_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('blog.detail', post_id=post_id))

@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like_blog(post_id):
    """Toggle like on a blog post (AJAX-friendly)."""
    post = db.session.get(BlogPost, post_id)
    if not post:
        abort(404)

    existing = BlogLike.query.filter_by(blog_id=post.id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
        action = 'unliked'
    else:
        db.session.add(BlogLike(blog_id=post.id, user_id=current_user.id))
        action = 'liked'
    db.session.commit()

    like_count = BlogLike.query.filter_by(blog_id=post.id).count()
    if request.is_json or request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
        return jsonify({'action': action, 'like_count': like_count})
    flash(f'Blog {action}.', 'success')
    return redirect(request.referrer or url_for('blog.detail', post_id=post.id))
