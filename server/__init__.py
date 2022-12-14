import os

from dotenv import load_dotenv

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

from datetime import date

load_dotenv()

socket = SocketIO()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'auth.login'


def create_app():
    
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQL_DB']
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    
    app.jinja_env.globals['date'] = date.today()
    
    # Initialize the various flask libraries
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socket.init_app(app)
    
    
    # Add blueprints to the app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Add socketIO events
    from . import game

    return app


if __name__ == "__main__":
    app = create_app()
    
    socket.run(app, debug=True)
    # app.run(debug=True)
