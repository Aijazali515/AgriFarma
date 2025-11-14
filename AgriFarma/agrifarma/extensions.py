# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
try:
    from flask_migrate import Migrate  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Migrate = None
try:
	from flask_uploads import UploadSet, IMAGES, DOCUMENTS, configure_uploads  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	UploadSet = None
	IMAGES = tuple()
	DOCUMENTS = tuple()
	configure_uploads = None
try:
	from flask_mail import Mail  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	Mail = None

# Flask extensions singletons

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
if Migrate:
	migrate = Migrate()
else:
	migrate = None

if Mail:
	mail = Mail()
else:
	mail = None

# Uploads (images, docs, plus some extra extensions like videos)
media = UploadSet('media', IMAGES + DOCUMENTS) if UploadSet else None

# Login settings
login_manager.login_view = "main.index"
login_manager.login_message_category = "info"
