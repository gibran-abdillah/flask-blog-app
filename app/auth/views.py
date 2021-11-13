from operator import or_
import re
from app import auth
from app.auth import auth_blueprint

from flask import (
    render_template, 
    url_for, 
    redirect, 
    flash,
    request,
    abort
)
from flask_login import login_user, current_user

from app.auth.forms import RegistrationForm, LoginForm, NewPassword
from app.models import User
from sqlalchemy import or_

@auth_blueprint.route('/')
def index_auth():
    return redirect(url_for('main.index_page'))

@auth_blueprint.route('/login', methods=["POST", "GET"])
def login_page():

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            pw = form.password.data
            check_exist = User.query.filter(
                or_(User.username==username, User.email==username))\
                    .first()
            if check_exist and check_exist.check_password(pw):
                login_user(check_exist, remember=form.rememberme)
                return redirect(url_for('dashboard.dashboard_index'))
            else:
                flash('invalid username/password')
        else:
            flash(form.errors, category='error_forms')
    return render_template('auth/login.html', form=form)

@auth_blueprint.route('/register', methods=['GET','POST'])
def register_page():
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():

            name = form.name.data
            username = form.username.data 
            password = form.password.data
            email = form.email.data 
            
            u = User(full_name=name, username=username, email=email)
            u.set_password(password)
            u.save()

            flash('registered, you can login now')
            return redirect(url_for('auth.login_page'))
    
        else:
            flash(form.errors, category='error_forms')

    return render_template('auth/register.html', form=form)

@auth_blueprint.route('/reset-password')
def reset_password():
    return render_template('auth/reset-password.html')

@auth_blueprint.route('/reset-password/<string:token>', methods=['GET','POST'])
def reset_pw(token):
    form = NewPassword()
    validate_token = User.check_reset_token(token)
    if validate_token:
        if request.method == 'POST':
            if form.validate_on_submit():
                u = User.query.filter_by(id=validate_token).first()
                u.set_password(form.password.data)
                u.save()
                flash('changed :D')
            else:
                flash(form.errors, category='error_forms')
        return render_template('auth/new-password.html', form=form)
    flash('invalid token')
    return redirect(url_for('auth.reset_password'))

