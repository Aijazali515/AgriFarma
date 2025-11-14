from datetime import UTC, datetime
from werkzeug.security import generate_password_hash
from io import BytesIO
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.blog import BlogPost

def create_user(app, email="uploader@example.com"):
    with app.app_context():
        u = User(email=email, password_hash=generate_password_hash("pass"), role="User")
        db.session.add(u)
        db.session.commit()
        return u.id

def login(client, email, password="pass"):
    client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

def test_blog_media_upload_persistence(client, app):
    uid = create_user(app)
    login(client, 'uploader@example.com')
    data = {
        'title': 'Media Test',
        'category': 'Techniques',
        'tags': 'test,upload',
        'content': 'Body with media',
    }
    file1 = (BytesIO(b'fake image bytes'), 'image1.png')
    file2 = (BytesIO(b'fake doc bytes'), 'doc1.pdf')
    res = client.post('/blog/new', data={**data, 'media_files': [file1, file2]}, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        post = BlogPost.query.filter_by(title='Media Test').first()
        assert post is not None
        assert 'image1' in post.media_files and 'doc1' in post.media_files

def test_permission_denial_blog_approve(client, app):
    # Non-admin tries to approve a post
    uid = create_user(app)
    login(client, 'uploader@example.com')
    # Create a post (auto-approved because non-admin logic sets approved True)
    client.post('/blog/new', data={'title':'Post Title','category':'Techniques','tags':'','content':'Valid content body for approval test'}, follow_redirects=True)
    with app.app_context():
        post = BlogPost.query.filter_by(title='Post Title').first()
        post.approved = False
        db.session.commit()
        pid = post.id
    # Attempt approve without admin role -> 403
    res = client.post(f'/blog/admin/post/{pid}/approve', follow_redirects=False)
    assert res.status_code == 403

def test_permission_denial_shop_admin_page(client, app):
    # Non-admin access to shop admin dashboard
    uid = create_user(app, email='buyer@example.com')
    login(client, 'buyer@example.com')
    res = client.get('/admin/shop')
    assert res.status_code == 403
