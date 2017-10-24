#!/usr/bin/python
#coding=utf-8

#from datetime import datetime

from flask import Flask, session, render_template, redirect, url_for, flash
#添加扩展
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail
from flask_mail import Message
from threading import Thread
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "zcxmhylllll"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

#mail configure [QQ 邮箱]
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT'] = '[Flasky Test]'
app.config['MAIL_SENDER'] = 'xxx<xxxxx@qq.com>'
app.config['FLASK_ADMIN'] = 'aaaaa@qq.com'  #os.environ.get('FLASK_ADMIN')



db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment= Moment(app)
mail = Mail(app)

migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)


class NameForm(FlaskForm):
    name = StringField("What's your name",validators=[Required()])
    submit = SubmitField("Submit")

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	users = db.relationship('User',backref='role',lazy = 'dynamic')
	def __repr__(self):
		return '<Role %r>' % self.name


class User(db.Model):
	__tablename__='users'
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(64),unique=True,index=True)
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	def __repr__(self):
		return '<User %r>' % self.username


@app.route('/',methods=['GET','POST'])
def index():	
	form = NameForm()
	if form.validate_on_submit():		    	
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user=User(username=form.name.data)    			
			db.session.add(user)
			session['known']=False
			if(app.config['FLASK_ADMIN']):
    				send_email(app.config['FLASK_ADMIN'],'New User','mail/new_user',user=user)
		else:
			session['known']=True
		session['name']=form.name.data
		form.name.data=''
		return redirect(url_for('index'))
	return render_template('index.html',form=form,name=session.get('name'),known=session.get('known',False))

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'),500

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
#manager.add_command("Shell",Shell(make_context=make_shell_context))
def send_async_mail(app, msg):
	with app.app_context():
		mail.send(msg)
def send_email(to,subject,template, **kwargs):
	msg = Message(app.config['MAIL_SUBJECT']+subject,sender=app.config['MAIL_SENDER'],recipients=[to])
	msg.body=render_template(template+".txt",**kwargs)
	msg.html=render_template(template+'.html',**kwargs)
	thr=Thread(target=send_async_mail,args=[app,msg])
	thr.start()
	return thr
    	

if __name__ == "__main__":
	manager.run()

