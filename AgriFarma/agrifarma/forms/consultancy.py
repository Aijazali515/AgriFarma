# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email
from agrifarma.models.consultancy import CONSULTANT_CATEGORIES
from agrifarma.models.profile import EXPERTISE_LEVELS

class ConsultantRegisterForm(FlaskForm):
    category = SelectField("Category", choices=[(c, c.replace('_',' ').title()) for c in CONSULTANT_CATEGORIES], validators=[DataRequired()])
    expertise_level = SelectField("Expertise Level", choices=[(e, e.title()) for e in EXPERTISE_LEVELS], validators=[DataRequired()])
    contact_email = StringField("Contact Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Apply as Consultant")
