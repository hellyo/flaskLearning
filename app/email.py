from flask import render_template
from threading import Thread
from flask_mail import Message
from .. import mail


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