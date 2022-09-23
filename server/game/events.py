import os

from flask import request, session
from flask_socketio import emit
from flask_login import current_user

from random_username.generate import generate_username

from .classes import Client, ClientStatus, RoomStatus
from .. import socket
from ..models import Game


@socket.on('connect')
def setupClient():
    
    username = None
    id=None
    
    if current_user.is_authenticated:
        username = current_user.username
        id = current_user.id
    else:
        username = generate_username()[0]
        
    sid = request.sid
    addr = request.environ.get("HTTP_TRUE_CLIENT_IP", request.remote_addr)
    
    user = Client(id, sid, username, addr)   
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


@socket.on('latency-ping')
def ping():
    
    emit('latency-pong')


@socket.on('game-ready')
def gameReady():
    
    user = session.get("user")
    user.status = ClientStatus.WAITING
    
    room = user.room
    
    ## Conditions to be reached before starting the game
    
    # Minimum 2 players (in prod)
    
    debug_env = os.environ.get("DEBUG") == "TRUE"
    
    if debug_env:
        min_players_check = True
    else:
        min_players_check = len(room) < 2
    
    # all clients are waiting (have pressed the start game button)
    all_users_ready = user.room.checkUsersStatus(ClientStatus.WAITING)
    
    if min_players_check and all_users_ready:
        user.room.playGame()
    else:
        emit('waiting-game')

@socket.on('game-tick')
def gameTick(tick):
    
    tick_num = tick['tick_id']
    score = tick['score']
    user = session.get('user')
    
    room = user.room
    
    if room.status != RoomStatus.END:
        game = room.game
        game.update_score(user, score)
