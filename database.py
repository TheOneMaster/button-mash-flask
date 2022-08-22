from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import date, datetime

from app import app

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=uuid4)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    dateCreated = db.Column(db.Date, default=date.today)

    participatedGames = db.relationship("Game", secondary=userGames, backref="user", lazy="subquery")
    
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=uuid4)
    winner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    runnerUp = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)


userGames = db.Table('userGames',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     )


if __name__ == "__main__":
    db.create_all()
    