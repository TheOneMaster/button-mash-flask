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
        """Create a room in which the game can be played. Rooms are made up of a maximum of 4 players and
        automatically send updates to attached user. 

        Args:
            number (int, optional): The number for the room. If no number or None is passed, the default
            number of 1000 is tried. If the number is already in use, a random number between 0 and 1000 is used. Defaults to None.
        """
        
        if number is None:
            number = Room.DEFAULT_ROOM
        
        self.number = self.__generate_number(number)
        self.status = RoomStatus.OPEN
        
        self.clients = []
        self.score = {}
        
        Room.NUM_MAP[number] = self
        
        self.start_time = None
    
    
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
        
        self.clients.remove(user)
        
        if self.status == RoomStatus.CLOSED:
            self.status = RoomStatus.OPEN
            
        leave_room(self.number)
        
        if len(self.clients) == 0:
            Room.NUM_MAP.pop(self.number)
        else:
            self.roomUpdate()
            Room.lobbyUpdate()

    def roomUpdate(self):
        
        msg = {client.sid: client.username for client in self.clients}
        print(self.number)
        
        emit('room-update', msg, to=self.number)
    
    def checkUsersStatus(self, status) -> bool:
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
            scores = [score/((curr_time - self.start_time)/1000) for score in scores]
            
            # Round scores to 3 decimal places
            scores = [round(score, 3) for score in scores]
            
            scores = {client: score for score, client in zip(scores, self.clients)}
            
            emit('game-score', scores, to=self.number)

    def gameEnd(self, user):
        
        user.status = UserStatus.READY
        
        all_users_finished = self.checkUsersStatus(UserStatus.READY)
        
        if all_users_finished:
            self.status = RoomStatus.END
                
            gameID = str(uuid4)
            
            json = {
                "id": gameID,
                "datetime": datetime.now(),
                "users": [client.username for client in self.clients],
                "score": self.score
            }
            
            file_path = "/json-store/data-store.jsonl"
            
            # Write game data to jsonl file
            with Writer(file_path, 'a+', compact=True) as jsonl:
                jsonl.write(json)
                
                print(f"Game {gameID} written to data storage")     
            
            # Reset instance variables for the game
            self.start_time = None
            self.score = {}
            
        else:
            return
            
        
        
        
    
    
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
        """Create a storage class for a client's data.

        Args:
            sid (str, optional): The client's socket ID. Defaults to None.
            username (str, optional): The username of the client. Defaults to None.
            addr (str, optional): The remote address of the client. Defaults to None.
        """
        
        self.sid = sid
        self.addr = addr
        self._username = username
        
        self.status = UserStatus.READY
        
        self.room = Room.getOpenRoom()
        
        self.update()
        
        self.room.addUser(self)
        
    def __str__(self):
        return f"{self.username} connected at {self.addr}"
    
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, new_name):
        
        self._username = new_name
        
        # Update client settings
        self.update()
        
        # Update room
        self.room.roomUpdate()
        
    def update(self):
        
        name = self._username
        room = self.room.number
        
        msg = {
            "username": name,
            "room": room
        }
        
        emit('client-settings', msg)
    
  
    def changeRoom(self, room):
        
        self.room.removeUser(self)
        
        new_room = Room.NUM_MAP.get(room, None)
        
        if new_room is None:
            new_room = Room(room)
        
        else:
            try: 
                new_room.addUser(self)
                
            except ValueError as error:
                emit('error', str(error))
        
        self.room = new_room
        
        self.update()
        self.room.addUser(self)
    
    def delete(self):
        """Delete the User by removing all references to the object.
        """        
        self.room.removeUser(self)
