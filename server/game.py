from flask import request, session
from flask_socketio import SocketIO, join_room, leave_room, emit, rooms
from flask_login import current_user

from random import randint
import json
from uuid import uuid4
from random_username.generate import generate_username
from functools import wraps

from .database import Game

socket = SocketIO()

DEFAULT_ROOM = 1000

ROOM_CLIENT_MAP = {}   # Map clients to a room, allows us to query list of clients connected to specific room
CLIENT_USERNAME = {}   # Map client socket ID to username
ROOM_SCORE = {}        # Map score per tick to room

def set_room(room):
    global ROOM_CLIENT_MAP
    
    if room not in ROOM_CLIENT_MAP:
        ROOM_CLIENT_MAP[room] = {request.sid: 0}
    
    elif len(ROOM_CLIENT_MAP[room]) <= 3:
        ROOM_CLIENT_MAP[room][request.sid] = 0
    
    else:
        while len(ROOM_CLIENT_MAP[room]) >= 4:
            room = randint(0, 1000)
            
            if room not in ROOM_CLIENT_MAP:
                ROOM_CLIENT_MAP[room] = {}
        
        ROOM_CLIENT_MAP[room][request.sid] = 0
        
    join_room(room)
    session['room'] = room
    
    return room

def remove_room():
    global ROOM_CLIENT_MAP
    
    sock_id = request.sid
    r_room = None
    empty_room = False
    
    for room, conn in ROOM_CLIENT_MAP.items():
        if sock_id in conn:
            conn.pop(sock_id)
            
            if len(conn) == 0:
                empty_room = True
            
            r_room = room
            leave_room(r_room)
    
    if empty_room:
        ROOM_CLIENT_MAP.pop(r_room)
    
    return r_room
     
def getRoom():
    
    room = None
    for i in rooms():
        if i in ROOM_CLIENT_MAP:
            room = i
    
    return room

"""
Helper functions for the socketIO connection. Use to automatically emit events when changes are made to rooms/clients
"""

def update_lobby(fn):
    """
    Decorator function for functions that cause changes to the lobby. Sends 
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        
        out = fn(*args, **kwargs)
        
        room = session.get('room')
        username = session.get('username')
        
        if room and username:
    
            # Send user settings to user
            msg_client = {
                'username': username,
                'room': room
            }
            
            emit('client-settings', msg_client)
            
            # Send updated room to all users in room
            client_room = ROOM_CLIENT_MAP[room]
            roomClients = {client: CLIENT_USERNAME[client] for client in client_room.keys()}
            msg_room = {
                'clients': roomClients
            }
            
            emit('room-update', msg_room, to=room)
            
            # Send updated lobby to all users connected to the server
            
            lobbyClients = {num: len(lobby) for num, lobby in ROOM_CLIENT_MAP.items()}
            print(lobbyClients)
            
            emit('lobby-update', lobbyClients, broadcast=True)
            
        
        return out
        
    return wrapper

###############
# Base Events #
###############
@socket.on('connect')
def setupClient():
    """
    First time setup when a client connects to the socket server. Sets default values for client unless logged in.
    """    
    
    # Add username to client
    username = None
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = generate_username()[0]
    
    usernameChange(username)
    
    # Add client to room map
    roomChange(DEFAULT_ROOM)
    
    print(f"Connected: {session['username']} from {request.remote_addr}")

@socket.on('disconnect')
def disconnect():
    global CLIENT_USERNAME
    
    remove_room()
    CLIENT_USERNAME.pop(request.sid)
    
    username = session['username']
    
    print(f'Disconnected: {username} from {request.remote_addr}')


############
# Settings #
############

@socket.on('username-change')
@update_lobby
def usernameChange(name):
    global CLIENT_USERNAME       
    
    CLIENT_USERNAME[request.sid] = name
    session['username'] = name

@socket.on("room-change")
@update_lobby
def roomChange(room):
    
    remove_room()
    set_room(room)

########
# Game #
########

@socket.on('game-ready')
def gameReady():
    global ROOM_SCORE
    
    username = session.get('username')    
    roomNum = session.get('room')
    room = ROOM_CLIENT_MAP[roomNum]
    
    room[request.sid] = 1
    
    room_isReady = all(v for v in room.values())
    if room_isReady:
        ROOM_SCORE[roomNum] = {}
        emit('start-game', to=roomNum)
    else:
        emit('waiting-game')
    


@socket.on('game-tick')
def gameTick(json):
    global ROOM_SCORE
    
    room = session['room']
    tick = json['tick_id']
    score = json['score']
    client = request.sid
    
    client_list = ROOM_CLIENT_MAP[room].keys()
    curRoom = ROOM_SCORE[room]
    
    if tick not in curRoom:
        curRoom[tick] = [None for i in client_list]
    
    client_index = list(client_list)
    client_index = client_index.index(client)

    lobby_score = curRoom[tick]
    lobby_score[client_index] = round(score, 3)
    
    tickCompleted = None not in lobby_score
    
    if tickCompleted:
        emit('game-score', lobby_score,  to=room)


@socket.on('game-end')
def gameEnd():
    
    gameId = str(uuid4())
    room = session['room']
    
    curRoom = ROOM_CLIENT_MAP[room]
    
    curRoom[request.sid] = 2
    print(curRoom)
    
    if all(ready == 2 for ready in curRoom.values()):
    
        with open(f"{gameId}.json", 'w') as json_file:
            score = ROOM_SCORE.pop(room)
            json.dump(score, json_file)
            
        for client in curRoom:
            curRoom[client] = 0
            
        print(f"Game stored in {gameId}.json")
