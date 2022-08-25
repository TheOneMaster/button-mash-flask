from uuid import uuid4
from datetime import date, datetime
from flask_login import UserMixin

from . import db

userGames = db.Table('userGames',
                     db.Column('user_id', db.String, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('game_id', db.String, db.ForeignKey('game.id'), primary_key=True),
                     )

def generate_uuid():
    return str(uuid4())



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    dateCreated = db.Column(db.Date, default=date.today)
    

    participatedGames = db.relationship("Game", secondary=userGames, 
                                        backref=db.backref('users', lazy=True),
                                        lazy=True)
    
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    runnerUp = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)

    