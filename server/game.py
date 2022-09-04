from flask import request, session

from flask_socketio import SocketIO, emit
from flask_login import current_user

from random_username.generate import generate_username

from .gameClasses import User, Room, UserStatus

socket = SocketIO()


@socket.on('connect')
def setupClient():
    
    username = None
    
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = generate_username()[0]
        
    sid = request.sid
    addr = request.remote_addr
    
    user = User(sid, username, addr)
    
    session['user'] = user
    
    print(user)
    
@socket.on('disconnect')
def disconnect():
    
    user = session.get('user')
    username = user.username
    addr = user.addr
    
    user.delete()
    
    session.pop('user')
    
    print(f"Disconnected: {username} from {addr}")


@socket.on('username-change')
def usernameChange(name):
    
    user = session.get('user')
    
    user.username = name
    
@socket.on('room-change')
def roomChange(number):
    
    user = session.get('user')
    
    user.changeRoom(number)

    
@socket.on('game-ready')
def gameReady():
    
    user = session.get("user")
    user.status = UserStatus.WAITING
    
    all_users_ready = user.room.checkUsersStatus(UserStatus.WAITING)
    
    if all_users_ready:
        user.room.gameStart()
    else:
        emit('waiting-game')

@socket.on('game-tick')
def gameTick(tick):
    
    tick_num = tick['tick_id']
    score = tick['score']
    user = session.get('user')
    
    room = user.room
    
    room.updateScore(tick_num, user, score)
    
@socket.on('game-end')
def gameEnd():
    
    user = session.get('user')
    
    room = user.room
    room.gameEnd(user)
