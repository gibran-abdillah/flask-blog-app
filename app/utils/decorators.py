from flask import abort, config, request
from functools import wraps
from flask_login import current_user
import re 
from config import GeneralConfig

EMAIL_REGEX = r'([\w\d\._-]+@+[\w\d\.]+[\w.]{2,6})'

valid_exts = ' '.join(GeneralConfig.ALLOWED_EXTENSIONS)

def admin_required(f):
    @wraps(f)
    def validate_user(*args, **kwargs): 
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return validate_user

def validate_image(imgs):
    ext_name = imgs.filename.split('.')
    if ext_name and ext_name[-1] in valid_exts:
        return True 
    return False 