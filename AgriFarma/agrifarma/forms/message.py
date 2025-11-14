from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class MessageForm(FlaskForm):
    """Form for sending messages to consultants"""
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(min=3, max=200, message='Subject must be between 3 and 200 characters')
    ])
    content = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=10, message='Message must be at least 10 characters')
    ])
    submit = SubmitField('Send Message')
