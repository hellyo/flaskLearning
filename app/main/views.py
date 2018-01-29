from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash,request,current_app,make_response

from .forms import EditProfileForm,EditProfileAdminForm,PostForm,CommentForm
from . import main
from .. import db
from ..models import User,Role,Permission,Post,Comment
from flask_login import login_required,current_user
from ..decorators import admin_required,permission_required

@main.route('/',methods=['GET','POST'])
def index():

    form = PostForm()
    
    if  current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    
    show_followed = False
    page = request.args.get('page',1,type=int)
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    error_out=False)
    try:
        posts = pagination.items
    except:
        posts = None
    print(pagination.total)
    return render_template('index.html',form=form,posts=posts,pagination=pagination,show_followed=show_followed)

#    return render_template('index.html',name=session.get('name'),known=session.get('known',False))

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page',1,type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page,per_page=10,error_out=False)
    posts=pagination.items
    #posts = user.posts.order_by(Post.timestamp.desc()).all()
    print(posts)
    return render_template('user.html',user=user,posts=posts,pagination=pagination)
    
@main.route('/edit-profile',methods=['GET','POST'])
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


@main.route('/edit-profile/<int:id>',methods = ['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('your profile has been updated')
        return redirect(url_for('.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user )

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,post=post,author=current_user._get_current_object())
        db.session.add(comment)
        flash('your comment has been commited!!')
        return redirect(url_for('.post',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = int((post.comments.count()-1) / current_app.config['FLASKY_POSTS_PER_PAGE']) + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page,current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    comments = pagination.items

    return render_template('post.html',posts = [post],form=form,comments=comments,pagination=pagination)

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('posts updated!!')
        return redirect(url_for('.post',id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('U have already following this user')
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    flash('you have successfully followed %s' % username)
    return redirect(url_for('.user',username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('U did not followe this user')
        return redirect(url_for('.user',username=username))
    current_user.unfollow(user)
    flash('you have successfully unfollowed %s' % username)
    return redirect(url_for('.user',username=username))


@main.route('/followers/<username>')
def followers(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type = int)
    print(user.followers.count())
    pagination = user.followers.paginate(page,per_page=20,error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items if not item.follower == user]
    return render_template('followers.html',user=user,title="Followers of "+username,endpoint='.followers',pagination=pagination,follows=follows)

@main.route('/followed-by/<username>')
def followed_by(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type = int)
    pagination = user.followed.paginate(page,per_page=20,error_out=False)
    follows = [{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items if not item.followed == user]
   
    return render_template('followers.html',user=user,title="Followed By "+username,endpoint='.followers',pagination=pagination,follows=follows)
    
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page,10,error_out=False)
    comments = pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment=Comment.query.get_or_404(id)
    comment.disabled = True

    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))