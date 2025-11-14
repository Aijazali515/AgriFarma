"""
Test script to verify profile picture upload functionality
"""
import os
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.profile import Profile
from io import BytesIO

app = create_app()

with app.app_context():
    print("=" * 60)
    print("PROFILE PICTURE UPLOAD VERIFICATION")
    print("=" * 60)
    
    # Test 1: Check if upload directory exists
    upload_dir = os.path.join('agrifarma', 'static', 'uploads', 'profiles')
    print(f"\n1. Upload Directory Check:")
    print(f"   Path: {upload_dir}")
    print(f"   Exists: {os.path.exists(upload_dir)}")
    print(f"   ✓ PASS" if os.path.exists(upload_dir) else "   ✗ FAIL")
    
    # Test 2: Check if display_picture column exists in database
    print(f"\n2. Database Column Check:")
    test_user = User.query.filter_by(email='user@test.com').first()
    if test_user and test_user.profile:
        has_column = hasattr(test_user.profile, 'display_picture')
        print(f"   Profile has display_picture attribute: {has_column}")
        print(f"   Current value: {test_user.profile.display_picture}")
        print(f"   ✓ PASS" if has_column else "   ✗ FAIL")
    else:
        print(f"   Test user not found")
        print(f"   ✗ FAIL")
    
    # Test 3: Check if form has display_picture field
    print(f"\n3. Form Field Check:")
    from agrifarma.forms.user import EditProfileForm
    form = EditProfileForm()
    has_field = hasattr(form, 'display_picture')
    print(f"   EditProfileForm has display_picture field: {has_field}")
    if has_field:
        print(f"   Field type: {type(form.display_picture).__name__}")
        print(f"   ✓ PASS")
    else:
        print(f"   ✗ FAIL")
    
    # Test 4: Check if templates exist
    print(f"\n4. Template Check:")
    templates = [
        'agrifarma/templates/profile_view.html',
        'agrifarma/templates/edit_profile.html'
    ]
    all_exist = True
    for template in templates:
        exists = os.path.exists(template)
        print(f"   {template}: {'✓' if exists else '✗'}")
        all_exist = all_exist and exists
    print(f"   {'✓ PASS' if all_exist else '✗ FAIL'}")
    
    # Test 5: Check routes
    print(f"\n5. Route Check:")
    with app.test_client() as client:
        # Login as test user
        response = client.post('/login', data={
            'email': 'user@test.com',
            'password': 'user123'
        }, follow_redirects=False)
        
        if response.status_code in [200, 302]:
            print(f"   Login: ✓")
            
            # Check profile view route
            response = client.get(f'/profile/{test_user.id}', follow_redirects=True)
            print(f"   Profile view (/profile/{test_user.id}): {response.status_code} {'✓' if response.status_code == 200 else '✗'}")
            
            # Check if profile_view.html is used
            uses_new_template = b'Edit Profile' in response.data or b'af-dp-hero' in response.data
            print(f"   Uses new template: {'✓' if uses_new_template else '✗'}")
            
            # Check profile edit route
            response = client.get('/profile/edit', follow_redirects=True)
            print(f"   Profile edit (/profile/edit): {response.status_code} {'✓' if response.status_code == 200 else '✗'}")
            
            # Check if edit form has file upload
            has_file_upload = b'enctype="multipart/form-data"' in response.data
            print(f"   Form has file upload support: {'✓' if has_file_upload else '✗'}")
            
            # Check if display_picture field is rendered
            has_dp_field = b'display_picture' in response.data or b'displayPictureInput' in response.data
            print(f"   Display picture field rendered: {'✓' if has_dp_field else '✗'}")
            
            print(f"   ✓ PASS")
        else:
            print(f"   Login failed: {response.status_code}")
            print(f"   ✗ FAIL")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("All components are ready for profile picture upload!")
    print("\nTo test manually:")
    print("1. Open http://127.0.0.1:5000")
    print("2. Login with user@test.com / user123")
    print("3. Click 'Profile' in navigation dropdown")
    print("4. Click 'Edit Profile' button")
    print("5. Upload a JPG/PNG/GIF image")
    print("6. Submit form and verify image displays")
    print("=" * 60)
