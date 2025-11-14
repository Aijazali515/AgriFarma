# -*- coding: utf-8 -*-
from datetime import datetime, UTC
from decimal import Decimal
from agrifarma.extensions import db
from .user import User

PRODUCT_STATUSES = ("Active", "Inactive")
ORDER_STATUSES = ("Pending", "Paid", "Shipped", "Cancelled")
REVIEW_STATUSES = ("Pending", "Approved", "Rejected")

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2), nullable=False, default=0)
    category = db.Column(db.String(64), index=True)
    images = db.Column(db.Text)  # comma-separated filenames
    inventory = db.Column(db.Integer, default=0, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(16), default='Active', index=True)
    featured = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    seller = db.relationship('User')
    reviews = db.relationship('Review', back_populates='product', cascade='all, delete-orphan')

    def image_list(self):
        return [i for i in (self.images or '').split(',') if i]

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    product = db.relationship('Product', back_populates='reviews')
    user = db.relationship('User')

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    user = db.relationship('User')
    product = db.relationship('Product')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    shipping_address = db.Column(db.String(256), nullable=False)
    payment_method = db.Column(db.String(64), nullable=False)  # e.g. COD, card, wallet
    payment_status = db.Column(db.String(32), default='Pending', index=True)  # Pending, Paid, Failed, Refunded
    payment_transaction_id = db.Column(db.String(128))  # Payment gateway transaction ID
    status = db.Column(db.String(16), default='Pending', index=True)  # Order status
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    total_amount = db.Column(db.Numeric(10,2), default=0)

    user = db.relationship('User')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10,2), nullable=False, default=0)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

    def line_total(self):
        return (self.unit_price or Decimal('0')) * self.quantity
