import os, logging
from sqlalchemy import create_engine 

BASEDIR = os.path.dirname(os.path.abspath(__file__))


def sqlite_uri(db_name: str):
    """
    generate sqlite url 
    """
    return 'sqlite:///{}'.format(os.path.join(BASEDIR, db_name))

class GeneralConfig:

    SQLALCHEMY_TRACK_MODIFICATIONS = True 
    SECRET_KEY = os.urandom(14)


    MAIL_HOST = 'smtp.mail.com'
    MAIL_SENDER = ''
    MAIL_PASSWORD = ''
    MAIL_PORT = 587 # default port for tls 
    MAIL_USETLS = True 
    MAIL_USESSL = False 
    
    ALLOWED_EXTENSIONS = ['jpg','png','jpeg']
    DIR_UPLOADS = os.path.join(BASEDIR, 'app/static/img')

class DevelopmentConfig(GeneralConfig):
    """
    configuration for development mode 
    """
    SQLALCHEMY_DATABASE_URI = sqlite_uri('development.db')
    LOG_LEVEL = logging.DEBUG

    DEBUG = True 

class ProductionConfig(GeneralConfig):
    """
    using sqlite is not recomended in production enviroment
    and sqlite cant used in heroku 
    """
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://uvYNtEWzlM:NpnKVWD4aa@remotemysql.com/uvYNtEWzlM'
    DEBUG = False 

class TestingConfig(GeneralConfig):

    """
    configuration in testing mode
    disabled csrf for testing authentication form
    """

    SQLALCHEMY_DATABASE_URI = sqlite_uri('testing.db')
    WTF_CSRF_ENABLED = False
    TESTING = True 

conf_obj = {'development':DevelopmentConfig, 
            'production':ProductionConfig,
            'testing':TestingConfig
}
