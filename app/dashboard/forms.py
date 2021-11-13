from sre_constants import RANGE_UNI_IGNORE
from app.models import User 

from wtforms.fields import (
    StringField,
    PasswordField, 
    TextAreaField,
    SubmitField,
    MultipleFileField,
    BooleanField
)

from wtforms.validators import (
    DataRequired, 
    Length, 
    EqualTo, 
    ValidationError,
)

from flask_wtf.file import (
    FileAllowed, 
    FileField, 
    FileRequired
)
from app.models import User 

from flask_wtf import FlaskForm
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.utils import EMAIL_REGEX
import re 

from app.auth.forms import RegistrationForm

    


class ChangePassword(FlaskForm):

    """
    making form for change password 
    """
    password = PasswordField('enter your password',validators=[DataRequired()])

    new_password = PasswordField('new password ', validators=[
        EqualTo('confirm_password'),
        DataRequired(message='new password is required'),
        Length(min=6, max=125, message='new password length must be between 6 to 125 characters')])

    confirm_password = PasswordField('confirm password')
    submit = SubmitField('change password')

    def validate_password(self, password_field):
        if not current_user.check_password(password_field.data):
            raise ValidationError("invalid old password")

class BlogForm(FlaskForm):
    title = StringField('Title Blog',
        validators=[
            DataRequired('fill this form'),
            Length(min=15, max=125)
        ]
    )
    body_content = TextAreaField("make some awesome things")
    thumbnail = FileField('image',
        validators=[
            FileRequired(message='file required'),
            FileAllowed(['jpg','jpeg','png'], message='only images are allowed')
        ]
    )

    submit = SubmitField("Submit")

    def validate_body_content(self, body_field):
        if len(str(body_field.data).split()) < 10:
            raise ValidationError('too short for body content (minimal 10 words) ')

class ImageForm(FlaskForm):

    imgs = MultipleFileField('images',
            render_kw={'multiple':True},
            validators=[

                FileAllowed(['jpg','png','jpeg'], message='only images are allowrd')
            ]
    )    
    submit = SubmitField('upload')

class AccountForm(FlaskForm):
    name = StringField(
        label='Full Name', 
        validators=[
            DataRequired('fill this form'),
            Length(min=5, max=100, message='name length must be between 5 to 100 characters')
        ]
    )
    username = StringField(
        label='username',
        validators=[
            DataRequired('fill your username'), 
            Length(min=5, max=100)
        ]
    )
    email = StringField( 
        label='email', 
        validators=[DataRequired()])

    submit = SubmitField()
    def validate_email(self, email_field):

        current_email = current_user.email 
        check_email = User.query.filter_by(email=email_field.data).first()
        
        if not re.match(EMAIL_REGEX, email_field.data):
            raise ValidationError('invalid email')
        
        if current_email != email_field.data:
            if check_email and check_email.email != current_email:
                raise ValidationError('email already used')

    def validate_username(self, username_field):

        current_username = current_user.username
        check_username = User.query.filter_by(username=username_field.data).first()

        if re.match('[A-Z]', username_field.data):
            raise ValidationError('invalid username, dont use uppercase to your username')
        
        if username_field.data != current_username:
            if check_username and check_username.username != current_username:
                raise ValidationError('username already used')

class AddAccount(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    admin = BooleanField(label='is admin')
    submit = SubmitField('Submit')

    

