
from app.main import main_blueprint
from flask import render_template, jsonify
from app.models import Post, Category

@main_blueprint.route('/blog/<slug_uri>')
def show_blog(slug_uri):
    check = Post.query.filter_by(slug_uri=slug_uri).first()
    return render_template('blog-single.html')

@main_blueprint.route('/blog/category/<category_name>')
def show_blog_category(category_name):
    """
    show posts by category
    """
    return render_template('category.html')

@main_blueprint.route('/blog')
def blog():
    return render_template('blog.html')