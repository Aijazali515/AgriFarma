"""Upload helper abstractions.

Provides graceful fallbacks when flask-uploads is not installed so calling
code can remain simple (feature-degraded instead of failing hard).
Includes file validation for security and proper file type checking.
"""
from __future__ import annotations
import os
from werkzeug.utils import secure_filename
from typing import Iterable, List, Set
from flask import current_app


ALLOWED_EXTENSIONS: dict[str, Set[str]] = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'},
    'document': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'rtf', 'odt', 'xls', 'xlsx'},
    'all': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'mp4', 'avi', 'mov', 'wmv', 
            'flv', 'webm', 'mkv', 'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 
            'rtf', 'odt', 'xls', 'xlsx'}
}


def allowed_file(filename: str, file_type: str = 'all') -> bool:
    """Check if file extension is allowed.
    
    Args:
        filename: Name of file to check
        file_type: Type category - 'image', 'video', 'document', or 'all'
    
    Returns:
        bool: True if extension is allowed
    """
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = ALLOWED_EXTENSIONS.get(file_type, ALLOWED_EXTENSIONS['all'])
    return ext in allowed


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension without dot.
    
    Args:
        filename: Name of file
        
    Returns:
        str: Extension (e.g., 'jpg', 'pdf') or empty string
    """
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def validate_file_size(file_storage, max_size_mb: int = 50) -> bool:
    """Check if file size is within limit.
    
    Args:
        file_storage: Werkzeug FileStorage object
        max_size_mb: Maximum file size in megabytes
        
    Returns:
        bool: True if file size is acceptable
    """
    if not file_storage:
        return False
    
    # Seek to end to get size
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)  # Reset to beginning
    
    max_bytes = max_size_mb * 1024 * 1024
    return size <= max_bytes


def save_files(storage_list: Iterable, subdir: str = "", file_type: str = 'all', max_size_mb: int = 50) -> List[str]:
    """Persist an iterable of Werkzeug FileStorage objects with validation.

    If flask-uploads is configured (media UploadSet), delegate to it.
    Otherwise, save into UPLOADED_MEDIA_DEST manually.
    
    Args:
        storage_list: Iterable of FileStorage objects
        subdir: Subdirectory within upload folder
        file_type: File type category for validation ('image', 'video', 'document', 'all')
        max_size_mb: Maximum file size in MB
        
    Returns:
        List of stored filenames (relative, not absolute paths).
    """
    saved: List[str] = []
    if not storage_list:
        return saved
    
    media = current_app.extensions.get('uploadset.media') if hasattr(current_app, 'extensions') else None
    base_dest = current_app.config.get('UPLOADED_MEDIA_DEST')
    
    if not base_dest:
        current_app.logger.warning("UPLOADED_MEDIA_DEST not configured")
        return saved
    
    if subdir:
        base_dest = os.path.join(base_dest, subdir)
        os.makedirs(base_dest, exist_ok=True)
    
    for fs in storage_list:
        if not fs or not getattr(fs, 'filename', None):
            continue
            
        original_filename = fs.filename
        
        # Validate file type
        if not allowed_file(original_filename, file_type):
            current_app.logger.warning(
                f"File type not allowed: {original_filename} for type {file_type}"
            )
            continue
        
        # Validate file size
        if not validate_file_size(fs, max_size_mb):
            current_app.logger.warning(
                f"File too large: {original_filename} exceeds {max_size_mb}MB"
            )
            continue
        
        filename = secure_filename(original_filename)
        if not filename:
            continue
        
        # Delegate if UploadSet present
        if media is not None:
            try:
                stored = media.save(fs)
                saved.append(stored)
                continue
            except Exception as e:
                current_app.logger.warning(f"UploadSet save failed: {e}")
                # fallback to manual save
        
        # Manual save
        dest_path = os.path.join(base_dest, filename)
        
        # Avoid overwrite: simple suffix pattern
        root, ext = os.path.splitext(dest_path)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = f"{root}_{counter}{ext}"
            filename = f"{os.path.splitext(filename)[0]}_{counter}{ext}"
            counter += 1
        
        try:
            fs.save(dest_path)
            saved.append(filename)
            current_app.logger.info(f"File saved: {filename}")
        except Exception as e:
            current_app.logger.error(f"Failed to save file {filename}: {e}")
            continue
    
    return saved


def delete_file(filename: str, subdir: str = "") -> bool:
    """Delete an uploaded file.
    
    Args:
        filename: Name of file to delete
        subdir: Subdirectory where file is stored
        
    Returns:
        bool: True if deleted successfully
    """
    if not filename:
        return False
    
    base_dest = current_app.config.get('UPLOADED_MEDIA_DEST')
    if not base_dest:
        return False
    
    if subdir:
        file_path = os.path.join(base_dest, subdir, filename)
    else:
        file_path = os.path.join(base_dest, filename)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            current_app.logger.info(f"File deleted: {filename}")
            return True
    except Exception as e:
        current_app.logger.error(f"Failed to delete file {filename}: {e}")
    
    return False
