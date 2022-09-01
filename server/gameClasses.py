"""

This file is a WIP. It is an attempt at a rewrite for the game to follow an object oriented structure.

It is still mostly incomplete. Work will continue once the base functionality of the website has been finished.

"""


from flask_socketio import emit, leave_room, join_room

from enum import Enum
from random import randint

class RoomStatus(Enum):
    
    OPEN = 0
    CLOSED = 1
    WAITING = 2
    ACTIVE = 3
    END = 4

class UserStatus(Enum):
    
    READY = 0
    WAITING = 1
    ACTIVE = 2


class Room():
    NUM_MAP = {}
    DEFAULT_ROOM = 1000
    
    def __init__(self, number=None):
        
        if number is None:
            number = Room.DEFAULT_ROOM
        
        self.number = self.__generate_number(room)
        self.status = RoomStatus.OPEN
        
        self.clients = []
    
    
    def __generate_number(self, num):
        
        if num not in num_map:
            return num
        
        else:
            return randint(0, 1000)
    
            
    def addUser(self, user):
        
        if self.status == RoomStatus.OPEN:
            self.clients.append(user)
            user.room = self
            
            if len(self.clients) == 4:
                self.status = RoomStatus.CLOSED
                
            join_room(self.number)
            lobbyUpdate()
            
        else:
            raise ValueError("Room is full")
        
    def removeUser(self, user):
        
        self.clients.pop(user)
        
        if self.status == RoomStatus.CLOSED:
            self.status = RoomStatus.OPEN
            
        leave_room(self.number)
        lobbyUpdate()

    def lobbyUpdate(self):
        
        msg = {
            'roomList': [client.username for client in self.clients]
        }
        
        emit('lobby-update', msg, to=self.number)

    @staticmethod
    def getOpen():
        """ Return an open room for a user to join."""
        open_room = False
        for room in NUM_MAP.values():
            if room.status == RoomStatus.OPEN:
                open_room = room
                break
        
            
  
class User():
    
    def __init__(self, sid=None, username=None, addr=None):
        
        self.sid = sid
        self.username = username
        self.addr = addr
        
        self.room = Room()
        self.room.addUser(self)
        
        self.status = UserStatus.READY
        
    def __str__(self):
        return f"{self.username}"
    
    def changeRoom(self, room):
        
        self.room.removeUser(self)
        