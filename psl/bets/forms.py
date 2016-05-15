from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField, validators
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.html5 import EmailField, IntegerField
from flask_wtf.file import FileField, FileAllowed, FileRequired

class BetForm(Form):
	start_datetime = StringField("start_datetime", validators=[DataRequired()])

class BetSettingsForm(Form):

	betting_time = IntegerField(default=60, validators=[DataRequired(), NumberRange(min=0, max=60)])
	betting_time_unit = SelectField(default="minutes", choices=[('seconds', 'seconds'), ('minutes', 'minutes'), ('hours', 'hours')], validators=[DataRequired()])

	encoding_time = IntegerField(default=15, validators=[DataRequired(), NumberRange(min=0, max=60)])
	encoding_time_unit = SelectField(default="minutes", choices=[('seconds', 'seconds'), ('minutes', 'minutes'), ('hours', 'hours')], validators=[DataRequired()])