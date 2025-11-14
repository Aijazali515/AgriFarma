import re, json
from datetime import datetime, timedelta, UTC
from werkzeug.security import generate_password_hash
from agrifarma.extensions import db
from agrifarma.models.user import User

def seed_users(app, days_offsets):
    with app.app_context():
        for i, offset in enumerate(days_offsets):
            dt = datetime.now(UTC) - timedelta(days=offset)
            u = User(email=f"chart{i}@example.com", password_hash=generate_password_hash("pass"), role="User", join_date=dt)
            db.session.add(u)
        db.session.commit()

def login_admin(client, app):
    with app.app_context():
        admin = User(email="chartadmin@example.com", password_hash=generate_password_hash("adminpass"), role="Admin")
        db.session.add(admin)
        db.session.commit()
    client.post('/login', data={'email':'chartadmin@example.com','password':'adminpass'}, follow_redirects=True)


def test_registration_chart_data(client, app):
    login_admin(client, app)
    # Seed users: offsets create distinct days (0= today, 1= yesterday, 3 days ago twice)
    seed_users(app, [0, 0, 1, 3, 3])
    start = (datetime.now(UTC) - timedelta(days=5)).strftime('%Y-%m-%d')
    end = datetime.now(UTC).strftime('%Y-%m-%d')
    res = client.get(f"/admin/reports?start={start}&end={end}")
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    m = re.search(r'const regData = (\[.*?\]);', html, re.DOTALL)
    assert m, 'regData JSON not found in reports page'
    reg_json = json.loads(m.group(1))
    # Ensure sorted ascending by date
    dates = [row['date'] for row in reg_json]
    assert dates == sorted(dates), 'Dates not sorted in regData'
    # Build expected counts
    counts = {}
    for d in dates:
        counts[d] = 0
    # We inserted 2 today, 1 yesterday, 2 three-days ago
    base_now = datetime.now(UTC)
    today_str = base_now.date().isoformat()
    yest_str = (base_now - timedelta(days=1)).date().isoformat()
    three_str = (base_now - timedelta(days=3)).date().isoformat()
    expected = {three_str:2, yest_str:1, today_str:2}
    for row in reg_json:
        if row['date'] in expected:
            assert row['count'] == expected[row['date']], f"Count mismatch for {row['date']}"