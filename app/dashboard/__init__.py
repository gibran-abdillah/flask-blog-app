from flask import Blueprint

dashboard_blueprint = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# import all route from dashboard
from .views import *
from .admin import *
from .errors import *
