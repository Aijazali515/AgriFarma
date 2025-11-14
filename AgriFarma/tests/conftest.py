import os
import sys
import pathlib
import pytest

# Ensure the inner project directory (where 'agrifarma' lives) is on sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agrifarma import create_app
from agrifarma.extensions import db

class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test"
    LOW_INVENTORY_THRESHOLD = 5
    # Prevent objects from expiring on commit so test fixtures can access attributes post-context
    SQLALCHEMY_SESSION_OPTIONS = {"expire_on_commit": False}

@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
