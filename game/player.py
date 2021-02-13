from threading import Thread
import socket
import sys
import errno
import threading

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
    

    def initialize(self):
        self._id = threading.get_ident()
        self.print_header = f"[*] player.py ({self._id}):"


    def recv_data(self):
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
        try:
            self.socket.send(data.encode() + (b"\n" if with_CR else b""))
        except InterruptedError as e:
            print(self.print_header, "send error:", e)
            return False
        return True


    def check_start(self):
        # TODO ユーザ名で再接続処理
        if self.master_.global_object.started:
            ok_send = self.send_data("the game has already started, please wait and reconnect in next game.")
            return True
        else:
            return False
            

    def check_first(self):
        with self.master_.global_object.check_first_lock:　#TODO ちゃんと他の人が設定中なんで待ってねって言ったほうが親切か.
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
            else:
                name_ = data
                self.player_name = name_
                ok_send = self.send_data(f"Thank you, {name_}! please wait for game to begin...\n")
                break

        self.master_.new_player(self)


    def run(self):
        self.initialize()

        if self.check_start():
            self.socket.close()
            return

        self.check_first()
        self.ask_name()

        self.listen_broadcast = True

        self.master_.global_object.event_players_ready.wait()

        ok_send = self.send_data("custom: start")

        while not self.master_.global_object.end_flag:
            pass

        _ = self.send_data(f"thank you, {self.player_name}! see you!\n")

        # while True:
        #     ok_recv, data = self.recv_data()
        #     if not ok_recv:
        #         break

        #     ok_send = self.send_data(data)
        #     if not ok_send:
        #         break
        
        self.socket.close()

