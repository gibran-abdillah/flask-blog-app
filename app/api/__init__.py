from flask import Blueprint

api_blueprint = Blueprint('api',__name__, url_prefix='/api')

from .errors import * 
from .views import *