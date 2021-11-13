import unittest

from app import create_app
from app.models import Category, db, User
from flask import current_app

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def test_app_exists(self):
        self.assertTrue(current_app is not None)
    
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_user(self):
        u = User(full_name='Gibran Abdillah', username='gibran', email='hello@gmail.com')
        u.set_password('gibran')        
        u.save()
        self.assertTrue(u)
    
    def test_add_category(self):
        c = Category(name='News')
        c.save()
        self.assertTrue(c)
    
    def test_create_admin(self):
        u = User(full_name='Gibran Ad', is_admin=True, email='asdasdsa@as.com', username='admin')
        u.set_password('admin')
        u.save()
        adm = User.query.filter_by(username='admin').first()
        self.assertTrue(adm.is_admin)
    