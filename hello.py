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
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "zcxmhylllll"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment= Moment(app)

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

if __name__ == "__main__":
	manager.run()

