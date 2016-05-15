from flask_wtf import Form
from flask.ext.uploads import UploadSet, IMAGES
from wtforms import StringField, BooleanField, PasswordField, validators
from wtforms.validators import DataRequired
from flask_wtf.html5 import EmailField, IntegerField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_security.forms import RegisterForm, ConfirmRegisterForm

class ForgotPasswordForm(Form):
	email = StringField('email', validators=[DataRequired()])

class RegisterForm(Form):
  email = StringField('email', validators=[DataRequired()])

class LoginForm(Form):
  username = StringField('username', validators=[DataRequired()])
  password = StringField('password', validators=[DataRequired()])

images = UploadSet('images', IMAGES)

class PhotoForm(Form):
    upload = FileField('image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])

class ChangePasswordForm(Form):
  password = PasswordField('Current Password', [
      validators.Required()
  ])
  new_password = PasswordField('New Password', [
      validators.Required(),
      validators.EqualTo('new_password_confirm', message='Passwords must match')
  ])
  new_password_confirm = PasswordField('Confirm New Password')

class ExtendedRegisterForm(RegisterForm):
    username = StringField('Username')
    password = StringField('password', validators=[DataRequired()])

class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    username = StringField('Username')
    password = StringField('password', validators=[DataRequired()])

