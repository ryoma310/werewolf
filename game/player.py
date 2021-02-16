from threading import Thread
import socket
import sys
import errno
import threading
from classes.abst_classes.role_abst import Role_AbstClass
import classes.roles
from classes.util import TIME_OF_DAY
import time


class PlayerThread(Thread):
    def __init__(self, soc, master_):
        Thread.__init__(self)
        self.socket = soc
        self.buf_size = 512
        self.master_ = master_
        self.print_header = None
        self.player_name = None
        self.listen_broadcast = False
        self.end_flag = False
        self.log = ""
        self.role:Role_AbstClass = None
        self.send_data_lock = threading.RLock()
        self.recv_data_lock = threading.RLock()
        self.alive = True
    

    def initialize(self):
        self._id = threading.get_ident()
        self.print_header = f"[*] player.py ({self._id}):"


    def recv_data(self):
        with self.recv_data_lock:
            try:
                data = self.socket.recv(self.buf_size)
            except InterruptedError as e:
                print(self.print_header, "recv:", e)
                return False, ""

            if (len(data) == 0):
                # EOF
                print(self.print_header, "recv:EOF")
                return False, ""

            data = data.rstrip()
            try:
                print(self.print_header, data.decode('utf-8'))
            except UnicodeDecodeError:
                print(self.print_header, "UnicodeDecodeError")
                return False, ""
            return True, data.decode('utf-8')
    

    def send_data(self, data:str, with_CR=True):
        with self.send_data_lock:
            try:
                # self.socket.send(data.encode() + (b"\n" if with_CR else b""))
                self.socket.sendall(data.encode() + (b"\n" if with_CR else b""))
            except InterruptedError as e:
                print(self.print_header, "send error:", e)
                return False
            time.sleep(0.3)
            return True


    def check_start(self):
        # TODO ユーザ名で再接続処理
        if self.master_.global_object.started:
            ok_send = self.send_data("the game has already started, please wait and reconnect in next game.")
            return True
        else:
            return False
            

    def check_first(self):
        #TODO ちゃんと他の人が設定中なんで待ってねって言ったほうが親切か.
        with self.master_.global_object.check_first_lock:
            if self.master_.global_object.player_num is None:
                ok_send = self.send_data("you are the first player!\nHow many players? > ", with_CR=False)
                while True:
                    if not ok_send:
                        sys.exit(0)
                    ok_recv, data = self.recv_data()
                    if not ok_recv:
                        sys.exit(0)
                    if data.isdigit() and int(data) > 0:
                        num = int(data)
                        self.master_.global_object.player_num = num
                        ok_send = self.send_data(f"Thank you, please wait for {num} players ready...\n")
                        break
                    else:
                        ok_send = self.send_data("please enter positive digit number\nHow many players? > ", with_CR=False)


    def ask_name(self):
        ok_send = self.send_data("enter your name > ", with_CR=False)
        while True:
            if not ok_send:
                sys.exit(0)
            ok_recv, data = self.recv_data()
            if not ok_recv:
                ok_send = self.send_data("some error occured, enter again > ", with_CR=False)
                continue # もう一回

            name_ = data
            success = self.master_.new_player(name_, self) # すでに登録されているかを確認していろいろ
            if not success:
                ok_send = self.send_data(f"{name_} is not available. please use another\nenter your name > ", with_CR=False)
                continue # もう一回

            ok_send = self.send_data(f"Thank you, {name_}! please wait for game to begin...\n")
            break

        


    def select_role(self):
        self.master_.global_object.event_players_role_select.wait()

        self.listen_broadcast = False
        role_dict_ = self.master_.global_object.roles_dict

        ok_send = self.send_data("役職選択 > ", with_CR=False)
        while True:
            if not ok_send:
                sys.exit(0)
            ok_recv, data = self.recv_data()
            if not ok_recv:
                sys.exit(0)
            if data.isdigit() and (int(data) in role_dict_.keys()):
                role_ = getattr(classes.roles, role_dict_[int(data)]).player_instance(self.player_name, self, self.master_)
                self.role = role_
                self.listen_broadcast = True
                self.master_.wait_answer_done()
                ok_send = self.send_data(f"受理しました, あなたは {role_.role_name} です.\n")
                break
            else:
                ok_send = self.send_data("役職の番号を入力してください.\n役職選択 > ", with_CR=False)


        # self.listen_broadcast = True 上に移動
        self.master_.global_object.event_players_role_select.wait() # 他のスレッドの終了待ち

    
    def vote_user(self):
        p_dict = self.master_.alive_players_dict()
        # 問い合わせ
        ok_send = self.send_data("投票 > ", with_CR=False)
        while True:
            if not ok_send:
                sys.exit(0)
            ok_recv, data = self.recv_data()
            if not ok_recv:
                sys.exit(0)
            if data.isdigit() and (int(data) in p_dict.keys()):
                voted_player = p_dict[int(data)]
                self.master_.submit_answer(submit_type="vote", user=voted_player)
                ok_send = self.send_data(f"{p_dict[int(data)]} に投票しました.\n")
                return
            else:
                ok_send = self.send_data("プレーヤーの番号を入力してください.\n投票 > ", with_CR=False)

    def set_not_alive(self):
        self.alive = False
        self.send_data("死んでしましました.\nもう生きてはいませんが、引き続き様子を見守りましょう")
        # ここで、役職公開とかもあり.


    def run(self):
        self.initialize()

        if self.check_start():
            self.socket.close()
            return

        self.check_first()
        self.ask_name()

        self.listen_broadcast = True

        self.master_.global_object.event_players_ready.wait()

        # ok_send = self.send_data("custom: start")

        self.select_role()

        self.master_.global_object.event_wait_next.wait()
        ########################

        # 0日目の処理 -> 初夜も夜中の知識/行動をする
        self.send_data("player: 0 day")
        self.role.get_knowledge(TIME_OF_DAY.ZERO)
        self.role.take_action(TIME_OF_DAY.ZERO)
        self.role.get_knowledge(TIME_OF_DAY.MIDNIGHT)
        self.role.take_action(TIME_OF_DAY.MIDNIGHT)
        self.master_.wait_answer_done() # 終了通知
        
        self.master_.global_object.event_wait_next.wait() # 次の段階待ち
        ########################

        while not self.master_.global_object.end_flag:
            ## 朝
            self.send_data(f"player: {self.master_.global_object.day} day morning")
            if self.alive:
                self.role.get_knowledge(TIME_OF_DAY.MORNING)
                self.role.take_action(TIME_OF_DAY.MORNING)
                self.master_.wait_answer_done()

            self.master_.global_object.event_wait_next.wait() # 次の段階待ち
            ########################

            ## 昼
            if self.end_flag:
                break
            self.send_data(f"player: {self.master_.global_object.day} day daytime")
            # 知識を与える: 死んだ人 (共通) -> master.broadcast

            # 行動: 投票 (共通)
            if self.alive:
                self.vote_user()

                self.master_.wait_answer_done()
            self.master_.global_object.event_wait_next.wait() # 次の段階待ち
            ########################


            ## 夜
            if self.end_flag:
                break
            self.send_data(f"player: {self.master_.global_object.day} day midnight")
            if self.alive:
                self.role.get_knowledge(TIME_OF_DAY.MIDNIGHT)
                self.role.take_action(TIME_OF_DAY.MIDNIGHT)
                self.master_.wait_answer_done()

            self.master_.global_object.event_wait_next.wait() # 次の段階待ち
            ########################



        _ = self.send_data(f"thank you, {self.player_name}! see you!\n")

        # while True:
        #     ok_recv, data = self.recv_data()
        #     if not ok_recv:
        #         break

        #     ok_send = self.send_data(data)
        #     if not ok_send:
        #         break
        
        self.socket.close()

