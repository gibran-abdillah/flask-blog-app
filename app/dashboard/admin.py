from flask.helpers import flash
from app.dashboard import dashboard_blueprint as dash 
from flask import ( 
    render_template, 
    redirect, 
    url_for, 
    Markup,
    request)

from app.utils import admin_required
from .forms import AccountForm, AddAccount
from app.models import User, Category, db 

"""
page only just for admin role
"""

@dash.route('/add-user', methods=['GET','POST'])
@admin_required
def add_user():
    form = AddAccount()
    if request.method == 'POST':
        if form.validate_on_submit():

            name = form.name.data 
            email = form.email.data 
            pwd = form.password.data 
            username = form.username.data 
            adm = form.admin.data

            u = User(username=username, 
                     email=email, 
                     full_name=name,
                     is_admin=adm)
            
            u.set_password(pwd)
            u.save()
            flash('Account Added!')

        else:
            flash(form.errors, category='error_forms')

    return render_template('dashboard/add-account.html', form=form)

@dash.route('/users', methods=['GET','POST'])
@admin_required
def show_users():
    if request.method == 'POST':
        checkbox_list = request.form.getlist('checkbox[]')
        option = request.form.get('opt')
        if len(checkbox_list) != 0 and option != 'Option':
            for users in checkbox_list:
                if option == '1':
                    u = User.query.filter_by(username=users).first()
                    if u: 
                        u.delete()
                        flash(Markup('{} deleted'.format(users)))
                elif option == '2':
                    u = User.query.filter_by(username=users).first()
                    if u:
                        u.is_admin = True 
                        u.save()
                        flash('{} promoted to admin'.format(users))
                        
    list_users = User.query.all()
    return render_template('dashboard/show-users.html', list_users=enumerate(list_users))

@dash.route('/delete-user/<int:user_id>')
@admin_required
def delete_user(user_id):
    check = User.query.filter_by(id=user_id).first()
    if check:
        check.delete()
        flash('deleted')
    else:
        flash('user id not found')
    return redirect(url_for('dashboard.show_users'))

@dash.route('/edit-user/<int:user_id>', methods=['GET','POST'])
@admin_required
def edit_user(user_id):
    check = User.query.filter_by(id=user_id).first()
    if check:
        form = AddAccount()
        if request.method == 'POST':
            if form.validate_on_submit():

                name = form.name.data 
                username = form.username.data 
                password = form.password.data 
                am = form.admin.data 

                check.full_name = name 
                check.username = username 
                check.is_admin = am 
                check.set_password(password)

                check.save()
                flash('edited !')
            else:
                flash(form.errors, category='error_forms')

        form.username.data = check.username
        form.name.data = check.full_name
        form.email.data = 'emaail@adsd.com'
        form.submit.value = 'Edit'
        return render_template('dashboard/add-account.html', form=form)
    else:
        flash('user not found')

@dash.route('/add-category')
@admin_required
def add_category():
    return render_template('dashboard/add-category.html')

@dash.route('/new-category', methods=['POST'])
@admin_required
def add_newcategory():
    category_list = request.form.getlist('category[]')
    if len(category_list) != 0:
        for categories in category_list:
            if len(categories) != 0:
                try:
                    c = Category(name=categories)
                    c.save()
                    print('added new category')
                    flash(Markup('<p>Added {}</p>'.format(categories)))
                except Exception as e:
                    db.session.rollback()
                    flash(Markup('<p>cant add this one {}</p> '.format(categories)))
                    continue

    else:
        flash('please add some name')
    return redirect(url_for('dashboard.add_category'))

@dash.route('/category', methods=['GET','POST'])
@admin_required
def category_page():
    if request.method == 'POST':
        categories_list = request.form.getlist('checkcat[]')
        if len(categories_list) != 0 and request.form['option_cat'] != 'Option':
            for categories in categories_list:
                if request.form['option_cat'] == '1':
                    c = Category.query.filter_by(id=categories).first()
                    c.delete()
                    flash(Markup(
                        '<p>{} deleted</p>'.format(categories)
                    ))
    return render_template('dashboard/category.html', categories=enumerate(Category.query.all()))