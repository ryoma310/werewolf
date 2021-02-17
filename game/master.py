from threading import Thread, Event
import time
import threading
import statistics
import random
from collections import defaultdict

from .player import PlayerThread
import classes.roles
from classes.util import WIN_CONDITION, ROLES


class GlobalObject:
    def __init__(self, master):
        self.master: MasterThread = master
        self.players:  Dict[str, PlayerThread] = {}
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
        self.roles_dict = {i: r for i, r in enumerate(
            classes.roles.role_list())}
        self.players_alive: list[PlayerThread] = []
        self.vote_list: [str] = []
        self.suspect_list: [str] = []
        self.guard_list: [str] = []
        self.bake_dict: defaultdict = defaultdict(str)
        self.attack_target: defaultdict = defaultdict(int)
        self.finish_condition: WIN_CONDITION = None
        self.check_username_lock = threading.RLock()
        self.voted_user = None


class MasterThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.global_object = GlobalObject(self)  # これを利用して何日目かとかを管理
        self.print_header = "[*] master.py:"

    def broadcast_data(self, data: str, log=True):
        for p in self.global_object.players.values():
            if p.listen_broadcast:
                p.send_data(data)
                p.log += data + "\n"

    def new_player(self, name: str, player_: PlayerThread):
        with self.global_object.check_username_lock:
            if name in self.global_object.players.keys():
                return False
            else:
                player_.player_name = name
                self.global_object.players[name] = player_
                self.global_object.players_alive.append(player_)
                name_ = player_.player_name
                ready_num = len(self.global_object.players)

                if ready_num < self.global_object.player_num:
                    self.broadcast_data(
                        f"{name_} joined! Now {ready_num}/{self.global_object.player_num} players ready, please wait all players ready...\n")
                else:
                    self.broadcast_data(
                        f"{name_} joined! Now all players ready!\n")
                    self.start_game()
                return True

    def start_game(self):
        self.started = True
        self.global_object.event_players_ready.set()

    def end_game(self):
        self.started = False
        self.global_object.end_flag = True
        for p in self.global_object.players.values():
            p.end_flag = True

    def wait_answer_start(self):
        self.global_object.event_wait_answer.clear()
        self.global_object.wait_answer_count = 0
        self.global_object.event_wait_answer.wait()

    def wait_answer_done(self):
        with self.global_object.wait_answer_lock:
            self.global_object.wait_answer_count += 1

        print(self.print_header,
              f"answer: {self.global_object.wait_answer_count}/{len(self.global_object.players_alive)}")
        if self.global_object.wait_answer_count < len(self.global_object.players_alive):
            pass
        else:
            self.global_object.event_wait_answer.set()

    def submit_answer(self, submit_type, user, **kwargs):
        if submit_type == "vote":
            self.global_object.vote_list.append(user)
        elif submit_type == "suspect":
            self.global_object.suspect_list.append(user)
        elif submit_type == "attack":
            priority = kwargs.get('priority', 1)
            self.global_object.attack_target[user] += priority
        elif submit_type == "guard":
            self.global_object.guard_list.append(user)
        elif submit_type == "bake":
            b, p = user.split()
            self.global_object.bake_dict[p] = b

    def select_role(self):
        self.broadcast_data("役職一覧:\n")

        roles_dict_str = "\n".join(
            [f"{k}: {v}" for k, v in self.global_object.roles_dict.items()])
        self.broadcast_data(roles_dict_str + "\n")
        self.global_object.event_players_role_select.set()  # playerスレッドにroleの選択を開始させる

        self.wait_answer_start()  # playerスレッドの処理終了を待つ

    def delete_player(self, user_name):
        found = next(
            (p for p in self.global_object.players_alive if p.player_name == user_name), None)
        if found:
            self.global_object.players_alive.remove(found)
            found.set_not_alive()

    def validate_game_condition(self):
        # 成立条件: wolf > 0 and villager > wolf
        # TODO: 変更
        wolfs_ = [
            p for p in self.global_object.players_alive if p.role.role_enum is ROLES.WEREWOLF]
        citizens_ = [
            p for p in self.global_object.players_alive if p.role.role_enum is not ROLES.WEREWOLF]  # TODO: 変更
        return True if (len(wolfs_) > 0) and (len(citizens_) > len(wolfs_)) else False

    def alive_players_dict(self):
        alives = self.global_object.players_alive
        return {i: p.player_name for i, p in enumerate(alives)}

    def bread_dict(self):
        random_bread = ["フライパン🍳", "パンツ", "チュロス",
                        "メロンパン", "ショートケーキ🍰", "ピザ", "チョココロネ", "ドーナツ🍩", "サンドウィッチ🥪"]
        default_bread = ["食パン🍞", "クロワッサン🥐", "ベーグル🥯",
                         "フランスパン🥖"] + random.sample(random_bread, 2)
        return {i: p for i, p in enumerate(default_bread)}

    def vote_broadcast(self):
        self.global_object.vote_list = []  # 一応初期化
        self.global_object.voted_user = None
        # 疑う対象の一覧を取得
        p_dict = self.alive_players_dict()
        # 選択肢をbroadcast
        p_dict_str = "\n".join([f"{k}: {v}" for k, v in p_dict.items()])
        self.broadcast_data(
            "それでは, 投票したい人物を選んでください.\n選択肢:\n" + p_dict_str + "\n")

    def anounce_vote_result(self):
        top_user = statistics.multimode(
            self.global_object.vote_list)  # modeのlistを返す
        execution_user = random.choice(top_user)  # 重複があるとランダムに1人
        self.broadcast_data(f"投票の結果、{execution_user} に決定しました")
        self.delete_player(execution_user)  # player_aliveから消す
        # ゲーム終了条件を満たしているのか？
        if self.check_game_finish():
            return
        while self.global_object.players[execution_user].role.role_enum == ROLES.HUNTER or self.global_object.players[execution_user].role.role_enum == ROLES.MONSTER_CAT:
            if self.global_object.players[execution_user].role.role_enum == ROLES.HUNTER:
                self.broadcast_data(f"しかし {execution_user} はハンターでした.")
                execution_user = self.global_object.players[execution_user].role.hunt(
                )
                self.broadcast_data(f"ハンターの一撃により {execution_user} が犠牲となりました.")
                # attacked_users.append(attacked_user)
                self.delete_player(execution_user)  # player_aliveから消す
            else:
                execution_user = self.global_object.players[execution_user].role.bit_explusion(
                )
                self.broadcast_data(f"{execution_user} が道連れになりました．")
                self.delete_player(execution_user)
            # ゲーム終了条件を満たしているのか？
            if self.check_game_finish():
                return
        """
        if self.global_object.players[execution_user].role.role_enum == ROLES.MONSTER_CAT:
            execution_user = self.global_object.players[attacked_user].role.bit_explusion()
            self.broadcast_data(f"{execution_user} が道連れになりました．")
            self.delete_player(execution_user)  # player_aliveから消す
            if self.check_game_finish(): return
            while self.global_object.players[execution_user].role.role_enum == ROLES.HUNTER:
                self.broadcast_data(f"しかし {execution_user} はハンターでした.")
                execution_user = self.global_object.players[execution_user].role.hunt()
                self.broadcast_data(f"ハンターの一撃により {execution_user} が犠牲となりました.")
                self.delete_player(execution_user)
                if self.check_game_finish(): return
        """
        self.global_object.voted_user = execution_user
        self.global_object.vote_list = []

    def anounce_suspect_result(self):
        top_user = statistics.multimode(
            self.global_object.suspect_list)  # modeのlistを返す
        suspected_user = random.choice(top_user)  # 重複があるとランダムに1人
        self.broadcast_data(f"最も強く疑われている人物は {suspected_user} です")
        self.global_object.suspect_list = []

    def anounce_attack_result(self):
        max_val = max(self.global_object.attack_target.values())  # 最大値をとる
        top_user = [k for k, v in self.global_object.attack_target.items(
        ) if v == max_val]  # 最大値な人を全部取ってくる
        attacked_user = random.choice(top_user)  # 重複があるとランダムに1人
        # ここで、騎士の守りをチェック
        if attacked_user not in self.global_object.guard_list:
            self.broadcast_data(f"昨晩の犠牲者は {attacked_user} でした.")
            #attacked_users = []
            # attacked_users.append(attacked_user)
            self.delete_player(attacked_user)  # player_aliveから消す
            # ゲーム終了条件を満たしているのか？
            if self.check_game_finish():
                return
            # or self.global_object.players[execution_user].role.role_enum == ROLES.MONSTER_CAT:
            while self.global_object.players[attacked_user].role.role_enum == ROLES.HUNTER:
                if self.global_object.players[attacked_user].role.role_enum == ROLES.HUNTER:
                    self.broadcast_data(f"しかし {attacked_user} はハンターでした.")
                    attacked_user = self.global_object.players[attacked_user].role.hunt(
                    )

                    self.broadcast_data(
                        f"ハンターの一撃により {attacked_user} が犠牲となりました.")
                    # attacked_users.append(attacked_user)
                    self.delete_player(attacked_user)  # player_aliveから消す
                else:
                    attacked_user = self.global_object.players[attacked_user].role.bit_attacked(
                    )
                    self.broadcast_data(f"{attacked_user} が道連れになりました．")
                    self.delete_player(attacked_user)  # player_aliveから消す
                # ゲーム終了条件を満たしているのか？
                if self.check_game_finish():
                    return
            # for atk in attacked_users: self.delete_player(atk)  # player_aliveから消す
            # if self.global_object.players[execution_user].role.role_enum == ROLES.MONSTER_CAT:
            #     pass
            # bit_attacked
        else:
            self.broadcast_data(f"昨晩の犠牲者は いません でした.")
        self.global_object.attack_target = defaultdict(int)  # 初期化
        self.global_object.guard_target = []

    def anounce_bread_result(self):
        bakers_ = [
            p for p in self.global_object.players_alive if p.role.role_enum is ROLES.BAKER]
        if len(bakers_) != 0:
            alived_baker_bread = []
            # 愚直にまわす
            for pname, b in self.global_object.bake_dict.items():
                for p in self.global_object.players_alive:
                    if p.player_name == pname:
                        alived_baker_bread.append(b)
            print(alived_baker_bread)
            if len(alived_baker_bread) > 0:
                self.broadcast_data(
                    f"今日は {random.choice(alived_baker_bread)} が 皆さんの手元に届けられました！")
            else:
                self.broadcast_data(f"パンは 届きませんでした…")

        # print(self.global_object.players_alive)

    def check_game_finish(self):
        # TODO: 後で変更
        wolfs_ = [
            p for p in self.global_object.players_alive if p.role.role_enum is ROLES.WEREWOLF]
        # TODO: 後で変更
        not_wolfs_ = [
            p for p in self.global_object.players_alive if p.role.role_enum is not ROLES.WEREWOLF]
        if len(wolfs_) == 0:  # 全ての人狼が追放
            self.global_object.finish_condition = WIN_CONDITION.NO_WOLFS
            return True
        elif len(wolfs_) >= len(not_wolfs_):  # 市民が人狼以下
            self.global_object.finish_condition = WIN_CONDITION.WOLF_EQ_OR_MORE_THAN_CITIZEN
            return True
        return False

    def finish_statement(self):
        if self.global_object.finish_condition == WIN_CONDITION.NO_WOLFS:
            self.broadcast_data("この村から全ての人狼が追放されました")
            self.broadcast_data("よって、市民陣営の勝利です！\n")

        elif self.global_object.finish_condition == WIN_CONDITION.WOLF_EQ_OR_MORE_THAN_CITIZEN:
            self.broadcast_data("この村の市民と人狼が同数となりました")
            self.broadcast_data("よって、人狼陣営の勝利です！\n")

    def show_roles(self):
        players_ = self.global_object.players
        players_role_dict = {
            name: p.role.role_name for name, p in players_.items()}
        p_r_dict_sorted = sorted(players_role_dict.items(), key=lambda x: x[1])
        p_r_dict_sorted_str = "\n".join(
            [f"{p_role}: {p_name}" for p_name, p_role in p_r_dict_sorted])
        self.broadcast_data("役職は以下の通りでした.\n" + p_r_dict_sorted_str)

    def calc_discuss_time(self) -> (str, int):
        # returns ("xx分", その秒数)
        day_ = self.global_object.day

        return "5秒", 5

    def run(self):
        # ここでゲームを展開
        self.global_object.event_players_ready.wait()

        self.broadcast_data("\n########## game start! ##########\n")

        self.select_role()

        self.broadcast_data("プレイヤー全員の役職選択が完了しました.")

        if not self.validate_game_condition():
            self.end_game()
            self.broadcast_data("役職選択の結果、このゲームは成立しませんでした.")
        else:
            # 以降ゲームが成立する場合、実施
            self.broadcast_data("役職選択の結果、このゲームは成立します.")

            # 0日目の処理
            self.broadcast_data(f"\n---------- 恐ろしい夜がやってきました ----------\n")
            print(self.print_header, "0 day")
            self.global_object.suspect_list = []  # 村人疑う用配列の初期化
            self.global_object.event_wait_next.set()
            self.global_object.event_wait_next.clear()

            self.wait_answer_start()

            # ゲーム終了までループ
            game_loop_flag = True
            while game_loop_flag:
                self.global_object.day += 1
                # day日目が始まりました.
                self.broadcast_data(
                    f"\n########## {self.global_object.day}日目が始まりました ##########\n")

                ## 朝 (スレッドに指令を出す)
                self.broadcast_data(
                    f"\n------ {self.global_object.day}日目 朝 ------\n")
                self.anounce_attack_result()
                if self.check_game_finish():  # ゲーム終了判定
                    game_loop_flag = False
                    self.finish_statement()
                    break
                self.anounce_suspect_result()  # 疑うの結果報告
                self.anounce_bread_result()
                self.global_object.event_wait_next.set()
                self.global_object.event_wait_next.clear()

                self.wait_answer_start()

                ## 昼: 投票
                self.broadcast_data(
                    f"\n------ {self.global_object.day}日目 昼 ------\n")
                # 議論の時間
                discuss_time_str, discuss_time_int = self.calc_discuss_time()
                self.broadcast_data(f"議論時間は {discuss_time_str} です.")
                self.broadcast_data(f"それでは議論を開始してください")
                time.sleep(discuss_time_int)  # TODO: ここはいい感じにする. 残り時間通知とか..

                self.broadcast_data(f"\n議論終了です.")

                self.vote_broadcast()  # アナウンス
                self.global_object.event_wait_next.set()  # 投票を実施させる
                self.global_object.event_wait_next.clear()
                self.wait_answer_start()  # playerスレッドの投票終了を待つ
                self.anounce_vote_result()  # 投票結果のアナウンス
                if self.check_game_finish():  # ゲーム終了判定
                    game_loop_flag = False
                    self.finish_statement()
                    break

                ## 夜 (スレッドに指令を出す)
                # self.broadcast_data(f"\n------ {self.global_object.day}日目 夜 ------\n")
                self.broadcast_data(f"\n---------- 恐ろしい夜がやってきました ----------\n")
                self.global_object.suspect_list = []  # 市民疑う用配列の初期化
                self.global_object.attack_target = defaultdict(
                    int)  # 人狼襲撃用配列の初期化
                self.global_object.event_wait_next.set()
                self.global_object.event_wait_next.clear()

                self.wait_answer_start()

        self.show_roles()

        self.broadcast_data("---------- game end! ----------\n")
        self.end_game()
        self.global_object.event_wait_next.set()
