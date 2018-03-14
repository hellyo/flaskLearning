from . import api
from .authentication import auth
from ..models import Post
from flask import jsonify


@api.route('/posts/')
@auth.login_required
def get_posts():
    '''
    get all posts
    '''
    posts = Post.query.all()
    return jsonify({'posts':[post.to_json() for post in posts]})


@api.route('/post/<int:id>')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())