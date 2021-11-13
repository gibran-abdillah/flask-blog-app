
from flask.templating import render_template
from sqlalchemy.sql.expression import desc
from app.api import api_blueprint
from app.models import Category, User, Post, PaginateGenerator
from flask import abort, jsonify, request, url_for
from app.utils.mail import Message
from app.utils.decorators import validate_image
from app import mail

@api_blueprint.route('/')
def index_api():
    return 'Hello World'

@api_blueprint.route('/user/<string:username>/posts')
def username_get_posts(username):
    result = User.query.filter_by(username=username).first()
    if result:
        posts_user = result.user_post.all()
        if len(posts_user) != 0:
            return jsonify(status=False, 
                           data=[x.to_dict() for x in posts_user])

    return jsonify({'status':False, 'data':'username not found'})

@api_blueprint.route('/user/<string:username>')
def api_username(username: str):
    result = User.query.filter_by(username=username).first()
    if result:
        return jsonify(status=True, data=result.to_dict())
    return jsonify({'status':False, 'data':'username not found'})

@api_blueprint.route('/recent-blogs')
def get_recent_blogs():
    result = Post.query.order_by(desc(Post.created_at)).limit(6)
    if result:
        return jsonify(status='success', 
                       data=[results.to_dict() 
                            for results in result])

    return jsonify(status='error', data='no result')

@api_blueprint.route('/blog/<slug>')
def fetch_blog(slug):
    result = Post.query.filter_by(slug_uri=slug).first()
    if result:
        return jsonify(status='success', data=result.to_show())
    return jsonify(status='fail', data='invalid id'), 404

@api_blueprint.route('/blogs')
def get_blogs():
    result = Post.query.all()
    if result:
        return jsonify(status='success', data=[results.to_dict() for results in result])
    return jsonify(status='error', data='no result')

@api_blueprint.route('/blogs/page/<int:page>')
def show_blog(page):
    prev_id = request.args.get('prev_id', None)
    category = request.args.get('category', None)
    if not prev_id and page > 1:
        return jsonify(status='fail', data='previous id is required when page > 1')
    if page == 1:
        prev_id = 0 
    return jsonify(PaginateGenerator(Post, page, previous_id=prev_id, category=category).generate())

@api_blueprint.route('/users')
def get_users():
    result = User.query.all()
    if result:
        return jsonify(status='success', 
                       data=[results.to_dict() 
                             for results in result])

    return jsonify(status='error', data='no result')

@api_blueprint.route('/users/page/<int:page>')
def show_users(page):
    prev_id = request.args.get('prev_id', None)
    if not prev_id and page > 1:
        return jsonify(status='fail', data='previous id is required when page > 1')
    if page == 1:
        prev_id = 0 
    return jsonify(PaginateGenerator(User, page, previous_id=prev_id).generate())

@api_blueprint.route('/categories')
def get_categories():
    result = Category.query.all()
    if result:
        return jsonify(status='success', data=[results.to_dict() for results in result])
    return jsonify(status='fail', data='categories not found')

@api_blueprint.route('/reset-password', methods=['POST','GET'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email',None)
        if not email:
            return jsonify(status='fail', data='missing email params')
        check = User.query.filter_by(email=email).first()
        if check:
            new_token = check.get_reset_token()
            body_mail = render_template('auth/reset-template.html', token=new_token)
            #print(body_mail)
            m = Message(to=email, subject='RESET PASSWORD', body=body_mail)
            mail.send_msg(m)
        return jsonify(status='success', data='ssshhh, its secret! check your email!')
    return jsonify(status='error', data='method not allowed')

