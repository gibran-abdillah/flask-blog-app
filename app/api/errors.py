from app.api import api_blueprint
from flask import make_response, jsonify

"""
error handler on api blueprint
"""

@api_blueprint.errorhandler(403)
def api_error403(e):
    return 'what are you doing here?'