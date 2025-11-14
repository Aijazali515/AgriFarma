# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from agrifarma.models.forum import Category


class NewThreadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=255)])
    # category_id matches route usage
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=3)])
    submit = SubmitField('Create Thread')

    def set_choices(self):
        cats = Category.query.order_by(Category.name).all()
        self.category_id.choices = [(c.id, c.name) for c in cats]


class ReplyForm(FlaskForm):
    content = TextAreaField('Reply', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Post Reply')


class MoveThreadForm(FlaskForm):
    category_id = SelectField('Move to', coerce=int)
    submit = SubmitField('Move')

    def set_choices(self):
        cats = Category.query.order_by(Category.name).all()
        self.category_id.choices = [(c.id, c.name) for c in cats]


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Search')
