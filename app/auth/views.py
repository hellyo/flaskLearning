#coding=utf-8

from flask import render_template,redirect,request,url_for,flash
from flask_login import logout_user,login_user,login_required,current_user
from . import auth
from ..models import User
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,PasswordResetRequestForm,PasswordResetForm,ChangeEmailForm
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

@auth.before_app_request
def before_requset():
	if current_user.is_authenticated \
		and not current_user.confirmed \
		and request.endpoint[:5] != 'auth.'\
		and request.endpoint != 'static':
		return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')
   



@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirm_token()
	send_email(current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
	flash('A new confirmation email has been sent to your by email')
	return redirect(url_for('main.index'))

@auth.route('/changePassWd',methods=['GET','POST'])
@login_required
def changePassWd():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.checkIn(form.oldPassword.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('your password has been updated') #渲染在当前返回的页面中
			return redirect(url_for('main.index'))
		else:
			flash('old password is wrong') #验证失败的话，渲染当前表单页面
	return render_template('auth/changePassWd.html',form=form)

@auth.route('/reset',methods=['GET','POST'])
def resetpasswordRequest():
	#print current_user.username
	if not current_user.is_anonymous: #未注册用户或者游客
		return redirect(url_for('main.index'))
	form=PasswordResetRequestForm()
	if form.validate_on_submit(): #已经提交
		
		user=User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()			
			send_email(user.email,'Reset Your Password','auth/email/reset_password',user=user,token=token,next=request.args.get('next'))
		flash('a confirmation email has been sent to you email box')			
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['GET','POST'])
def passwordReset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token,form.password.data):
			flash('your password has been updated')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html',form=form)
		

@auth.route('/change-email',methods=['GET','POST'])
def change_email_request():
	form=ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.checkIn(form.password.data):
			new_email = form.email.data
			token=current_user.generate_change_mail_token(new_email)
			send_email(new_email,"confirm your email address",'auth/email/change_email',user=current_user,token=token)
			flash('an email has been sent to your NEW email address')
			return redirect(url_for('main.index'))
		else:
   			flash('Invalid email or password')
	return render_template('auth/change_email.html',form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash('your email address has been changed')
	else:
		flash('error')
	return redirect(url_for('main.index'))

			


			
