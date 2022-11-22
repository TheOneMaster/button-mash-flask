import os
from datetime import datetime
from uuid import uuid4

import classes  # Typing checks
from flask_socketio import emit

from server import db, socket
from server.models import Game, User


class BaseGame():
    
    def __init__(self, room: classes.Room, time=10, freq=30) -> None:
        """Base storage class for games. Each game is attached to a room.

        Args:
            room (Room): Room object that the game is being played in
            time (int, optional): Maximum time for the game in seconds. Defaults to 10.
            freq (int, optional): Frequency (tick rate) of the game. Defaults to 30.
        """
        self.room      = room
        self.gameTime  = time
        self.freq      = freq
        self.tickTime  = 1/freq
        self.startTime = None
        
    def __repr__(self) -> str:
        rep = f"{self.__class__.__name__}(room={self.room.number}, freq={self.freq})"
        return rep
        
        
class TimeGame(BaseGame):
    
    def __init__(self, room: classes.Room, time=10, freq=30) -> None:
        """Time-based game. Button Mash for a specified duration of time and the winner is
        the one with the highest score at the end of the time period.

        Args:
            room (Room): Room object that the game is being played in
            time (int, optional): Maximum time for the game in seconds. Defaults to 10.
            freq (int, optional): Frequency (tick rate) of the game. Defaults to 30.
        """
        super().__init__(room, time, freq)
        
        self.totalTicks = freq * time
        self.ticks = [None] * self.totalTicks
        
        self._cur_score = None
        
    def start_game(self) -> None:
        self.startTime = datetime.now()
        self._cur_score = [0 for i in self.room.clients]
        
        msg = {
            "type": "time",
            "freq": self.freq,
            "time": self.gameTime
        }
        
        emit("start-game", msg, to=self.room.number)
        self.game_loop()
    
    def game_loop(self) -> None:
        
        for i in range(self.totalTicks):
            
            total_score = self._cur_score.copy()
            self.ticks[i] = total_score
            
            cur_time = datetime.now()
            
            delta = cur_time - self.startTime
            delta_sec = delta.total_seconds()
            
            scores = [score/delta_sec for score in total_score]
            scores = [round(score, 3) for score in scores]
            
            usernames = [client.username for client in self.room.clients]
            scores = {username: score for username, score in zip(usernames, scores)}
            
            emit('game-score', scores, to=self.room.number)
            
            socket.sleep(self.tickTime)
            
    def end_game(self) -> None:
        
        emit("game-end", to=self.room.number)
        
        # Do not save game if debug mode
        if os.environ.get('DEBUG') == 'TRUE':
            return
        
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
        
        # Add game to participatedGames for any user that is in the DB
        for client in self.room.clients:
            if client.id is not None:
                user = User.query.filter_by(id=client.id).first()
                user.participatedGames.append(game)
        
        db.session.add(game)
        db.session.commit()
        
    def update_score(self, client: classes.Client, score: int) -> None:
        
        index = self.room.clients.index(client)
        self._cur_score[index] = score
