from app.main import main_blueprint
from flask import render_template, url_for, send_from_directory
from config import GeneralConfig
from app import mail
from app.utils.mail import Message

@main_blueprint.route('/')
def index_page():
    return render_template('index.html')

@main_blueprint.route('/img/<string:filename>')
def show_image(filename):
    return send_from_directory(GeneralConfig.DIR_UPLOADS, filename)

