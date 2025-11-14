# -*- coding: utf-8 -*-
from datetime import datetime, UTC
from agrifarma.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    parent = db.relationship('Category', remote_side=[id], backref='children')

    def __repr__(self):
        return f"<Category {self.name}>"

class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    category = db.relationship('Category', backref='threads')
    author = db.relationship('User', backref='threads', foreign_keys=[author_id])
    posts = db.relationship('Post', backref='thread', cascade='all, delete-orphan', order_by='Post.created_at')

    def __repr__(self):
        return f"<Thread {self.title}>"

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    author = db.relationship('User', backref='posts', foreign_keys=[author_id])

    def __repr__(self):
        return f"<Post {self.id} on Thread {self.thread_id}>"
