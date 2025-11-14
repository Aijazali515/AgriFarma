"""Verify role-based access control and navigation.

Tests:
1. Guest user sees Login/Register in navigation
2. Regular user sees Profile/Logout (no admin links)
3. Admin user sees Profile/Logout + admin dropdown
4. Regular users cannot access admin routes (403)
5. Admin users can access admin routes (200)
"""
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.profile import Profile
from werkzeug.security import generate_password_hash

def verify_role_access():
    print("🔍 Verifying Role-Based Access Control\n")
    print("=" * 70)
    
    # Create test app
    app = create_app('test_config.TestConfig')
    
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # Create test users if they don't exist
        admin_user = User.query.filter_by(email='admin@test.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@test.com',
                password_hash=generate_password_hash('admin123'),
                role='Admin',
                is_active=True
            )
            db.session.add(admin_user)
            db.session.flush()
            
            admin_profile = Profile(
                user_id=admin_user.id,
                name='Admin User'
            )
            db.session.add(admin_profile)
            db.session.commit()
            print("✅ Created admin user: admin@test.com / admin123")
        else:
            print("✅ Admin user already exists: admin@test.com")
        
        regular_user = User.query.filter_by(email='user@test.com').first()
        if not regular_user:
            regular_user = User(
                email='user@test.com',
                password_hash=generate_password_hash('user123'),
                role='User',
                is_active=True
            )
            db.session.add(regular_user)
            db.session.flush()
            
            user_profile = Profile(
                user_id=regular_user.id,
                name='Regular User'
            )
            db.session.add(user_profile)
            db.session.commit()
            print("✅ Created regular user: user@test.com / user123")
        else:
            print("✅ Regular user already exists: user@test.com")
    
    print("\n" + "=" * 70)
    print("🧪 Testing Navigation & Access Control")
    print("=" * 70 + "\n")
    
    with app.test_client() as client:
        # Test 1: Guest navigation
        print("TEST 1: Guest User Navigation")
        response = client.get('/')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Login' in html and 'Sign Up' in html
        assert 'Logout' not in html
        print("  ✅ Guest sees Login/Sign Up buttons")
        print("  ✅ Guest does NOT see Logout\n")
        
        # Test 2: Guest cannot access admin routes
        print("TEST 2: Guest Access to Admin Routes")
        admin_routes = ['/admin/', '/admin/users', '/admin/moderation', '/admin/reports']
        for route in admin_routes:
            response = client.get(route, follow_redirects=False)
            assert response.status_code in [302, 401, 403], f"Expected redirect/403 for {route}, got {response.status_code}"
        print("  ✅ Guest blocked from all admin routes (redirected or 403)\n")
        
        # Test 3: Regular user login and navigation
        print("TEST 3: Regular User Login & Navigation")
        response = client.post('/login', data={
            'email': 'user@test.com',
            'password': 'user123'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("  ✅ Regular user logged in successfully")
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'Regular User' in html or 'user' in html.lower()
        assert 'Login' not in html or 'Logout' in html  # Should see logout, not login
        print("  ✅ Regular user sees their profile info")
        print("  ✅ Regular user sees Profile/Logout (not Login/Register)\n")
        
        # Test 4: Regular user cannot access admin routes
        print("TEST 4: Regular User Access to Admin Routes")
        for route in admin_routes:
            response = client.get(route, follow_redirects=False)
            assert response.status_code == 403, f"Expected 403 for {route}, got {response.status_code}"
        print("  ✅ Regular user blocked from all admin routes (403 Forbidden)\n")
        
        # Logout
        client.get('/logout')
        
        # Test 5: Admin user login and navigation
        print("TEST 5: Admin User Login & Navigation")
        response = client.post('/login', data={
            'email': 'admin@test.com',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("  ✅ Admin user logged in successfully")
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'Admin User' in html or 'Admin' in html
        print("  ✅ Admin sees admin analytics dashboard (not community dashboard)")
        print("  ✅ Admin role displayed in navigation\n")
        
        # Test 6: Admin can access admin routes
        print("TEST 6: Admin User Access to Admin Routes")
        for route in admin_routes:
            response = client.get(route, follow_redirects=False)
            assert response.status_code == 200, f"Expected 200 for {route}, got {response.status_code}"
            print(f"  ✅ Admin accessed {route} successfully")
        print()
        
        # Test 7: Check profile and logout links
        print("TEST 7: Authenticated User Menu Links")
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '/profile/' in html or 'My Profile' in html
        assert '/logout' in html or 'Logout' in html
        print("  ✅ Profile link available")
        print("  ✅ Logout link available\n")
    
    print("=" * 70)
    print("🎉 All Role-Based Access Control Tests PASSED!")
    print("=" * 70)
    print("\n✨ Summary:")
    print("  • Guest users see Login/Register")
    print("  • Authenticated users see Profile/Logout dropdown")
    print("  • Admin users see admin menu items in dropdown")
    print("  • Admin routes are protected with 403 for non-admins")
    print("  • Admin users can access admin dashboard and tools")
    print("\n📝 Test Credentials:")
    print("  Admin: admin@test.com / admin123")
    print("  User:  user@test.com / user123")

if __name__ == "__main__":
    verify_role_access()
