from threading import Thread, Event
import time
import threading
from .player import PlayerThread

class GlobalObject:
    def __init__(self, master):
        self.master: MasterThread = master
        self.players: list[PlayerThread] = []
        self.day: int = 0
        self.started: bool = False
        self.player_num: int = None
        self.check_first_lock = threading.RLock()
        self.event_players_ready = Event()
        self.end_flag = False


class MasterThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.global_object = GlobalObject(self) # これを利用して何日目かとかを管理
        self.print_header = "[*] master.py:"

    def broadcast_data(self, data:str, log=True):
        for p in self.global_object.players:
            if p.listen_broadcast:
                p.send_data(data)
                p.log += data + "\n"


    def new_player(self, player_:PlayerThread):
        self.global_object.players.append(player_)
        name_ = player_.player_name
        ready_num = len(self.global_object.players)

        if ready_num < self.global_object.player_num:
            self.broadcast_data(f"{name_} joined! Now {ready_num}/{self.global_object.player_num} players ready, please wait all players ready...\n")
        else:
            self.broadcast_data(f"{name_} joined! Now all players ready!")
            self.start_game()

    def start_game(self):
        self.started = True
        self.global_object.event_players_ready.set()

    def end_game(self):
        self.started = False
        self.global_object.end_flag = True
        for p in self.global_object.players:
            p.end_flag = True
                

    def run(self):
        # ここでゲームを展開
        self.global_object.event_players_ready.wait()

        self.broadcast_data("\n---------- game start! ----------\n")

        for i in range(10):
            self.broadcast_data(str(i+1))
            time.sleep(1)

        self.broadcast_data("---------- game end! ----------\n")
        self.end_game()


