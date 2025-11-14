# -*- coding: utf-8 -*-
"""Password reset token model for secure forgot-password flow."""
from datetime import datetime, timedelta
import secrets
from agrifarma.extensions import db

class PasswordResetToken(db.Model):
    """Stores secure tokens for password resets with expiration."""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(128), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, index=True)
    
    user = db.relationship('User', backref='reset_tokens')
    
    @staticmethod
    def create_token(user_id: int, validity_hours: int = 24) -> 'PasswordResetToken':
        """Generate a new secure token for the given user."""
        token_str = secrets.token_urlsafe(64)
        expires = datetime.utcnow() + timedelta(hours=validity_hours)
        token = PasswordResetToken(
            user_id=user_id,
            token=token_str,
            expires_at=expires
        )
        db.session.add(token)
        db.session.commit()
        return token
    
    def is_valid(self) -> bool:
        """Check if token is unused and not expired."""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def mark_used(self) -> None:
        """Mark token as consumed."""
        self.used = True
        db.session.commit()
