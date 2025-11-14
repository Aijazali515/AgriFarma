from werkzeug.security import generate_password_hash
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.consultancy import Consultant, CONSULTANT_CATEGORIES


def register_user(client, email='user@example.com'):
    # ensure a clean session for creating a distinct user
    client.get('/logout', follow_redirects=True)
    data = {
        'name': 'User',
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123',
        'profession': 'farmer',
        'expertise_level': 'beginner'
    }
    client.post('/register', data=data, follow_redirects=True)


def test_consultant_registration_flow(client, app):
    register_user(client, email='consultant@example.com')
    res = client.post('/consultant/register', data={
        'category': 'soil',
        'expertise_level': 'expert',
        'contact_email': 'consultant@example.com'
    }, follow_redirects=True)
    assert b'Application submitted' in res.data
    with app.app_context():
        c = Consultant.query.first()
        assert c is not None
        assert c.approval_status == 'Pending'


def test_admin_approval_workflow(client, app):
    # Seed an admin
    with app.app_context():
        admin = User(email='admin@example.com', password_hash=generate_password_hash('adminpass'), role='Admin')
        db.session.add(admin)
        db.session.commit()

    # normal user applies
    register_user(client, email='applier@example.com')
    client.post('/consultant/register', data={
        'category': 'irrigation',
        'expertise_level': 'intermediate',
        'contact_email': 'applier@example.com'
    }, follow_redirects=True)

    # admin approves
    client.post('/login', data={'email': 'admin@example.com', 'password': 'adminpass'}, follow_redirects=True)
    with app.app_context():
        pending = Consultant.query.filter_by(approval_status='Pending').first()
        assert pending is not None
        cid = pending.id
    res = client.post('/admin/consultants', data={'consultant_id': cid, 'action': 'approve'}, follow_redirects=True)
    assert b'Consultant status updated' in res.data
    with app.app_context():
        approved = db.session.get(Consultant, cid)
        assert approved.approval_status == 'Approved'


def test_public_listing_by_category(client, app):
    # create two consultants with different categories
    register_user(client, email='c1@example.com')
    res1 = client.post('/consultant/register', data={
        'category': 'soil',
        'expertise_level': 'expert',
        'contact_email': 'c1@example.com'
    }, follow_redirects=True)
    assert b'Application submitted' in res1.data

    register_user(client, email='c2@example.com')
    res2 = client.post('/consultant/register', data={
        'category': 'crop_disease',
        'expertise_level': 'beginner',
        'contact_email': 'c2@example.com'
    }, follow_redirects=True)
    assert b'Application submitted' in res2.data

    # Approve all
    with app.app_context():
        all_cons = Consultant.query.all()
        assert len(all_cons) == 2
        for c in all_cons:
            c.approval_status = 'Approved'
        db.session.commit()
        # sanity check
        assert Consultant.query.filter_by(approval_status='Approved').count() == 2

    # Filter list
    res_all = client.get('/consultants')
    assert b'mailto:c1@example.com' in res_all.data and b'mailto:c2@example.com' in res_all.data

    res_soil = client.get('/consultants?category=soil')
    assert b'mailto:c1@example.com' in res_soil.data and b'mailto:c2@example.com' not in res_soil.data


def test_consultant_pagination_boundaries(client, app):
    # Create many approved consultants
    from agrifarma.models.consultancy import Consultant
    from agrifarma.models.user import User
    from werkzeug.security import generate_password_hash
    from datetime import datetime, UTC, timedelta
    with app.app_context():
        # seed users and consultants
        base_time = datetime.now(UTC) - timedelta(days=1)
        for i in range(1, 31):  # > 2 pages (per_page=12)
            email = f"cons{i:02d}@example.com"
            u = User(email=email, password_hash=generate_password_hash('pw'), role='User')
            db.session.add(u)
            db.session.flush()
            c = Consultant(user_id=u.id, category='soil', expertise_level='expert', contact_email=email, approval_status='Approved')
            c.created_at = base_time
            base_time = base_time + timedelta(minutes=1)
            db.session.add(c)
        db.session.commit()

    # Page 1 should include cons01 and not cons25
    r1 = client.get('/consultants?page=1&category=soil')
    assert b'cons01@example.com' in r1.data and b'cons25@example.com' not in r1.data
    # Page 2 should include cons13 (since ordering desc by created_at, later times are later additions) - verify separation
    r2 = client.get('/consultants?page=2&category=soil')
    assert b'cons13@example.com' in r2.data
    # High page beyond range should fallback to empty list (no consultants found message)
    r99 = client.get('/consultants?page=99&category=soil')
    assert b'No consultants found' in r99.data
