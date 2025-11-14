from __future__ import annotations
import os
from flask import Blueprint, current_app, send_from_directory, abort
from flask_login import current_user
from agrifarma.extensions import db
from agrifarma.models.blog import BlogPost
from werkzeug.utils import secure_filename

bp = Blueprint('media', __name__, url_prefix='/media')


@bp.route('/<path:filename>')
def serve_media(filename: str):
    # Ensure safe path
    safe = secure_filename(os.path.basename(filename))
    if not safe:
        abort(404)
    base = current_app.config.get('UPLOADED_MEDIA_DEST')
    if not base or not os.path.isdir(base):
        abort(404)
    # Gating: if file is attached to an unapproved blog post, only author or admin may access
    try:
        # First, try to narrow down via LIKE to reduce Python filtering
        candidates = BlogPost.query.filter(BlogPost.media_files.isnot(None)).filter(BlogPost.media_files.ilike(f"%{safe}%")).all()
        for post in candidates:
            files = [f.strip() for f in (post.media_files or '').split(',') if f.strip()]
            if safe in files:
                if not post.approved:
                    if not current_user.is_authenticated:
                        abort(403)
                    if current_user.role != 'Admin' and current_user.id != post.author_id:
                        abort(403)
                break
    except Exception:
        # If lookup fails for any reason, default to public access
        pass

    # Do not trust subdir traversal; flat filenames only for now
    return send_from_directory(base, safe, as_attachment=False)
