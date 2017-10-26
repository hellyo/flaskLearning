from flask import render_template,redirect,request,url_for,flash
from flask_login import logout_user,login_user,login_required,current_user
from . import auth
from ..models import User
from .forms import LoginForm,RegistrationForm
from .. import db
from ..email import send_email

@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.checkIn(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash("Invalid username or password")
	return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('you have been logged out')
	return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,username=form.username.data,password=form.password.data)
		db.session.add(user)		
		db.session.commit()
		token = user.generate_confirm_token()
		send_email(user.email,'Confirm You Account','auth/email/confirm',user=user,token=token)		
		flash("A confirmation email has been sent to you by email.")		
		return redirect(url_for('main.index'))
	return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('Your Account has been confirmed,Thanks')
	else:
		flash('please reConfirmed')
	return redirect(url_for('main.index'))
    		
