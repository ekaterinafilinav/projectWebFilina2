from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class AddDepartForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    who_paid = IntegerField('Chief ID', validators=[DataRequired()])
    pay_size = IntegerField('Members', validators=[DataRequired()])
    category = StringField('category', validators=[DataRequired()])
    submit = SubmitField('Submit')
