from flask_socketio import emit, leave_room, join_room

from enum import Enum
from random import randint
from uuid import uuid4
from datetime import datetime
import jsonlines

from .. import socket, db
from ..models import Game, User

class RoomStatus(Enum):   
    OPEN = 0
    CLOSED = 1
    WAITING = 2
    ACTIVE = 3
    END = 4

class ClientStatus(Enum): 
    READY = 0
    WAITING = 1
    ACTIVE = 2


  
class Client():
      
    def __init__(self, id:str=None, sid:str=None, username:str=None, addr:str=None):
        """Create a storage class for a client's data.

        Args:
            sid (str, optional): The client's socket ID. Defaults to None.
            username (str, optional): The username of the client. Defaults to None.
            addr (str, optional): The remote address of the client. Defaults to None.
        """
        self.id = id
        self.sid = sid
        self.addr = addr
        self._username = username
        
        self.status = ClientStatus.READY
        
        self.room = Room.getOpenRoom(id)
        
        self.update()
        
        self.room.addUser(self)
        
    def __str__(self):
        return f"{self.username} connected at {self.addr} in room {self.room.number}"
    
    
    def __eq__(self, __o: object) -> bool:
        
        if isinstance(__o, Client):
            if __o.id is not None:
                return __o.id == self.id
            
        return False
    
    
    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, new_name):
        
        self._username = new_name
        
        # Update client settings
        self.update()
        
        # Update room
        self.room.roomUpdate()
       
       
    def update(self):
        """Update the client when changes are made
        """
        
        msg = {
            "username": self._username,
            "room": self.room.number
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
                emit(error.message)
        
        self.room = new_room
        
        self.update()
        self.room.addUser(self)
        
        print(f"{self.username} moved to room {self.room.number}")
    
    def delete(self):
        """Delete the User by removing all references to the object.
        """        
        self.room.removeUser(self)


class MashGame():
    
    def __init__(self, room, time=10, freq=30) -> None:
        
        self.gameTime = time
        self.freq = freq
        self.room = room
        
        self.tickTime = 1/freq
        self.totalTicks = freq * time
        self.ticks = [None] * self.totalTicks
        
        self.startTime = None
        self._cur_score = None
        
    def start_game(self):
        self.startTime = datetime.now()
        self._cur_score = [0 for i in self.room.clients]
        
        msg = {
            "freq": self.freq,
            "time": self.gameTime
        }
        
        emit("start-game", msg, to=self.room.number)
        
        # Run game
        self.game_loop()
                   
    def game_loop(self):
        
        for i in range(self.totalTicks):
            
            total_score = self._cur_score.copy()
            self.ticks[i] = total_score
            
            cur_time = datetime.now()
            
            # Use time delta from start to now to calculate score (clicks per second)
            delta = cur_time - self.startTime
            delta_sec = delta.total_seconds()
            
            scores = [score/delta_sec for score in total_score]
            
            # Round to 3 decimal places
            scores = [round(score, 3) for score in scores]
            
            # Attach usernames to scores being sent
            usernames = [client.username for client in self.room.clients]
            scores = {username: score for username, score in zip(usernames, scores)}
            
            emit('game-score', scores, to=self.room.number)
            
            socket.sleep(self.tickTime)
            
    def end_game(self):
        
        emit('game-end', to=self.room.number)
        
        gameID = str(uuid4())        
        
        clients = [client.username for client in self.room.clients]
        
        # Get winner and runner up
        
        final_score = self.ticks[-1]
        scores_sorted = sorted(final_score, reverse=True)                       # Sort scores in descending order to find top placers
        sorted_index = [final_score.index(score) for score in scores_sorted]    # Index for the scores sorted in descending order
        podium_clients = [self.room.clients[i] for i in sorted_index][:2]       # Client objects for the top 2 placing clients
        
        podium = {
            'winner': podium_clients[0].id,
            'runnerUp': podium_clients[1].id
        }
        
        # Create new game object from game data
        game = Game(id=gameID, clients=clients, ticks=self.ticks, **podium)
        
        for client in self.room.clients:
        # Add game to participatedGames for any user that is in the DB
            
            if client.id is not None:
                user = User.query.filter_by(id=client.id).first()
                user.participatedGames.append(game)
        
        
        db.session.add(game)
        db.session.commit()
            
            
    def update_score(self, client, score):
        
        index = self.room.clients.index(client)
        
        self._cur_score[index] = score
        

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
        
        Room.NUM_MAP[number] = self
        
        self.game = None
    
    
    def __len__(self):
        return len(self.clients)
    
    
    def __generate_number(self, num: int):
        
        while num in Room.NUM_MAP:
            num = randint(0, 1000)
            
        return num
    
            
    def addUser(self, user):
        
        if self.status == RoomStatus.OPEN:
            
            if any(user==client for client in self.clients):
                raise ValueError("User is already in room")
            
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
            Room.NUM_MAP.pop(self.number, None)
        else:
            self.roomUpdate()

        Room.lobbyUpdate()

    def roomUpdate(self):
        
        msg = {client.sid: client._username for client in self.clients}
        
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
      
    def playGame(self):
        
        self.status = RoomStatus.ACTIVE
        
        for client in self.clients:
            client.status = ClientStatus.ACTIVE
            
        self.game = MashGame(self, time=5)
        self.game.start_game()
        
        self.status = RoomStatus.END
        
        for client in self.clients:
            client.status = ClientStatus.READY
            
        self.game.end_game()
        del self.game
        
    @staticmethod
    def lobbyUpdate():
        """Update the whole lobby about any room changes
        """
        msg = {number: len(room.clients) for number, room in Room.NUM_MAP.items()}
        
        emit('lobby-update', msg, broadcast=True)

    @staticmethod
    def getOpenRoom(client_id=None):
        """ Return an open room for a user to join."""
        
        # Find if open rooms exist
        for room in Room.NUM_MAP.values():
            if room.status == RoomStatus.OPEN:
                
                # Check that client is not already in room                
                if client_id is not None and any(client_id == client.id for client in room.clients):
                    continue
                
                return room
        
        # Else create a new room  
        open_room = Room()
        
        return open_room            
