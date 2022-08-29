from flask import request, current_app
from flask_socketio import SocketIO, join_room, leave_room, emit

from random import randint

socket = SocketIO(ping_interval=.5, ping_timeout=1)

DEFAULT_ROOM = 1000
ROOM_CLIENT_MAP = {1000: set()}

def set_room(room=DEFAULT_ROOM):
    global ROOM_CLIENT_MAP
    
    if room not in ROOM_CLIENT_MAP:
        ROOM_CLIENT_MAP[room] = set([request.sid])
    
    elif len(ROOM_CLIENT_MAP[room]) <= 3:
        ROOM_CLIENT_MAP[room].add(request.sid)
    
    else:
        while len(ROOM_CLIENT_MAP[room]) >= 4:
            room = randint(0, 1000)
            
            if room not in ROOM_CLIENT_MAP:
                ROOM_CLIENT_MAP[room] = set()
        
        ROOM_CLIENT_MAP[room].add(request.sid)
        
    join_room(room)
    
    return room

def remove_room():
    global ROOM_CLIENT_MAP
    
    sock_id = request.sid
    for room, conn in ROOM_CLIENT_MAP.items():
        if sock_id in conn:
            conn.remove(sock_id)

@socket.on('connect')
def connect():
    
    room = set_room()
    
    json = {
        "room": room
    }
    
    print(ROOM_CLIENT_MAP)
    
    emit('settings', json)


@socket.on('disconnect')
def disconnect():
    leave_room()
    remove_room()
    print(ROOM_CLIENT_MAP)
    
@socket.on('settings')
def test(data):
    print(data)