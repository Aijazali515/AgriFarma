#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify media upload functionality in AgriFarma.

This script tests:
1. Flask-Uploads (Flask-Reuploaded) is properly configured
2. UPLOADED_MEDIA_DEST is set correctly
3. Upload folder exists and is writable
4. UploadSet is available and functional
5. Media upload service works correctly
"""
import os
import sys
from io import BytesIO
from werkzeug.datastructures import FileStorage

# Test 1: Import and configuration
print("=" * 60)
print("MEDIA UPLOAD CONFIGURATION TEST")
print("=" * 60)

try:
    import flask_uploads
    print("✓ Flask-Uploads (Reuploaded) is installed")
    print(f"  Version: {flask_uploads.__version__ if hasattr(flask_uploads, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"✗ Flask-Uploads import failed: {e}")
    sys.exit(1)

# Test 2: App configuration
from agrifarma import create_app
app = create_app()

with app.app_context():
    upload_dest = app.config.get('UPLOADED_MEDIA_DEST')
    print(f"\n✓ UPLOADED_MEDIA_DEST: {upload_dest}")
    
    if os.path.exists(upload_dest):
        print(f"✓ Upload directory exists")
    else:
        print(f"✗ Upload directory does NOT exist")
        sys.exit(1)
    
    # Test 3: Check if directory is writable
    test_file = os.path.join(upload_dest, '.test_write')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✓ Upload directory is writable")
    except Exception as e:
        print(f"✗ Upload directory is NOT writable: {e}")
        sys.exit(1)
    
    # Test 4: Check UploadSet configuration
    from agrifarma.extensions import media
    if media is not None:
        print(f"✓ Media UploadSet is configured")
        print(f"  Name: {media.name}")
        print(f"  Extensions: {media.extensions[:10]}...")  # Show first 10
    else:
        print(f"✗ Media UploadSet is NOT configured")
        sys.exit(1)
    
    # Test 5: Test upload service
    print("\n" + "=" * 60)
    print("TESTING UPLOAD SERVICE")
    print("=" * 60)
    
    from agrifarma.services import uploads
    
    # Create a mock file
    mock_file = FileStorage(
        stream=BytesIO(b"Test image content for AgriFarma"),
        filename="test_upload_image.jpg",
        content_type="image/jpeg"
    )
    
    try:
        saved_files = uploads.save_files([mock_file])
        if saved_files:
            print(f"✓ Upload service successfully saved file: {saved_files[0]}")
            
            # Verify file exists
            saved_path = os.path.join(upload_dest, saved_files[0])
            if os.path.exists(saved_path):
                print(f"✓ Uploaded file exists at: {saved_path}")
                file_size = os.path.getsize(saved_path)
                print(f"  File size: {file_size} bytes")
                
                # Clean up test file
                os.remove(saved_path)
                print(f"✓ Test file cleaned up")
            else:
                print(f"✗ Uploaded file does NOT exist at expected path")
                sys.exit(1)
        else:
            print(f"✗ Upload service returned empty list")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Upload service failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 6: List existing uploads
    print("\n" + "=" * 60)
    print("EXISTING UPLOADS")
    print("=" * 60)
    
    existing_files = [f for f in os.listdir(upload_dest) if os.path.isfile(os.path.join(upload_dest, f))]
    if existing_files:
        print(f"✓ Found {len(existing_files)} existing upload(s):")
        for f in existing_files[:5]:  # Show first 5
            file_path = os.path.join(upload_dest, f)
            file_size = os.path.getsize(file_path)
            print(f"  - {f} ({file_size} bytes)")
        if len(existing_files) > 5:
            print(f"  ... and {len(existing_files) - 5} more")
    else:
        print("  No existing uploads (this is normal for a new installation)")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    print("\nMedia uploads are fully configured and operational!")
    print(f"Upload directory: {upload_dest}")
    print(f"\nYou can now:")
    print("  1. Navigate to http://127.0.0.1:5000/blog/new")
    print("  2. Create a blog post with image attachments")
    print("  3. Files will be saved to the uploads directory")
    print("  4. Access them via /media/<filename> route")
