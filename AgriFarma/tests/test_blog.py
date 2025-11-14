from werkzeug.security import generate_password_hash
from agrifarma.extensions import db
from agrifarma.models.blog import BlogPost, Comment
from agrifarma.models.user import User


def register_user(client, email='blogger@example.com'):
    data = {
        'name': 'Blogger',
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123',
        'profession': 'farmer',
        'expertise_level': 'beginner'
    }
    client.post('/register', data=data, follow_redirects=True)


def test_blog_creation_and_comment(client, app):
    register_user(client)
    res = client.post('/blog/new', data={
        'title': 'My First Blog',
        'category': 'Success Stories',
        'tags': 'success,first',
        'content': 'This is a success story',
    }, follow_redirects=True)
    assert b'Blog post published' in res.data
    # comment
    res2 = client.post('/blog/post/1', data={'content': 'Great story!'}, follow_redirects=True)
    assert b'Comment posted' in res2.data


def test_blog_search(client, app):
    register_user(client, email='searcher@example.com')
    client.post('/blog/new', data={
        'title': 'Rain Patterns',
        'category': 'Weather Tips',
        'tags': 'rain,weather',
        'content': 'Predicting rain patterns.'
    }, follow_redirects=True)
    res = client.get('/blog/?q=rain')
    assert b'Rain Patterns' in res.data


def test_blog_admin_moderation(client, app):
    # create admin directly
    with app.app_context():
        admin = User(email='kbadmin@example.com', password_hash=generate_password_hash('adminpass'), role='Admin')
        db.session.add(admin)
        db.session.commit()
    # login admin
    client.post('/login', data={'email': 'kbadmin@example.com', 'password': 'adminpass'}, follow_redirects=True)
    # create unapproved post by non-admin user
    register_user(client, email='author2@example.com')
    client.post('/blog/new', data={
        'title': 'Moderate Me',
        'category': 'Techniques',
        'tags': 'mod',
        'content': 'Needs approval maybe.'
    }, follow_redirects=True)
    # fetch the created post id dynamically (avoid hard-coded assumption)
    with app.app_context():
        post = BlogPost.query.filter_by(title='Moderate Me').first()
        assert post is not None, 'Expected blog post to exist.'
        target_id = post.id
    # delete it via admin endpoint
    res = client.post(f'/blog/admin/post/{target_id}/delete', follow_redirects=True)
    assert b'Post deleted' in res.data
