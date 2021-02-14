from threading import Thread, Event
import time
import threading
from .player import PlayerThread
import classes.roles


class GlobalObject:
    def __init__(self, master):
        self.master: MasterThread = master
        self.players: list[PlayerThread] = []
        self.day: int = 0
        self.started: bool = False
        self.player_num: int = None
        self.check_first_lock = threading.RLock()
        self.wait_answer_lock = threading.RLock()
        self.wait_answer_count = 0
        self.event_players_ready = Event()
        self.event_players_role_select = Event()
        self.event_wait_answer = Event()
        self.end_flag: bool = False
        self.roles_dict = {i: r for i, r in enumerate(classes.roles.role_list())}


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


    def wait_answer_start(self):
        self.global_object.event_wait_answer.clear()
        self.global_object.wait_answer_count = 0
        self.global_object.event_wait_answer.wait()


    def wait_answer_done(self):
        with self.global_object.wait_answer_lock:
            self.global_object.wait_answer_count += 1
        if self.global_object.wait_answer_count < self.global_object.player_num:
            pass
        else:
            self.global_object.event_wait_answer.set()
        

    def select_role(self):
        self.broadcast_data("select role:\n")

        roles_dict_str = "\n".join([ f"{k}: {v}" for k, v in self.global_object.roles_dict.items()])
        self.broadcast_data(roles_dict_str + "\n")
        self.global_object.event_players_role_select.set() # playerスレッドにroleの選択を開始させる

        self.wait_answer_start() # playerスレッドの処理終了を待つ

        self.broadcast_data("ok")

                

    def run(self):
        # ここでゲームを展開
        self.global_object.event_players_ready.wait()

        self.broadcast_data("\n---------- game start! ----------\n")

        self.select_role()

        # 0日目の処理
        # 
        # 

        # ゲーム終了までループ
        game_loop_flag = True
        while game_loop_flag:
            self.global_object.day += 1
            # day日目が始まりました.
            self.broadcast_data(f"\n---------- {self.global_object.day}日目が始まりました ----------\n")

            ## ゲーム終了判定 ->  game_loop_flag=False
            if True:
                game_loop_flag = False


            ## 朝 (スレッドに指令を出す)
            # 知識を与える

            # 行動


            ## 昼 (スレッドに指令を出す)
            # 知識を与える

            # 行動


            ## 夜 (スレッドに指令を出す)
            # 知識を与える

            # 行動



        # for i in range(10):
        #     self.broadcast_data(str(i+1))
        #     time.sleep(1)

        # 誰が勝ったか? <- 終了判定の部分でやってもいいかも

        self.broadcast_data("---------- game end! ----------\n")
        self.end_game()


