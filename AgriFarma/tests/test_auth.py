from agrifarma.extensions import db
from agrifarma.models.user import User

def register(client, **kwargs):
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "mobile": "",
        "city": "",
        "state": "",
        "country": "",
        "profession": "farmer",
        "expertise_level": "beginner",
    }
    data.update(kwargs)
    return client.post("/register", data=data, follow_redirects=True)

def login(client, email="test@example.com", password="password123"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

def test_registration_and_login_flow(client):
    res = register(client)
    assert res.status_code == 200
    assert b"Registration successful" in res.data

    # Logout then login
    client.get("/logout", follow_redirects=True)
    res = login(client)
    assert b"Logged in successfully" in res.data


def test_unique_email_enforced(client):
    res1 = register(client)
    assert b"Registration successful" in res1.data
    # Logout before attempting second registration with same email
    client.get("/logout", follow_redirects=True)
    res2 = register(client)
    assert b"Email already registered" in res2.data


def test_profile_permission(client):
    # Register user1
    register(client, email="u1@example.com")
    client.get("/logout", follow_redirects=True)

    # Register user2 and login
    register(client, email="u2@example.com")

    # user2 tries to edit profile (allowed for self)
    res = client.get("/profile/edit")
    assert res.status_code == 200

    # Create another user and try to edit via direct access (should still edit only own profile route)
    client.get("/logout", follow_redirects=True)
    register(client, email="u3@example.com")
    res = client.get("/profile/edit")
    assert res.status_code == 200
