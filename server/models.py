from uuid import uuid4
from datetime import date, datetime
from flask import url_for
from flask_login import UserMixin

from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import String, Integer, Column, DateTime

from . import db


userGames = db.Table('userGames',
                     db.Column('user_id', Integer, db.ForeignKey('users.id'), primary_key=True),
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
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    country = Column(String, nullable=True)
    picture = Column(String, nullable=False, default=default_picture)
    dateCreated = Column(DateTime, default=datetime.now)
    

    participatedGames = db.relationship("Game", secondary=userGames, 
                                        backref=db.backref('users_', lazy=True),
                                        lazy=True)
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, username={self.username})"
    
class Game(db.Model):
    """
    Model for the Game table in the database
    """
    id = Column(String, primary_key=True)
    winner = Column(Integer, db.ForeignKey('users.id'), nullable=True)
    runnerUp = Column(Integer, db.ForeignKey('users.id'), nullable=True)
    dateTime = Column(DateTime, default=datetime.now)
    
    clients = Column(ARRAY(String))
