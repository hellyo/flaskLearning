from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash

from forms import EditProfileForm
from . import main
from .. import db
from ..models import User
from flask_login import login_required,current_user

@main.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html',name=session.get('name'),known=session.get('known',False))

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user in None:
        abort(404)
    return render_template('user.html',user=user)
    
@main.route('edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('your profile has ben updated')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

    
    



	
	
	
	