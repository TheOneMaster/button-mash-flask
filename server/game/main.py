from uuid import uuid4
from flask_socketio import emit

from datetime import date, datetime
import jsonlines

from .. import socket


class MashGame():
    
    def __init__(self, room, time=10, freq=30) -> None:
        
        self.gameTime = time
        self.freq = freq
        self.room = room
        
        self.tickTime = 1/freq
        self.totalTicks = freq * time
        self.ticks = {}
        
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
            
            delta = cur_time - self.startTime
            delta_sec = delta.total_seconds()
            
            scores = [score/delta_sec for score in total_score]
            
            # Round to 3 decimal places
            scores = [round(score, 3) for score in scores]
            
            emit('game-score', scores, to=self.room.number)
            
            socket.sleep(self.tickTime)
            
    def end_game(self):
        
        json_store_path = "json-store/data-store.jsonl"
        gameID = str(uuid4())
               
        with jsonlines.open(json_store_path, mode='a', compact=True) as jsonl:
            
            json = {
                "id": gameID,
                "datetime": str(datetime.now()),
                "players": [client.username for client in self.room.clients],
                "ticks": self.ticks
            }
            
            jsonl.write(json)
            
            print(f"Game: {gameID} has been written to data storage")
            
            emit('game-end', to=self.room.number)
            
    def update_score(self, client, score):
        
        index = self.room.clients.index(client)
        
        self._cur_score[index] = score
        
        