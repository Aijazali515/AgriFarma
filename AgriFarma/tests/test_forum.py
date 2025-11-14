import pytest
from agrifarma.extensions import db
from agrifarma.models.forum import Category, Thread, Post
from agrifarma.models.user import User


def register_and_login(client, email='f1@example.com'):
    data = {
        'name': 'Forum User',
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123',
        'mobile': '',
        'city': '',
        'state': '',
        'country': '',
        'profession': 'farmer',
        'expertise_level': 'beginner',
    }
    client.post('/register', data=data, follow_redirects=True)


def test_thread_creation_and_reply(client, app):
    # create a category
    with app.app_context():
        c = Category(name='General')
        db.session.add(c)
        db.session.commit()
        cat_id = c.id

    register_and_login(client)

    # create thread
    res = client.post('/forum/new', data={'title': 'Hello Forum', 'category_id': cat_id, 'content': 'First post content'}, follow_redirects=True)
    assert b'Thread created' in res.data
    assert b'Hello Forum' in res.data

    # reply
    res2 = client.post('/forum/thread/1', data={'content': 'A reply'}, follow_redirects=True)
    assert b'Reply posted' in res2.data
    assert b'A reply' in res2.data


def test_search_posts(client, app):
    # create category and thread/post
    with app.app_context():
        c = Category(name='SearchCat')
        db.session.add(c)
        db.session.commit()
        user = User.query.first()
        if not user:
            from werkzeug.security import generate_password_hash
            user = User(email='u_search@example.com', password_hash=generate_password_hash('pw'), role='User')
            db.session.add(user)
            db.session.commit()
        t = Thread(title='Searchable Thread', category_id=c.id, author_id=user.id)
        db.session.add(t)
        db.session.flush()
        p = Post(thread_id=t.id, author_id=user.id, content='This contains UNIQUE_KEYWORD_123')
        db.session.add(p)
        db.session.commit()

    res = client.get('/forum/search?q=UNIQUE_KEYWORD_123')
    assert b'UNIQUE_KEYWORD_123' in res.data


def test_admin_moderation(client, app):
    # create admin user
    with app.app_context():
        from werkzeug.security import generate_password_hash
        admin = User(email='admin@example.com', password_hash=generate_password_hash('adminpass'), role='Admin')
        db.session.add(admin)
        db.session.commit()
        # create category and thread
        c = Category(name='ModCat')
        db.session.add(c)
        db.session.commit()
        t = Thread(title='To be deleted', category_id=c.id, author_id=admin.id)
        db.session.add(t)
        db.session.commit()
        tid = t.id

    # login as admin
    client.post('/login', data={'email': 'admin@example.com', 'password': 'adminpass'}, follow_redirects=True)

    # delete thread
    res = client.post(f'/forum/thread/{tid}/delete', follow_redirects=True)
    assert b'Thread deleted' in res.data