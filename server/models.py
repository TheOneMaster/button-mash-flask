from uuid import uuid4
from datetime import date, datetime
from flask import url_for
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from . import db


userGames = db.Table('userGames',
                     db.Column('user_id', db.String, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('game_id', db.String, db.ForeignKey('game.id'), primary_key=True),
                     )

def generate_uuid():
    return uuid4().hex

def default_picture():
    return url_for('static', filename="Images/profile.png")



class User(db.Model, UserMixin):
    """
    Model for the User Table in the database
    """
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=True)
    picture = db.Column(db.String, nullable=False, default=default_picture)
    dateCreated = db.Column(db.Date, default=date.today)
    

    participatedGames = db.relationship("Game", secondary=userGames, 
                                        backref=db.backref('users', lazy=True),
                                        lazy=True)
    
class Game(db.Model):
    """
    Model for the Game table in the database
    """
    id = db.Column(db.String, primary_key=True)
    winner = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    runnerUp = db.Column(db.String, db.ForeignKey('user.id'), nullable=True)
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)

    