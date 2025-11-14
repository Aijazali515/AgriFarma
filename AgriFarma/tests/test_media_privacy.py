from werkzeug.security import generate_password_hash
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.blog import BlogPost
import os


def test_unapproved_media_access_control(client, app):
    # Create admin and login
    with app.app_context():
        admin = User(email='admin@blog.com', password_hash=generate_password_hash('adminpass'), role='Admin')
        db.session.add(admin)
        db.session.commit()
    client.post('/login', data={'email': 'admin@blog.com', 'password': 'adminpass'}, follow_redirects=True)

    # Determine upload destination
    upload_dest = None
    with app.app_context():
        upload_dest = app.config['UPLOADED_MEDIA_DEST']
    assert upload_dest and os.path.isdir(upload_dest)

    # Create a dummy file
    fname = 'test_priv.txt'
    fpath = os.path.join(upload_dest, fname)
    with open(fpath, 'w', encoding='utf-8') as fh:
        fh.write('secret content')

    # Create blog post referencing file, force unapproved state
    with app.app_context():
        post = BlogPost(title='Secret', content='x', category='Techniques', author_id=admin.id, tags='', media_files=fname, approved=False)
        db.session.add(post)
        db.session.commit()
        pid = post.id

    # Logout admin, register normal user and login
    client.get('/logout', follow_redirects=True)
    client.post('/register', data={
        'name': 'User', 'email': 'normal@example.com', 'password': 'pw12345', 'confirm_password': 'pw12345',
        'profession': 'farmer', 'expertise_level': 'beginner'
    }, follow_redirects=True)
    client.post('/login', data={'email': 'normal@example.com', 'password': 'pw12345'}, follow_redirects=True)

    # Normal user should receive 403
    res_forbidden = client.get(f'/media/{fname}')
    assert res_forbidden.status_code == 403, res_forbidden.status_code

    # Login admin again - should have access
    client.get('/logout', follow_redirects=True)
    client.post('/login', data={'email': 'admin@blog.com', 'password': 'adminpass'}, follow_redirects=True)
    res_allowed = client.get(f'/media/{fname}')
    assert res_allowed.status_code == 200

    # Toggle approval to True and normal user should then access
    with app.app_context():
        post = db.session.get(BlogPost, pid)
        post.approved = True
        db.session.commit()
    client.get('/logout', follow_redirects=True)
    client.post('/login', data={'email': 'normal@example.com', 'password': 'pw12345'}, follow_redirects=True)
    res_open = client.get(f'/media/{fname}')
    assert res_open.status_code == 200
