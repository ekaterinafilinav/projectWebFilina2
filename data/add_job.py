from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    whose_salary = IntegerField('whose salary id', validators=[DataRequired()])
    work_size = StringField('salary amount', validators=[DataRequired()])
    # collaborators = StringField('Collaborators', validators=[DataRequired()])
    # is_finished = BooleanField('Is job finished?')

    submit = SubmitField('Submit')
