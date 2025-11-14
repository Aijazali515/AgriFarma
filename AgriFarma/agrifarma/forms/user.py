# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from agrifarma.models.profile import PROFESSIONS, EXPERTISE_LEVELS

try:  # Provide a fallback if email_validator isn't installed in some environments
    import email_validator  # noqa: F401
    from wtforms.validators import Email as WTEmail  # type: ignore
    EMAIL_VALIDATOR = WTEmail()
except Exception:
    class _NoopEmail:
        def __call__(self, form, field):
            return True
    EMAIL_VALIDATOR = _NoopEmail()


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), EMAIL_VALIDATOR])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    mobile = StringField("Mobile", validators=[Length(max=20)])
    city = StringField("City", validators=[Length(max=64)])
    state = StringField("State", validators=[Length(max=64)])
    country = StringField("Country", validators=[Length(max=64)])
    profession = SelectField("Profession", choices=[(p, p.title()) for p in PROFESSIONS])
    expertise_level = SelectField("Expertise", choices=[(e, e.title()) for e in EXPERTISE_LEVELS])
    submit = SubmitField("Create Account")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), EMAIL_VALIDATOR])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class EditProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    mobile = StringField("Mobile", validators=[Length(max=20)])
    city = StringField("City", validators=[Length(max=64)])
    state = StringField("State", validators=[Length(max=64)])
    country = StringField("Country", validators=[Length(max=64)])
    profession = SelectField("Profession", choices=[(p, p.title()) for p in PROFESSIONS])
    expertise_level = SelectField("Expertise", choices=[(e, e.title()) for e in EXPERTISE_LEVELS])
    display_picture = FileField("Profile Picture", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only (JPG, PNG, GIF)')])
    submit = SubmitField("Save Changes")

class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), EMAIL_VALIDATOR])
    submit = SubmitField("Send Reset Link")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")
