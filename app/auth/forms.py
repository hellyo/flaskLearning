from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User



class LoginForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
	password = PasswordField('Password',validators=[DataRequired()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
	username=StringField('Username',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-za-z0-9_.]*$',0,'Username must have only letters,numbers,dots or undersores')]	)
	password = PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='Password must match')])	
	password2 = PasswordField('Confirm Password',validators=[DataRequired()])
	submit = SubmitField('Register')


	def validate_email(self,field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('Email already registered')

	def validate_username(self,field):
		if User.query.filter_by(username = field.data).first():
			raise ValidationError('username has already in use')

class ChangePasswordForm(FlaskForm):
	oldPassword=PasswordField('Old Password',validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='Password must match')])	
	password2 = PasswordField('Confirm Password',validators=[DataRequired()])
	submit=SubmitField('Confirm')


class PasswordResetRequestForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
	submit = SubmitField('Reset Password')

class PasswordResetForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
	password = PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message="password must match")])
	password2 = PasswordField('Confirm Password',validators=[DataRequired()])
	submit = SubmitField('Reset Password')

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first() is None:
			raise ValidationError('Unknown email')

class ChangeEmailForm(FlaskForm):
	email = StringField('New Email',validators=[DataRequired(),Email(),Length(1,64)])
	password = PasswordField('password',validators=[DataRequired()])
	submit=SubmitField('change email')

	def validate_email(self,field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('Email already registered.')



    	
