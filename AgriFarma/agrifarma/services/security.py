from __future__ import annotations
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(func=None):
    """Decorator enforcing Admin role; can be used on view functions.

    Usage:
    @admin_required
    def view(): ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != 'Admin':
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator(func) if func else decorator
