# -*- coding: utf-8 -*-
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'agrifarma.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Uploads
    UPLOADED_MEDIA_DEST = str(BASE_DIR / 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'rtf'}
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@agrifarma.local')
    MAIL_SUPPRESS_SEND = os.getenv('MAIL_SUPPRESS_SEND', 'True').lower() in ('true', '1', 'yes')  # Disable in dev by default
    
    # Payment Configuration
    PAYMENT_GATEWAY = os.getenv('PAYMENT_GATEWAY', 'mock')  # mock, stripe, jazzcash
    
    # Stripe Configuration (if using Stripe)
    PAYMENT_STRIPE_CONFIG = {
        'api_key': os.getenv('STRIPE_SECRET_KEY', ''),
        'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    }
    
    # JazzCash Configuration (if using JazzCash)
    PAYMENT_JAZZCASH_CONFIG = {
        'merchant_id': os.getenv('JAZZCASH_MERCHANT_ID', ''),
        'password': os.getenv('JAZZCASH_PASSWORD', ''),
        'integrity_salt': os.getenv('JAZZCASH_INTEGRITY_SALT', '')
    }
    
    # Low inventory threshold for alerts
    LOW_INVENTORY_THRESHOLD = int(os.getenv('LOW_INVENTORY_THRESHOLD', 5))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
