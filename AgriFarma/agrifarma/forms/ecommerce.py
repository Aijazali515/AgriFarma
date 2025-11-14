# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Email
from agrifarma.models.ecommerce import PRODUCT_STATUSES, ORDER_STATUSES

CATEGORIES = ["seeds","fertilizers","equipment","bio","other"]
PAYMENT_METHODS = ["COD","card","wallet"]

class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description")
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2)
    category = SelectField("Category", choices=[(c, c.title()) for c in CATEGORIES], validators=[DataRequired()])
    images = StringField("Images (comma-separated)")
    inventory = IntegerField("Inventory", default=0, validators=[NumberRange(min=0)])
    status = SelectField("Status", choices=[(s, s) for s in PRODUCT_STATUSES])
    featured = SelectField("Featured", choices=[("false","No"),("true","Yes")], validators=[DataRequired()])
    submit = SubmitField("Save Product")

class AddToCartForm(FlaskForm):
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1, max=100)], default=1)
    submit = SubmitField("Add to Cart")

class UpdateCartItemForm(FlaskForm):
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=0, max=100)], default=1)
    submit = SubmitField("Update")

class CheckoutForm(FlaskForm):
    shipping_address = StringField("Shipping Address", validators=[DataRequired(), Length(max=256)])
    payment_method = SelectField("Payment Method", choices=[(m, m) for m in PAYMENT_METHODS], validators=[DataRequired()])
    submit = SubmitField("Place Order")

class ReviewForm(FlaskForm):
    rating = IntegerField("Rating (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField("Comment", validators=[Length(max=2000)])
    submit = SubmitField("Submit Review")
