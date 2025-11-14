# WSGI entrypoint for production servers (e.g., gunicorn, uWSGI)
from agrifarma import create_app

# Use DevelopmentConfig by default; override via env if needed
application = create_app("config.DevelopmentConfig")

# For local testing with `python wsgi.py`
if __name__ == "__main__":
    application.run()
