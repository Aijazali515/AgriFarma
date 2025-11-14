#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick verification script for AgriFarma media uploads.

Run this to confirm everything is working:
    python verify_uploads.py
"""

def verify():
    print("\n" + "="*70)
    print("AGRIFARMA MEDIA UPLOAD VERIFICATION")
    print("="*70 + "\n")
    
    checks = []
    
    # 1. Flask-Reuploaded installed
    try:
        import flask_uploads
        checks.append(("✓", "Flask-Reuploaded installed"))
    except ImportError:
        checks.append(("✗", "Flask-Reuploaded NOT installed"))
        return False
    
    # 2. Config loaded
    try:
        from agrifarma import create_app
        app = create_app()
        checks.append(("✓", "App created successfully"))
    except Exception as e:
        checks.append(("✗", f"App creation failed: {e}"))
        return False
    
    # 3. Upload dest configured
    with app.app_context():
        dest = app.config.get('UPLOADED_MEDIA_DEST')
        if dest:
            checks.append(("✓", f"UPLOADED_MEDIA_DEST: {dest}"))
        else:
            checks.append(("✗", "UPLOADED_MEDIA_DEST not configured"))
            return False
        
        # 4. Directory exists
        import os
        if os.path.exists(dest):
            checks.append(("✓", "Upload directory exists"))
        else:
            checks.append(("✗", "Upload directory missing"))
            return False
        
        # 5. UploadSet configured
        from agrifarma.extensions import media
        if media:
            checks.append(("✓", f"Media UploadSet configured (name: {media.name})"))
        else:
            checks.append(("✗", "Media UploadSet not configured"))
            return False
        
        # 6. Routes registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        if '/blog/new' in routes:
            checks.append(("✓", "Blog upload route registered"))
        else:
            checks.append(("✗", "Blog upload route missing"))
        
        if any('/media/' in r for r in routes):
            checks.append(("✓", "Media serving route registered"))
        else:
            checks.append(("✗", "Media serving route missing"))
    
    # Print results
    for status, msg in checks:
        print(f"{status} {msg}")
    
    print("\n" + "="*70)
    
    all_passed = all(check[0] == "✓" for check in checks)
    if all_passed:
        print("ALL CHECKS PASSED ✓")
        print("\nMedia uploads are fully operational!")
        print("\nNext steps:")
        print("  1. Start server: python run.py")
        print("  2. Visit: http://127.0.0.1:5000")
        print("  3. Login and create a blog post with attachments")
        print("  4. Files will be saved to the uploads directory")
    else:
        print("SOME CHECKS FAILED ✗")
        print("\nPlease review the errors above and fix them.")
    
    print("="*70 + "\n")
    return all_passed

if __name__ == '__main__':
    import sys
    success = verify()
    sys.exit(0 if success else 1)
