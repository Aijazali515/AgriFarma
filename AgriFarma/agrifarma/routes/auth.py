# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from agrifarma.extensions import db, login_manager
from agrifarma.models.user import User
from agrifarma.models.profile import Profile
from agrifarma.models.password_reset import PasswordResetToken
from agrifarma.forms.user import RegisterForm, LoginForm, EditProfileForm, ForgotPasswordForm, ResetPasswordForm
from agrifarma.services import email as email_service

bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    # Use SQLAlchemy 2.x Session.get instead of legacy Query.get
    try:
        return db.session.get(User, int(user_id))
    except Exception:  # pragma: no cover
        return None


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.profile_view", id=current_user.id))

    form = RegisterForm()
    if form.validate_on_submit():
        # Enforce unique email
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email already registered.", "danger")
            return render_template("register.html", form=form)

        user = User(
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data),
            role="User",
        )
        db.session.add(user)
        db.session.flush()  # get user.id

        profile = Profile(
            user_id=user.id,
            name=form.name.data,
            mobile=form.mobile.data or None,
            city=form.city.data or None,
            state=form.state.data or None,
            country=form.country.data or None,
            profession=form.profession.data or None,
            expertise_level=form.expertise_level.data or None,
        )
        db.session.add(profile)
        db.session.commit()

        login_user(user)
        flash("Registration successful. Welcome to AgriFarma!", "success")
        return redirect(url_for("auth.profile_view", id=user.id))

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"]) 
def login():
    # If already authenticated, keep UX-friendly redirect on GET,
    # but allow POST to switch accounts (useful for admin switching in tests).
    if current_user.is_authenticated and request.method == "GET":
        return redirect(url_for("auth.profile_view", id=current_user.id))

    form = LoginForm()
    if form.validate_on_submit():
        # If a user is already logged in, permit switching accounts
        # by logging out first.
        if current_user.is_authenticated:
            logout_user()
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash("Account is inactive.", "warning")
                return render_template("login.html", form=form)
            login_user(user)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("auth.profile_view", id=user.id))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/profile/<int:id>")
@login_required
def profile_view(id: int):
    user = db.session.get(User, id)
    if not user:
        abort(404)
    # Permissions: allow viewing profiles; editing restricted separately
    return render_template("profile_view.html", user=user, profile=user.profile)


@bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    # Only owner or admin can edit
    user = current_user
    if not (user.id == current_user.id or current_user.role == "Admin"):
        abort(403)

    form = EditProfileForm(obj=user.profile)
    if form.validate_on_submit():
        p = user.profile
        p.name = form.name.data
        p.mobile = form.mobile.data or None
        p.city = form.city.data or None
        p.state = form.state.data or None
        p.country = form.country.data or None
        p.profession = form.profession.data or None
        p.expertise_level = form.expertise_level.data or None
        
        # Handle display picture upload
        if form.display_picture.data:
            file = form.display_picture.data
            if file.filename:
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join('agrifarma', 'static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename: userid_timestamp.extension
                ext = os.path.splitext(secure_filename(file.filename))[1]
                unique_filename = f"user_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                filepath = os.path.join(upload_dir, unique_filename)
                
                # Delete old display picture if exists
                if p.display_picture:
                    old_file = os.path.join(upload_dir, p.display_picture)
                    if os.path.exists(old_file):
                        try:
                            os.remove(old_file)
                        except Exception:
                            pass  # Ignore deletion errors
                
                # Save new file
                file.save(filepath)
                p.display_picture = unique_filename
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("auth.profile_view", id=user.id))

    return render_template("edit_profile.html", form=form)


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Create reset token
            token = PasswordResetToken.create_token(user.id)
            # Send email with proper template
            reset_url = url_for('auth.reset_password', token=token.token, _external=True)
            email_service.send_password_reset_email(
                user_email=user.email,
                reset_url=reset_url,
                user_name=user.profile.name if user.profile else None
            )
        # Always show success to avoid email enumeration
        flash("If that email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    
    return render_template("forgot_password.html", form=form)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    # Validate token
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    if not reset_token or not reset_token.is_valid():
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = reset_token.user
        user.password_hash = generate_password_hash(form.password.data)
        reset_token.mark_used()
        db.session.commit()
        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("reset_password.html", form=form, token=token)
