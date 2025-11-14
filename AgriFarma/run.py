# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from pathlib import Path
from sys import exit

# Optional integrations like Flask-Migrate/Minify removed for a lean default run.

from agrifarma import create_app
from agrifarma.extensions import db, migrate

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'True') == 'True')

class DefaultConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    # Use an absolute path to avoid accidentally using instance/ relative DBs
    _BASE_DIR = Path(__file__).resolve().parent
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{(_BASE_DIR / 'agrifarma.db').as_posix()}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    # Dev: force template/static refresh
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0

app = create_app(DefaultConfig)
if migrate:
    app.logger.info('Flask-Migrate enabled.')

# (Optional) Integrations such as Flask-Migrate or Flask-Minify
# can be re-enabled here if needed in production.
    
if DEBUG:
    app.logger.info('DEBUG = %s', str(DEBUG))

if __name__ == "__main__":
    app.run(debug=True)
