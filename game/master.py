from threading import Thread, Event
import time
import threading
import statistics
import random

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
        self.event_wait_next = Event()
        self.end_flag: bool = False
        self.roles_dict = {i: r for i, r in enumerate(classes.roles.role_list())}
        self.players_alive: list[PlayerThread] = []
        self.vote_list: [str] = []
        self.suspect_list: [str] = []


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
        self.global_object.players_alive.append(player_)
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

        if self.global_object.wait_answer_count < len(self.global_object.players_alive):
            print(self.print_header, f"answer: {self.global_object.wait_answer_count}/{len(self.global_object.players_alive)}")
            pass
        else:
            self.global_object.event_wait_answer.set()

    def submit_answer(self, submit_type, user):
        if submit_type == "vote":
            self.global_object.vote_list.append(user)
        elif submit_type == "suspect":
            self.global_object.suspect_list.append(user)
        

    def select_role(self):
        self.broadcast_data("select role:\n")

        roles_dict_str = "\n".join([ f"{k}: {v}" for k, v in self.global_object.roles_dict.items()])
        self.broadcast_data(roles_dict_str + "\n")
        self.global_object.event_players_role_select.set() # playerスレッドにroleの選択を開始させる

        self.wait_answer_start() # playerスレッドの処理終了を待つ

        self.broadcast_data("ok")

    
    def delete_player(self, user_name):
        found = next( (p for p in self.global_object.players_alive if p.player_name==user_name) ,None)
        if found:
            self.global_object.players_alive.remove(found)
            found.set_not_alive()


    def alive_players_dict(self):
        alives = self.global_object.players_alive
        return {i:p.player_name for i, p in enumerate(alives)}


    def vote_broadcast(self):
        self.global_object.vote_list = [] # 一応初期化
        # 疑う対象の一覧を取得
        p_dict = self.alive_players_dict()
        # 選択肢をbroadcast
        p_dict_str = "\n".join([ f"{k}: {v}" for k, v in p_dict.items()])
        self.broadcast_data("vote user:\n" + p_dict_str + "\n")

    
    def anounce_vote_result(self):
        top_user = statistics.multimode(self.global_object.vote_list) # modeのlistを返す
        execution_user = random.choice(top_user) # 重複があるとランダムに1人
        self.broadcast_data(f"投票の結果、{execution_user} が処刑されました")
        self.delete_player(execution_user) # player_aliveから消す
        self.global_object.vote_list = []

    
    def anounce_suspect_result(self):
        top_user = statistics.multimode(self.global_object.suspect_list) # modeのlistを返す
        suspected_user = random.choice(top_user) # 重複があるとランダムに1人
        self.broadcast_data(f"{suspected_user} が疑われています")
        self.global_object.suspect_list = []



                

    def run(self):
        # ここでゲームを展開
        self.global_object.event_players_ready.wait()

        self.broadcast_data("\n---------- game start! ----------\n")

        self.select_role()


        # 0日目の処理
        self.broadcast_data(f"\n---------- 0日目です ----------\n")
        print(self.print_header, "0 day")
        self.global_object.suspect_list = [] # 村人疑う用配列の初期化
        self.global_object.event_wait_next.set()
        self.global_object.event_wait_next.clear()

        self.wait_answer_start()
 

        # ゲーム終了までループ
        game_loop_flag = True
        while game_loop_flag:
            self.global_object.day += 1
            # day日目が始まりました.
            self.broadcast_data(f"\n---------- {self.global_object.day}日目が始まりました ----------\n")

            ## ゲーム終了判定 ->  game_loop_flag=False
            # if True:
            #     game_loop_flag = False


            ## 朝 (スレッドに指令を出す)
            self.broadcast_data(f"\n------ {self.global_object.day}日目 朝 ------\n")
            self.anounce_suspect_result() #疑うの結果報告
            self.global_object.event_wait_next.set()
            self.global_object.event_wait_next.clear()
 
            self.wait_answer_start()


            ## 昼: 投票
            self.broadcast_data(f"\n------ {self.global_object.day}日目 昼 ------\n")
            self.vote_broadcast() # アナウンス
            self.global_object.event_wait_next.set() # 投票を実施させる
            self.global_object.event_wait_next.clear()
            self.wait_answer_start() # playerスレッドの投票終了を待つ
            self.anounce_vote_result()
            


            ## 夜 (スレッドに指令を出す)
            self.broadcast_data(f"\n------ {self.global_object.day}日目 夜 ------\n")
            self.global_object.suspect_list = [] # 村人疑う用配列の初期化
            self.global_object.event_wait_next.set()
            self.global_object.event_wait_next.clear()

            self.wait_answer_start()



        # for i in range(10):
        #     self.broadcast_data(str(i+1))
        #     time.sleep(1)

        # 誰が勝ったか? <- 終了判定の部分でやってもいいかも

        self.broadcast_data("---------- game end! ----------\n")
        self.end_game()


