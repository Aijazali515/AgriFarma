class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///agrifarma.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
