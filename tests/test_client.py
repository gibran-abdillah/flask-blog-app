import unittest

from flask import session
from flask.globals import request
from flask_login import current_user
from app import create_app
from app.models import User, db

# data for register / login
FULL_NAME = 'Gibran Abdillah'
USERNAME = 'hadehbang'
PASSWORD = 'cumansegini'
EMAIL = 'gatauiniisiapa@gmail.com'

class TestClient(unittest.TestCase):
    def setUp(self) -> None:

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_client = self.app.test_client()
        self.app_context.push()
        db.create_all(app=self.app)
    
    def tearDown(self) -> None:
        self.app_context.pop()
    
    def test_main_route(self):
        response = self.app_client.get('/')
        self.assertEqual(200, response.status_code)
    
    def auth_register(self):
        response = self.app_client.post('/auth/register', 
                    data={
                        'name':FULL_NAME,
                        'username':USERNAME, 
                        'email':EMAIL,
                        'password':PASSWORD, 
                        'password_confirmation':PASSWORD, 
                        'submit':'Submit'

        }, follow_redirects=True)
        return response 

    def auth_login(self, username, password, r='response'):
        with self.app_client as client:
            response = client.post('/auth/login',
                data={
                    'username':username, 
                    'password':password
                }, follow_redirects=True
            )
            if r == 'cookies':
                return response.request.cookies.items()
            return response 
    
    def test_auth_register_and_login(self):
        resp_register = self.auth_register()
        self.assertEqual(resp_register.request.path, '/auth/login')
        resp_login = self.auth_login(USERNAME,PASSWORD)
        self.assertEqual(resp_login.request.path, '/dashboard/welcome')

    def test_auth_redirects(self):
        response = self.app_client.get('/auth', follow_redirects=True)
        self.assertEqual(response.request.path, '/')
    
    def test_404_page(self):
        response = self.app_client.get('/asdsadhsadasdf')
        self.assertEqual(404, response.status_code)
    
    def test_unaunthenticated_dashboard(self):
        response = self.app_client.get('/dashboard/welcome', follow_redirects=True)
        self.assertTrue(response.request.path != '/dashboard/welcome')
    
    def test_auth_wrong_password(self):
        response = self.auth_login(username=USERNAME, password='invalidpassword')
        self.assertTrue(response.request.path != '/dashboard/welcome')
    
    def test_api_user(self):
        response = self.app_client.get('/api/users')
        self.assertTrue(response.is_json)
    
    def test_api_blogs(self):
        response = self.app_client.get('/api/blogs')
        self.assertTrue(response.is_json)
    
    def test_api_reset_password(self):
        response = self.app_client.get('/api/reset-password')
        self.assertTrue(response.is_json)
    
    def test_api_recent_posts(self):
        response = self.app_client.get('/api/recent-blogs')
        self.assertTrue(response.is_json)
    
    def create_user(self):
        u = User(full_name='Asede hadeh', username='admin', email='gatauisiap@asd.com')
        u.set_password('admin')
        u.is_admin = True 
        u.save()
    
    def test_dashboard_admin(self):
        self.create_user()
        login = self.auth_login('admin', 'admin', 'cookies')
        with self.app_client as client:
            for keys, values in login:
                client.set_cookie(server_name='localhost', key=keys, value=values)
                response = client.get('/dashboard/add-user', follow_redirects=True)
                # when not admin access /dashboard/add-user, it will redirect to homepage 
                self.assertTrue(response.request.path != '/dashboard/welcome')
    
    def test_not_valid_token(self):
        c = User.check_reset_token('asdasdasd')
        self.assertIsNone(c)    
    
    def get_token(self):
        t = User.query.all()[0].get_reset_token()
        return t 
    
    def test_get_token(self):
        self.assertTrue(
            type(self.get_token()) == str 
        )
    
    def test_valid_token(self):
        token = self.get_token()
        self.assertTrue(User.check_reset_token(token))
    
    
