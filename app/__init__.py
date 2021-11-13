from flask_sqlalchemy import SQLAlchemy
from flask import Flask 
from flask_login import LoginManager
from config import conf_obj
from .utils.mail import Mail

login_manager = LoginManager()
db = SQLAlchemy()
mail = Mail()

def create_app(env_type: str='development'):

    app = Flask(__name__)
    app.config.from_object(conf_obj[env_type])

    # import and init the blueprint
    from app.main import main_blueprint
    from app.auth import auth_blueprint
    from app.api import api_blueprint
    from app.dashboard import dashboard_blueprint
    
    app.register_blueprint(api_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(dashboard_blueprint)

    # init the extensions
    login_manager.init_app(app)
    db.init_app(app)
    if env_type != 'testing':
        mail.init_app(app)

    return app 
