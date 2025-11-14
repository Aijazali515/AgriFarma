# -*- coding: utf-8 -*-
from datetime import datetime, UTC
from agrifarma.extensions import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), default="User")  # Admin, User, Consultant
    is_active = db.Column(db.Boolean, default=True)
    join_date = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    # 1-1 relationship with Profile
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Shopping cart relationship (without backref since CartItem already defines it)
    cart_items = db.relationship("CartItem", lazy="dynamic", cascade="all, delete-orphan", foreign_keys="CartItem.user_id")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"
