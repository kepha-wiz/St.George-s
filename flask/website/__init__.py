import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

# Initialize database
db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gvfvsvf'
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    db.init_app(app)
    
    # Import blueprints with absolute paths
    from website.views import views
    from website.auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import models
    from website.models import User

    create_database(app)
    
    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

def create_database(app):
    db_path = path.join("website", DB_NAME)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print("Created Database!")
