from flask import url_for, escape, current_app
from requests.cookies import MockResponse
from sqlalchemy import extract
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime
from flask import flash, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as serializer 
from app import db, login_manager
import re, random, os, config

RANDOM_CHAR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz123456789'

class BaseModel:

    def save(self):
        db.session.add(self)
        self.__commit()
    
    def __commit(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        self.__commit()


class PaginateGenerator: 
    """
    pagination generator for post models
    """
    def __init__(self, modquery, 
                page: int=1, 
                perpage: int=6, 
                category: str=None,
                previous_id: int=1):
        """"
        :param modquery > models query (eg : User, Post)
        :param page 
        :param previous_ud > "next_id" that used for previous id ( on page 1 )
        """

        self.modquery = modquery
        self.page = page 
        self.previous_id = previous_id
        self.perpage = perpage
        self.category = category
    
    def generate(self) -> dict:

        if self.page == 1:
            self.previous_id = 0 
        
        if self.page != 1 and self.previous_id == 0:
            raise ValueError('invalid previous id for page >= 1')
        
        self.total_data = self.modquery.query.count()
        self.page_generate = round(self.total_data / self.perpage)
        fetch_data = self.modquery.query.filter(self.modquery.id >= self.previous_id)
        
        if not self.category:
            self.data = fetch_data.limit(self.perpage+1).all()
        else:
            self.data = fetch_data.filter(
                self.modquery.post_cat.any(name=self.category)
            ).limit(self.perpage+1).all()
        
        return {
            'items':self.validate_data(), 
            'next_id':self.next_id,
            'has_next':self.has_next
        }

    @property
    def has_next(self) -> bool:
        return len(self.data) > self.perpage 
    
    @property
    def next_id(self) -> int:
        if self.has_next:
            return self.data[-1].id
        return False 

    def validate_data(self):
        if not self.data:
            return 0 

        return [
            _.to_dict() 
            for _ in self.data
        ]
        
post_tags = db.Table('tags',
                db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
)

class User(db.Model, BaseModel, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(25), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # buat nampung postingan dan gambar user0
    user_post = db.relationship('Post', backref='author', 
                                lazy='dynamic',
                                cascade='all,delete')

    user_image = db.relationship('Image', backref='image_author', 
                                 lazy='dynamic',
                                 cascade='all,delete')


    def set_password(self, password: str) -> None:
        """
        set and hashing the password 
        """
        self.password = generate_password_hash(password, method='sha512', salt_length=5)
    
    def check_password(self, password: str):
        return check_password_hash(self.password, password)
    
    def __repr__(self) -> str:
        if self.is_admin:
            return '<admin:{}'.format(self.username)
            
        return '<username:{}'.format(self.username)

    
    def to_dict(self) -> dict:
        """
        return dict for api 
        """
    
        return {
            'user_id':self.id, 
            'posts':[
                x.to_dict() for x in self.user_post.all()
            ],
            'total_posts':self.user_post.count()
        }
    
    def get_reset_token(self, expires_sec=3600):
        """
        generate token for reset password
        """
        s = serializer(current_app.config.get('SECRET_KEY'),expires_in=expires_sec)
        return s.dumps({'id':self.id}).decode('utf-8')
    
    @classmethod
    def check_reset_token(cls, token: str):
        """
        validate reset password token
        """
        s = serializer(current_app.config.get('SECRET_KEY'),3600)
        try:
            id_user = s.loads(token)['id']
            return id_user
        except:
            return None 

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_key = ''.join(random.choice(RANDOM_CHAR) for _ in range(25))


class Post(db.Model, BaseModel):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(125), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_name = db.Column(db.String(125))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    slug_uri = db.Column(db.String(120))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # many to many relationship in category, There is attribute 'postingan' in Category
    post_cat = db.relationship('Category', secondary=post_tags, backref=db.backref('postingan', lazy='dynamic'))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.slug_uri = self.set_slug(self.title)

    def __repr__(self):
        return '<title:{}'.format(self.title)
    
    @classmethod
    def by_month(cls, month: int):

        '''
        filter posts by month
        '''

        result = cls.query.filter(
            extract('month', cls.created_at) == month).all()

        return result
            
    @property
    def total_post(self):
        return self.query.order_by(None).count()
    
    def to_dict(self)-> dict:

        return {
            'post_id':self.id, 
            'created_at':self.created_at.strftime('%d/%m/%y'),
            'title':escape(self.title),
            'slug':self.slug_uri,
            'preview':' '.join(self.content.split()[0:11]),
            'thumbnail':self.image_name
        }
    
    def to_show(self) -> dict:
 
        return {
            'id':self.id, 
            'content':self.content,
            'title':self.title, 
            'thumbnail_url':url_for('static', filename='img/{}'.format(self.image_name)),
            'created_at':self.created_at,
            'author':self.author.username,
        }
    
    def set_slug(self, title: str):
        slugy = re.findall('([\w\d\s]+)', title)
        if len(slugy) != 0:
            slug_uri = ''.join(c.replace(' ','-') for c in slugy)
            if slug_uri.endswith('-'):
                return slug_uri[:len(slug_uri)-1]
            else:
                return slug_uri
        else:
            flash('cant set slug')
    
    def delete(self):
        """"
        delete data from db and delete images on post
        """

        db.session.delete(self)
        if self.image_name:
            image = os.path.join(config.GeneralConfig.DIR_UPLOADS, self.image_name)
            if os.path.exists(image):
                os.remove(image)
        db.session.commit()
    
    
    
class Category(db.Model, BaseModel):
    __tablename__ = 'category'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    
    def __repr__(self):
        return '<name:{}'.format(self.name)
    
    def __init__(self, name: str):
        if ' ' in name:
            raise ValueError('space not allowed for category')
        self.name = name.capitalize()
    
    def to_dict(self):
        return {
            'id':self.id, 
            'name':self.name, 
            'post_id': [
                posts.id for posts in self.postingan.all()
            ]
        }

class Image(db.Model, BaseModel):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True, unique=True)
    image_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # nanti di sini ada property image_author, isinya author si user 
    def set_name(self, filename: str):
        self.image_name = filename.split('.')[0]

    def __repr__(self) -> str:
        return '<image_url:{}'.format(self.image_url)
    
    def delete(self) -> None:
        """
        delete image from db and delete image on storage 
        """
        image_path = os.path.join( 
            config.GeneralConfig.DIR_UPLOADS, self.image_name
        )

        if os.path.exists(image_path):
            os.remove(image_path)

        db.session.delete(self)
        db.session.commit()

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
