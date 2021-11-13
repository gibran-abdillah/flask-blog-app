from app import create_app
from app.models import db, User 
import os, config , unittest

env_type = os.environ.get('FLASK_ENV', default='development')

app = create_app(env_type=env_type)


@app.cli.command()
def create_db():
    try:
        db.create_all(app=app)
    except Exception as e:print(e)
    

@app.cli.command()
def test():
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command('seed-data')
def seed_data():
    """
    creating user admin
    """
    user = User(full_name='Gibran Abdillah', username='admin', email='mymail@gmail.com')
    user.set_password('admin')
    user.is_admin = True 
    user.save()

if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT','5000'), host='0.0.0.0')
