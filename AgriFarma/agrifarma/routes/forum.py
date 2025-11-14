# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload

from agrifarma.extensions import db
from agrifarma.models.forum import Category, Thread, Post
from agrifarma.models.likes import PostLike
from agrifarma.forms.forum import NewThreadForm, ReplyForm, MoveThreadForm

bp = Blueprint("forum", __name__, url_prefix="/forum")

    # Provide latest threads for sidebar
@bp.app_context_processor
def inject_latest_threads():
    # Eager-load author and category to avoid N+1 in sidebar
    latest = (
        Thread.query.options(
            joinedload(Thread.author),
            joinedload(Thread.category)
        )
        .order_by(Thread.created_at.desc())
        .limit(10)
        .all()
    )
    return dict(forum_latest_threads=latest)

@bp.route("/")
def index():
    # Eager-load children and threads collections
    categories = (
        Category.query.options(
            selectinload(Category.children),
            selectinload(Category.threads)
        )
        .filter(Category.parent_id.is_(None))
        .order_by(Category.name.asc())
        .all()
    )
    return render_template("forum_index.html", categories=categories)

@bp.route("/category/<int:category_id>")
def category_view(category_id):
    # Eager-load subcategories for navigation on the page
    category = (
        Category.query.options(
            selectinload(Category.children)
        )
        .filter_by(id=category_id)
        .first()
    )
    if not category:
        abort(404)
    page = request.args.get("page", 1, type=int)
    # Eager-load author for thread list to avoid N+1
    pagination = (
        Thread.query.options(
            joinedload(Thread.author)
        )
        .filter_by(category_id=category.id)
        .order_by(Thread.created_at.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    return render_template("category_view.html", category=category, threads=pagination.items, pagination=pagination)

@bp.route("/thread/<int:thread_id>", methods=["GET", "POST"])
def thread_view(thread_id):
    thread = db.session.get(Thread, thread_id)
    if not thread:
        abort(404)
    form = ReplyForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please login to reply.", "warning")
            return redirect(url_for("auth.login"))
        post = Post(thread_id=thread.id, author_id=current_user.id, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        flash("Reply posted.", "success")
        return redirect(url_for("forum.thread_view", thread_id=thread.id))

    # Eager-load author on posts to avoid N+1 when rendering
    posts = (
        Post.query.options(
            joinedload(Post.author)
        )
        .filter_by(thread_id=thread.id)
        .order_by(Post.created_at.asc())
        .all()
    )
    move_form = None
    if current_user.is_authenticated and current_user.role == "Admin":
        move_form = MoveThreadForm()
        move_form.set_choices()
        if move_form.validate_on_submit() and move_form.category_id.data != thread.category_id:
            thread.category_id = move_form.category_id.data
            db.session.commit()
            flash("Thread moved.", "info")
            return redirect(url_for("forum.thread_view", thread_id=thread.id))

    categories = Category.query.filter(Category.parent_id.is_(None)).order_by(Category.name.asc()).all()
    return render_template("thread_view.html", thread=thread, posts=posts, form=form, move_form=move_form, categories=categories)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_thread():
    form = NewThreadForm()
    form.set_choices()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, category_id=form.category_id.data, author_id=current_user.id)
        db.session.add(thread)
        db.session.flush()
        first_post = Post(thread_id=thread.id, author_id=current_user.id, content=form.content.data)
        db.session.add(first_post)
        db.session.commit()
        flash("Thread created.", "success")
        return redirect(url_for("forum.thread_view", thread_id=thread.id))
    return render_template("new_thread.html", form=form)

@bp.route("/thread/<int:thread_id>/delete", methods=["POST"])
@login_required
def delete_thread(thread_id):
    thread = db.session.get(Thread, thread_id)
    if not thread:
        abort(404)
    if current_user.role != "Admin" and current_user.id != thread.author_id:
        abort(403)
    db.session.delete(thread)
    db.session.commit()
    flash("Thread deleted.", "info")
    return redirect(url_for("forum.index"))

@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        results = Post.query.join(Thread, Post.thread_id == Thread.id) \
            .filter(or_(Post.content.ilike(f"%{q}%"), Thread.title.ilike(f"%{q}%"))) \
            .order_by(Post.created_at.desc()) \
            .limit(50).all()
    return render_template("forum_index.html", categories=Category.query.all(), search_query=q, search_results=results)


@bp.route("/post/<int:post_id>/like", methods=["POST"])
@login_required
def toggle_like_post(post_id):
    """Toggle like on a forum post (AJAX-friendly)."""
    post = db.session.get(Post, post_id)
    if not post:
        abort(404)
    
    existing = PostLike.query.filter_by(post_id=post.id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
        action = 'unliked'
    else:
        db.session.add(PostLike(post_id=post.id, user_id=current_user.id))
        action = 'liked'
    db.session.commit()
    
    like_count = PostLike.query.filter_by(post_id=post.id).count()
    # Return JSON for AJAX or redirect for non-AJAX
    if request.is_json or request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
        return jsonify({'action': action, 'like_count': like_count})
    flash(f'Post {action}.', 'success')
    return redirect(request.referrer or url_for('forum.thread_view', thread_id=post.thread_id))
