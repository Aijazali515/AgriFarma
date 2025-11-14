# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length
from agrifarma.models.blog import PREDEFINED_CATEGORIES

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=255)])
    category = SelectField('Category', choices=[(c, c) for c in PREDEFINED_CATEGORIES], validators=[DataRequired()])
    tags = StringField('Tags (comma separated)')
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10)])
    media_files = MultipleFileField('Attach Media (images/docs)')
    submit = SubmitField('Publish')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Post Comment')
