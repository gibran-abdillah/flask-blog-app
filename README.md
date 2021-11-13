# flask-blog-app


## Features 
- login with multiple user ( admin, user ) 
- bulk delete for blogs, images, user
- bulk promote users to admin 
- admin cant see email users 
- wysiwyg editor with ckeditor 
- basic rest api 
- reset password 
- cursor pagination 
- validate email and password ( avoid duplicate ) 

## Installations 
```sh
apt-get install python3 git 
git clone https://github.com/gibran-abdillah/flask-blog-app.git 
cd flask-blog-app
pip install -r requirements.txt 
```

## set up and run your script!
```
export FLASK_APP=server.py
export FLASK_ENV=development 
flask run 
```

## Before you deploy this app
before you start deploy, change your smtp information in config.py so that the reset password function can be useful and if you want to use environment to production, change with your mysql database in config.py 

### Demo 
<a href='http://gatau-ini.herokuapp.com'>http://gatau-ini.herokuapp.com</a>

## to do 
- improv on the frontend
- create migration database
- create a search feature on the blog
- track bugs and fix them
- whats next?
