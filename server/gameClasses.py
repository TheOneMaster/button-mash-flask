"""

This file is a WIP. It is an attempt at a rewrite for the game to follow an object oriented structure.

It is still mostly incomplete. It will be integrated only once the base functionality has been finished.

"""


from flask_socketio import emit, leave_room, join_room

from enum import Enum
from random import randint
from uuid import uuid4
from datetime import datetime
from jsonlines import Writer

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
    
    def __init__(self, number: int=None):
        
        if number is None:
            number = Room.DEFAULT_ROOM
        
        self.number = self.__generate_number(number)
        self.status = RoomStatus.OPEN
        
        self.clients = []
        self.score = {}
        
        self.start_time = None
        self.end_time = None
    
    
    def __generate_number(self, num: int):
        
        if num not in Room.NUM_MAP:
            return num
        
        else:
            return randint(0, 1000)
    
            
    def addUser(self, user):
        
        if self.status == RoomStatus.OPEN:
            self.clients.append(user)
            
            if len(self.clients) == 4:
                self.status = RoomStatus.CLOSED
                
            join_room(self.number)
            self.roomUpdate()
            Room.lobbyUpdate()
            
        else:
            raise ValueError("Room is full")
        
    def removeUser(self, user):
        
        self.clients.pop(user)
        
        if self.status == RoomStatus.CLOSED:
            self.status = RoomStatus.OPEN
            
        leave_room(self.number)
        self.roomUpdate()
        Room.lobbyUpdate()

    def roomUpdate(self):
        
        msg = {client.sid: client.username for client in self.clients}
        
        emit('lobby-update', msg, to=self.number)
    
    def checkUsersReady(self, status) -> bool:
        """Checks if all users share the same status

        Args:
            status (UserStatus): The status against which all clients in the room will be tested

        Returns:
            bool: The boolean value of the check
        """
                
        check = all(client.status == status for client in self.clients)
        
        return check
    
    
    def gameStart(self):
        
        self.status = RoomStatus.ACTIVE
        
        for client in self.clients:
            client.status = UserStatus.ACTIVE
            
        self.start_time = datetime.now()
        
        emit('start-game', to=self.number)
    
    def updateScore(self, tick, user, score):
        
        if tick not in self.score:
            index = self.clients.index(user)
            scores = [None for i in self.clients]
            scores[index] = score
            
            self.score[tick] = scores
            
        else:
            index = self.clients.index(user)
            scores = self.scores[tick]
            scores[index] = score
            
        if None not in scores:
            
            curr_time = datetime.now()
            
            # Get scores (clicks per second) from the totalPresses recorded in the tick
            scores = [score/(curr_time - self.start_time) for score in scores]
            
            # Round scores to 3 decimal places
            scores = [round(score, 3) for score in scores]
            
            emit('game-score', scores, to=self.number)

    def gameEnd(self):
        
        self.status = RoomStatus.END
        
        for client in self.clients:
            client.status = UserStatus.READY
            
        gameID = str(uuid4)
        
        json = {
            "id": gameID,
            "datetime": datetime.now(),
            "users": [client.username for client in self.clients],
            "score": self.score
        }
        
        file_path = "/json-store/data-store.jsonl"
        
        with Writer(file_path, 'a+', compact=True) as jsonl:
            
            jsonl.write(json)
            
            print(f"Game {gameID} written to data storage")
            
        
        
        
    
    
    @staticmethod
    def lobbyUpdate():
        
        msg = {number: len(room.clients) for number, room in Room.NUM_MAP.items()}
        
        emit('lobby-update', msg, broadcast=True)

    @staticmethod
    def getOpenRoom():
        """ Return an open room for a user to join."""
        
        # Find if open rooms exist
        for room in Room.NUM_MAP.values():
            if room.status == RoomStatus.OPEN:
                return room
        
        # Create a new room
        open_room = False    
        open_room = Room()
        
        return open_room
        
            
  
class User():
    
    def __init__(self, sid=None, username=None, addr=None):
        
        self.sid = sid
        self.username = username
        self.addr = addr
        
        self.room = Room.getOpenRoom()
        self.room.addUser(self)
        
        self.status = UserStatus.READY
        
    def __str__(self):
        return f"{self.username}"
    
    def changeRoom(self, room):
        
        self.room.removeUser(self)
        
        new_room = Room.NUM_MAP[room]
        new_room.addUser(self)
        