import re, os
from flask.globals import current_app
from flask_login.utils import login_user
from werkzeug.exceptions import abort 
from werkzeug.utils import secure_filename
from wtforms.widgets.core import CheckboxInput
from config import GeneralConfig


from app.dashboard import dashboard_blueprint as dash 

from flask_login import (
    login_required, 
    logout_user, 
    current_user
)

from flask import ( 
    request,
    redirect,
    url_for,
    render_template,
    flash,
    Markup,
    Response
)

from app.utils import validate_image
from .forms import ( 
    ChangePassword, 
    BlogForm, 
    AccountForm, 
    ImageForm
)

from app.models import Category, User, Post, Image

''''
route for all users include admin 

'''
@dash.route('/welcome')
@login_required
def dashboard_index():
    return render_template('dashboard/index.html')

@dash.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('main.index_page'))

@dash.route('/account', methods=['GET','POST'])
@login_required
def account_page():
    form = AccountForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user.email = form.email.data 
            current_user.full_name = form.name.data 
            current_user.username = form.username.data 
            current_user.save()
            flash('ok')
        else:
            flash(form.errors, category='error_forms')
    
    # set value type

    form.name.data = current_user.full_name
    form.username.data = current_user.username 
    form.email.data = current_user.email

    return render_template('dashboard/account.html', form=form)

@dash.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePassword()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_password = form.new_password.data 
            if current_user.check_password(new_password):
                flash('you entering an old password, enter a new password')
            else:
                current_user.set_password(new_password)
                current_user.save()
                flash('password changed!')
        else:
            flash(form.errors, category='error_forms')
        
    return render_template('dashboard/change-password.html', form=form)

@dash.route('/add-blog', methods=['POST','GET'])
@login_required
def add_blog():
    form = BlogForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            body_content = form.body_content.data
            thumbnail_name = form.thumbnail.data
            new_thumbnailname = secure_filename(thumbnail_name.filename)
            title = form.title.data 

            thumbnail_name.save(os.path.join(GeneralConfig.DIR_UPLOADS, new_thumbnailname))
            
            p = Post(title=title, content=body_content, image_name=new_thumbnailname)
            p.author = current_user
            p.save()
            
            category_id = request.form['category_post']

            c = Category.query.filter_by(id=category_id).first()
            c.postingan.append(p)
            c.save()

            flash('blog added')

        else:
            flash(form.errors, category='error_forms')
    return render_template('dashboard/add-blog.html', 
                            form=form, 
                            categories=enumerate(Category.query.all()))

@dash.route('/add-images', methods=['POST','GET'])
@login_required
def add_images():
    form = ImageForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            list_images = form.imgs.data 
            list_uploaded = []
            for images in list_images:
                # validate images extensions and secure file name
                if validate_image(images):
                    new_filename = secure_filename(images.filename)
                    list_uploaded.append(new_filename)
                    images.save(os.path.join(GeneralConfig.DIR_UPLOADS,new_filename))

                    # add image to db
                    i = Image(image_name=new_filename)

                    i.image_author = current_user
                    i.save()
                    
                    list_uploaded.append(new_filename)

            uploaded = Markup('<br>uploaded '.join(list_uploaded))
            flash(uploaded)
            list_uploaded.clear()
        else:
            flash(form.errors, category='error_forms')

    return render_template('dashboard/add-images.html', form=form)

@dash.route('/blog', methods=['GET','POST'])
@login_required
def blog():
    if request.method == 'POST':
        selected_posts = request.form.getlist('checked[]')
        if len(request.form['opt']) < 4 and len(selected_posts) != 0:
            for posts_id in selected_posts:
                check_exist = Post.query.filter_by(id=posts_id).first()
                if check_exist and current_user.is_admin\
                    or check_exist.author.username == current_user.username:
                    if request.form['opt'] == '1':
                        check_exist.delete()
                        flash('{} deleted'.format(posts_id))
                else:
                    flash('oops.. somethings wrong ')
        else:
            flash('select blogs and option please')

    # if is admin, show all posts by users
    if not current_user.is_admin:
        posts = Post.query.filter_by(user_id=current_user.id).all()
    else:
        posts = Post.query.all()
    return render_template('dashboard/blog.html', posts=posts)

@dash.route('/edit-blog/<int:blog_id>', methods=['GET','POST'])
@login_required
def edit_blog(blog_id):
    check = Post.query.filter_by(id=blog_id).first()
    if check and current_user.is_admin\
        or check.author.username == current_user.username:
        form = BlogForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                thumbnail_image = form.thumbnail.data 
                if validate_image(thumbnail_image):
                    check.title = form.title.data 
                    check.content = form.body_content.data 
                    new_filename = secure_filename(thumbnail_image.filename)
                    form.thumbnail.data.save(os.path.join(GeneralConfig.DIR_UPLOADS, new_filename))

                    check.image_name = new_filename

                    if len(check.post_cat) != 0:
                        print('deleting category before ..')
                        check.post_cat = []

                    if check.image_name != new_filename:
                        file_before = os.path.join(GeneralConfig.DIR_UPLOADS, check.image_name)
                        if os.path.exists(file_before):
                            os.remove(file_before)
                    check.save()

                    cat_id = request.form['category_post']
                    c = Category.query.filter_by(id=cat_id).first()
                    c.postingan.append(check)
                    c.save()
                    flash('edited')
                
                else:
                    flash('invalid image')
            
            else:
                flash(form.errors, category='error_forms')
        
        form.title.data = check.title 
        form.body_content.data = check.content

        return render_template('dashboard/add-blog.html', form=form, categories=enumerate(Category.query.all()))
    else:
        flash('blog not found?!')
        return render_template('dashboard/blog.html')

@dash.route('/delete-blog/<int:blog_id>')
@login_required
def delete_blog(blog_id):
    check = Post.query.filter_by(id=blog_id).first()
    if check and current_user.is_admin\
        or current_user.username == check.author.username:
        check.delete()
        flash('deleted')
    else:
        flash('oopss.. something wrong?')
    return redirect(url_for('dashboard.blog'))

@dash.route('/delete-image/<int:image_id>')
@login_required
def delete_image(image_id):
    check = Image.query.filter_by(id=image_id).first()
    if check:
        if current_user.id == check.user_id\
            or current_user.is_admin:
            check.delete()
            flash('deleted')
    return redirect(url_for('dashboard.show_images'))

@dash.route('/images', methods=['GET','POST'])
@login_required
def show_images():
    if request.method == 'POST':
        lists_images = request.form.getlist('checkimage[]')
        if len(lists_images) != 0 and request.form['opt_img'] == '1':
            for image_id in lists_images:
                check_image = Image.query.filter_by(id=image_id).first()
                if check_image and check_image.user_id == current_user.id\
                    or current_user.is_admin:
                    check_image.delete()
                    flash(Markup('<br>deleted {}'.format(image_id)))
                else:
                    flash('something went wrong')
        else:
            flash('something went wrong')
    if current_user.is_admin:
        image = Image.query.all()
    else:
        image = Image.query.filter_by(user_id=current_user.id)
    return render_template('dashboard/images.html', image=enumerate(image))

@dash.route('/img-ckeditor')
@login_required
def img_ckeditor():
    if current_user.is_admin:
        images = Image.query.all()
    else:
        images = Image.query.filter_by(user_id=current_user.id)
    return render_template('dashboard/list-images.html', images=enumerate(images))