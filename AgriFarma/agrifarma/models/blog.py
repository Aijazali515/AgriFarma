# -*- coding: utf-8 -*-
from datetime import datetime, UTC
from agrifarma.extensions import db

PREDEFINED_CATEGORIES = [
    'Success Stories',
    'Techniques',
    'Weather Tips',
    'Market Insights',
    'Soil Health',
    'Irrigation',
]

# Association table for tags (simple CSV storage alternative)

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    tags = db.Column(db.String(255))  # comma-separated tags
    media_files = db.Column(db.String(512))  # comma-separated filenames
    approved = db.Column(db.Boolean, default=True)

    author = db.relationship('User', backref='blog_posts')
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')

    def tag_list(self):
        return [t.strip() for t in self.tags.split(',')] if self.tags else []

    def media_items(self):
        """Return structured media metadata.

        Each item: { 'filename': str, 'ext': str, 'kind': 'image'|'video'|'doc'|'other' }
        Classification based on extension for template rendering.
        """
        items = []
        if not self.media_files:
            return items
        import os
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        video_exts = {'.mp4', '.webm', '.ogg'}
        doc_exts = {'.pdf', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx', '.csv'}
        for raw in self.media_files.split(','):
            fname = raw.strip()
            if not fname:
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext in image_exts:
                kind = 'image'
            elif ext in video_exts:
                kind = 'video'
            elif ext in doc_exts:
                kind = 'doc'
            else:
                kind = 'other'
            items.append({'filename': fname, 'ext': ext, 'kind': kind})
        return items

class Comment(db.Model):
    __tablename__ = 'blog_comments'
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    approved = db.Column(db.Boolean, default=True)

    author = db.relationship('User', backref='comments')
