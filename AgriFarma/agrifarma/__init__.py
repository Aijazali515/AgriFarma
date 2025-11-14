# -*- coding: utf-8 -*-
"""AgriFarma - Flask App Factory.

Ensures required runtime configuration defaults (like upload destinations)
are present so tests and development runs don't fail when optional settings
are omitted.
"""
from flask import Flask
import os
from .extensions import db, login_manager, csrf, media, migrate, mail


def create_app(config_object: str | object = "config.Config") -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_object)
    # Defaults
    app.config.setdefault('LOW_INVENTORY_THRESHOLD', 5)
    
    # Enable error propagation in debug mode (kept True for clearer traces)
    app.config['PROPAGATE_EXCEPTIONS'] = True

    # Init extensions
    register_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register CLI commands (development helpers)
    register_cli(app)

    # Create tables (dev bootstrap); in production prefer migrations
    with app.app_context():
        # Ensure all models are imported so SQLAlchemy is aware of FKs across modules
        try:
            from agrifarma.models import user as _user_models  # noqa: F401
            from agrifarma.models import profile as _profile_models  # noqa: F401
            from agrifarma.models import ecommerce as _ecommerce_models  # noqa: F401
            from agrifarma.models import blog as _blog_models  # noqa: F401
            from agrifarma.models import consultancy as _consultancy_models  # noqa: F401
            from agrifarma.models import password_reset as _password_reset_models  # noqa: F401
            from agrifarma.models import likes as _likes_models  # noqa: F401
            from agrifarma.models import forum as _forum_models  # noqa: F401
            from agrifarma.models import message as _message_models  # noqa: F401
        except Exception:
            # Best-effort import; blueprints may import models as well
            pass
        db.create_all()
    
    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Initialize Flask-Mail
    if mail:
        mail.init_app(app)
    
    if migrate:
        from agrifarma.models import user as _user_models  # noqa: F401
        from agrifarma.models import ecommerce as _ecommerce_models  # noqa: F401
        from agrifarma.models import blog as _blog_models  # noqa: F401
        from agrifarma.models import consultancy as _consultancy_models  # noqa: F401
        from agrifarma.models import password_reset as _password_reset_models  # noqa: F401
        from agrifarma.models import likes as _likes_models  # noqa: F401
        from agrifarma.models import message as _message_models  # noqa: F401
        migrate.init_app(app, db)

    # Provide a default upload destination if not set (e.g. in tests)
    if 'UPLOADED_MEDIA_DEST' not in app.config:
        # Use an uploads folder inside the application package for safety
        default_dest = os.path.join(app.root_path, 'uploads')
        os.makedirs(default_dest, exist_ok=True)
        app.config['UPLOADED_MEDIA_DEST'] = default_dest
    else:
        # Ensure the directory exists when provided via config/TestConfig
        os.makedirs(app.config['UPLOADED_MEDIA_DEST'], exist_ok=True)

    # Configure uploads
    try:
        from flask_uploads import configure_uploads
        configure_uploads(app, media)
    except Exception:
        # If flask_uploads not available, skip configuration (uploads disabled)
        app.logger.warning("flask_uploads not installed - media uploads disabled.")

    # Optional HTML/asset minification in development/production
    # Disabled in development to avoid conflicts
    # try:
    #     from flask_minify import Minify  # type: ignore
    #     Minify(app=app, html=True, js=True, cssless=True)
    # except Exception:
    #     pass


def register_blueprints(app: Flask) -> None:
    # main/home routes
    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    # users, forum, knowledge, consultancy, marketplace, admin - placeholders
    # These can be added as we implement features.
    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    # forum blueprint
    try:
        from .routes.forum import bp as forum_bp
        app.register_blueprint(forum_bp)
    except Exception:
        # forum may not be ready in early development steps
        pass
    try:
        from .routes.blog import bp as blog_bp
        app.register_blueprint(blog_bp)
    except Exception:
        pass
    # consultancy blueprint
    try:
        from .routes.consultancy import bp as consultancy_bp
        app.register_blueprint(consultancy_bp)
    except Exception:
        pass

    # ecommerce (shop) blueprint
    try:
        from .routes.ecommerce import bp as shop_bp
        app.register_blueprint(shop_bp)
    except Exception:
        pass
    # admin blueprint
    try:
        from .routes.admin import bp as admin_bp
        app.register_blueprint(admin_bp)
    except Exception:
        pass
    # media blueprint
    try:
        from .routes.media import bp as media_bp
        app.register_blueprint(media_bp)
    except Exception:
        pass
    # search blueprint
    try:
        from .routes.search import bp as search_bp
        app.register_blueprint(search_bp)
    except Exception:
        pass
    # API blueprint
    try:
        from .routes.api import bp as api_bp
        app.register_blueprint(api_bp)
    except Exception:
        pass
    return None


def register_cli(app: Flask) -> None:
    """Attach custom Flask CLI commands for development utilities (e.g. seeding)."""
    from agrifarma.seed_data import seed_all, clear_all  # local import to avoid circular
    import click

    @app.cli.command("seed")
    @click.option("--fresh", is_flag=True, help="Clear all existing data before seeding")
    def seed_command(fresh: bool) -> None:
        """Populate the database with a realistic development dataset."""
        if fresh:
            clear_all()
        seed_all()
        click.echo("✅ Seed complete.")

    @app.cli.command("clear")
    def clear_command() -> None:
        """Remove all rows from major tables (development only)."""
        clear_all()
        click.echo("🧹 Database cleared.")

    @app.cli.command("counts")
    def counts_command() -> None:
        """Print quick entity counts to verify seed volume."""
        from agrifarma.models.user import User
        from agrifarma.models.profile import Profile
        from agrifarma.models.consultancy import Consultant
        from agrifarma.models.ecommerce import Product, Review, Order
        from agrifarma.models.forum import Thread, Post
        from agrifarma.models.blog import BlogPost, Comment
        totals = {
            "users": User.query.count(),
            "profiles": Profile.query.count(),
            "consultants": Consultant.query.count(),
            "products": Product.query.count(),
            "reviews": Review.query.count(),
            "orders": Order.query.count(),
            "threads": Thread.query.count(),
            "posts": Post.query.count(),
            "blog_posts": BlogPost.query.count(),
            "comments": Comment.query.count(),
        }
        for k, v in totals.items():
            click.echo(f"{k}: {v}")
