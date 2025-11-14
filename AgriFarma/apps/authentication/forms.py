# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

# The WTForms Email validator raises an exception at instantiation time
# if the optional 'email_validator' package is not installed. Try to
# import and instantiate it; if that fails, provide a no-op fallback.
try:
    from wtforms.validators import Email as _Email
    try:
        # Try to create an instance to ensure dependencies are present
        _Email()
        Email = _Email
    except Exception:
        raise
except Exception:
    class Email:
        def __init__(self, *a, **k):
            pass

        def __call__(self, form, field):
            # Accept any value (skip validation)
            return True

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
