from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators

from wtforms import (
    StringField,
    SubmitField, 
    PasswordField,
    ValidationError
)
from wtforms.fields.core import BooleanField

from wtforms.fields.html5 import EmailField


from wtforms.validators import (
    Length, 
    DataRequired, 
    EqualTo,
    Email
)
from wtforms.widgets.core import CheckboxInput

from app.models import User
from app.utils import EMAIL_REGEX

import re

class RegistrationForm(FlaskForm):
    name = StringField(
        label="Full Name",
        validators=[DataRequired()], 
        render_kw={'class':'outline-dark'}
    
    )
    username = StringField(
        label="username",
        validators=[ 
            DataRequired(message='fill this form'),
            Length(min=5, max=125, message='length of username must be between 5 to 125')
        ]
    )

    email = EmailField(
        label='email',
        validators=[DataRequired(message='email required')]
    )

    password = PasswordField(
        label="password",
        validators=[ 
            DataRequired("password is required"),
            Length(min=6, max=200, message="length password must be between 6 to 200 characters"),
            EqualTo("password_confirmation", message='password doesnt match')
     
        ]
    )

    password_confirmation = PasswordField(
        label="confirmation password", 
        validators=[DataRequired(message='required')]
    )
    show_password = BooleanField('show password ')

    submit = SubmitField("register")

    def validate_name(self, name_field):
        """
        validate full name
        return error when unique characters in full name 
        """
        if re.match(r'[\d_.]', name_field.data):
            raise ValidationError("numeric / unique characters not allowed")
    
    def validate_username(self, username_field):
        """
        validate username form
        return error when username already used / username contain uppercase
        """
        if re.match(r'[A-Z]', username_field.data):
            raise ValidationError("you only can using lowercase for username")
        
        if User.query.filter_by(username=username_field.data).first():
            raise ValidationError("username already registered, try another one")
    
    def validate_email(self, email_field):
        if User.query.filter_by(email=email_field.data).first():
            raise ValidationError("email has registered, try another one")
        
        if not re.match(EMAIL_REGEX, email_field.data):
            raise ValidationError('invalid email')

class NewPassword(FlaskForm):
    password = PasswordField(
        label='password', 
        validators=[
            Length(min=7, max=100, message='length of password must be between 7 to 100'),
            DataRequired('fill this form'),
            EqualTo('confirm_password')
        ]
    )
    confirm_password = PasswordField()
    submit = SubmitField('reset')

class LoginForm(FlaskForm):
    username = StringField("username",
        validators=[DataRequired("please enter your username"),
                    Length(min=5, max=125, message='username length must be between 5 to 125')]
    )

    password = PasswordField("password", validators=[DataRequired()])
    rememberme = BooleanField('remember me')
    submit = SubmitField("login")