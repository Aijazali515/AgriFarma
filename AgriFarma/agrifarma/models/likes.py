# -*- coding: utf-8 -*-
"""Like models for forum posts and blog posts."""
from datetime import datetime, UTC
from agrifarma.extensions import db

class PostLike(db.Model):
    """Stores likes for forum posts."""
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # Unique constraint: one like per user per post
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='uq_post_user_like'),)
    
    post = db.relationship('Post', backref='likes')
    user = db.relationship('User')

class BlogLike(db.Model):
    """Stores likes for blog posts."""
    __tablename__ = 'blog_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # Unique constraint: one like per user per blog
    __table_args__ = (db.UniqueConstraint('blog_id', 'user_id', name='uq_blog_user_like'),)
    
    blog = db.relationship('BlogPost', backref='likes')
    user = db.relationship('User')
