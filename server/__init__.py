import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Might have to move this into the function later
# from .game import socket
from .database import db, User

load_dotenv()

def create_app():
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLITE_URI']
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    
    db.init_app(app)
    # socket.init_app(app)
    
    login_manager = LoginManager(app=app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add blueprints to the app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app


if __name__ == "__main__":
    app = create_app()
    # socket.run(app, debug=True)
    app.run(debug=True)