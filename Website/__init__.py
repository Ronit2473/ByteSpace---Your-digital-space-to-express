from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import os

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    
    # Use environment variable for secret key in production
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hELLOwORLD')
    
    # Database configuration for production vs development
    if os.environ.get('DATABASE_URL'):
        # Production: Use PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        # Fix postgres:// to postgresql:// for newer SQLAlchemy versions
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Development: Use SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Disable modification tracking to save resources
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, Post, Comment
    
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    # Updated path checking for production
    db_path = 'Website/' + DB_NAME if not os.environ.get('DATABASE_URL') else None
    
    if not os.environ.get('DATABASE_URL') and not path.exists(db_path):
        # Only create SQLite database if not using PostgreSQL
        with app.app_context():
            db.create_all()
        print("Created Database!")
    elif os.environ.get('DATABASE_URL'):
        # Create PostgreSQL tables
        with app.app_context():
            db.create_all()
        print("Created PostgreSQL Database Tables!")
