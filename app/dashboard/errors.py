from app.dashboard import dashboard_blueprint as dash 
from flask import redirect, url_for

@dash.errorhandler(401)
def dash_handle401(e):
    return redirect(url_for('auth.login_page'))

@dash.errorhandler(403)
def dash_handle403(e):
    return redirect(url_for('dashboard.dashboard_index'))

