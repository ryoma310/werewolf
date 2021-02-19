from threading import Thread, Event
import time
import threading
import statistics
import random
from collections import defaultdict
from typing import Dict, List

from .player import PlayerThread
import classes.roles
from classes.util import WIN_STATUS, WIN_CONDITION, FINISH_TRIGER, ROLES, HANGED_WIN_DATE


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
            ROLES.ALL_ROLES)}
        self.players_alive: List[PlayerThread] = []
        self.vote_list: [str] = []
        self.suspect_list: [str] = []
        self.guard_dict: defaultdict = defaultdict(str)
        self.bake_dict: defaultdict = defaultdict(str)
        self.attack_target: defaultdict = defaultdict(int)
        self.fortune_dict: defaultdict = defaultdict(str)
        self.magician_dict: defaultdict = defaultdict(str)
        self.cupid_dict: defaultdict = defaultdict(str)
        self.cupid_lovers_dict: defaultdict = defaultdict(str)
        self.finish_condition: WIN_STATUS = WIN_STATUS()
        self.check_username_lock = threading.RLock()
        self.voted_user = None
        self.magic_target = None
        # self.fortune_dict: defaultdict = defaultdict(str)
        # self.guard_user = None #佐古追加、騎士がサイコキラーを守ったかの判別 騎士クラスは未編集
        # self.forecast_user = None #佐古追加、占い師がサイコキラーを占ったかの判別 占い師クラスは未編集
        self.submit_lock = threading.RLock()
        self.lovers_dict: defaultdict = defaultdict(list)
        self.dead_list_for_magician: [str] = []
        self.dead_log: [str] = []
        self.stealed_wolf = False


class MasterThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.global_object = GlobalObject(self)  # これを利用して何日目かとかを管理
        self.print_header = "[*] master.py:"

    def broadcast_data(self, data: str, log=True):
        for p in list(self.global_object.players.values()):
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
                    self.start_game()
                    self.broadcast_data(
                        f"{name_} joined! Now all players ready!\n")
                    
                return True

    def start_game(self):
        self.global_object.started = True
        self.global_object.event_players_ready.set()

    def end_game(self):
        self.global_object.started = False
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
        with self.global_object.submit_lock:
            if submit_type == "vote":
                self.global_object.vote_list.append(user)
            elif submit_type == "suspect":
                self.global_object.suspect_list.append(user)
            elif submit_type == "attack":
                priority = kwargs.get('priority', 1)
                self.global_object.attack_target[user] += priority
            elif submit_type == "guard":
                g, p = user.split()
                self.global_object.guard_dict[p] = g
            elif submit_type == "bake":
                b, p = user.split()
                self.global_object.bake_dict[p] = b
            elif submit_type == "cupid":
                p1 = kwargs.get('cupid1', "")
                p2 = kwargs.get('cupid2', "")
                if p1 and p2:  # 一応チェック
                    self.global_object.lovers_dict[p1].append(p2)
                    self.global_object.lovers_dict[p2].append(p1)

                self.global_object.cupid_dict[user] = [p1, p2]
                self.global_object.cupid_lovers_dict[user] = [p1, p2] # 一個にしたいなぁ
            elif submit_type == "magician":
                p, m = user.split()
                self.global_object.magician_dict[p] = m

    def select_role(self):
        self.broadcast_data("役職一覧:\n")

        roles_dict_str = "\n".join(
            [f"{k}: {v.value}" for k, v in self.global_object.roles_dict.items()])
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
        # 成立条件: wolf > 0 and CITIZEN_SIDE > wolf
        wolfs_ = [
            p for p in self.global_object.players_alive if p.role.role_enum in ROLES.WEREWOLF_SIDE]
        citizens_ = [
            p for p in self.global_object.players_alive if p.role.role_enum in ROLES.CITIZEN_SIDE]
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

    def switch_role(self, target_player: PlayerThread, target_role: ROLES):
        new_role = getattr(classes.roles, target_role.name.lower()).player_instance(
            target_player.player_name, target_player, self)
        target_player.role = new_role

    def magician_swtich_phase(self):
        dead_list = []
        magician_list = [k for k, v in self.global_object.magician_dict.items()]  # 魔術師のリストをとってくる
        if len(magician_list) == 0:
            return
        magic_success_man = random.choice(magician_list)  # 魔術師の中から抽選
        for magician, target in self.global_object.magician_dict.items():
            if magician == magic_success_man:
                self.global_object.magic_target = target
                self.switch_role(
                    self.global_object.players[magician], self.global_object.players[target].role.role_enum)
                self.global_object.players[magician].send_data(
                    f"{target} の役職は, \"{self.global_object.players[target].role.role_name}\" でした.")
                self.global_object.players[magician].send_data(
                    f"よってあなたの役職は, \"{self.global_object.players[target].role.role_name}\" になります.")
            else: # 抽選漏れの件を伝えると仮定
                self.switch_role(
                    self.global_object.players[magician], ROLES.CITIZEN)
                self.global_object.players[magician].send_data(f"残念ながらあなたは役職を奪えませんでした.")
                self.global_object.players[magician].send_data(f"よってあなたの役職は, 市民 になります.")

        for magician, target in self.global_object.magician_dict.items():
            if magician == magic_success_man:
                target_role_enum = self.global_object.players[target].role.role_enum
                self.switch_role(self.global_object.players[target], ROLES.CITIZEN)
                werewolfs_num = len([p.player_name for p in self.global_object.players.values(
                ) if p.role.role_enum is ROLES.WEREWOLF])
                # 人狼が複数人いる場合, 魔術師が人狼を奪うと, その人狼は市民になって死ぬ
                if target_role_enum == ROLES.WEREWOLF:
                    self.global_object.stealed_wolf = True
                    if werewolfs_num >= 2:
                        self.global_object.dead_list_for_magician.append(target)
                # self.global_object.players[target].send_data(f"あなたは魔術師に役職を奪われたため \"市民\" になりました.")

    def check_fox_immoral(self):
        fox_ = [
            p for p in self.global_object.players_alive if p.role.role_enum is ROLES.FOX_SPIRIT]
        immoral_ = [
            p for p in self.global_object.players_alive if p.role.role_enum is ROLES.IMMORAL]
        if (not fox_) and (immoral_):  # foxがいなくて、immoralがいる
            to_fox_user = random.choice(immoral_)
            self.switch_role(to_fox_user, ROLES.FOX_SPIRIT)
            to_fox_user.send_data("あなたは背徳者でしたが、妖狐がいなかったため、妖狐になってしまいました.")

    def vote_broadcast(self):
        self.global_object.vote_list = []  # 一応初期化
        self.global_object.voted_user = None
        # 疑う対象の一覧を取得
        p_dict = self.alive_players_dict()
        # 選択肢をbroadcast
        p_dict_str = "\n".join([f"{k}: {v}" for k, v in p_dict.items()])
        self.broadcast_data(
            "それでは, 投票したい人物を選んでください.\n選択肢:\n" + p_dict_str + "\n")

    def kill_lovers(self, name):
        dead_lovers = []
        if self.global_object.lovers_dict:
            alive_list = self.alive_players_dict().values()
            for p_name, opponents in self.global_object.lovers_dict.items():
                if name == p_name:
                    for opponent in opponents:
                        if (not opponent in dead_lovers) and opponent in alive_list:
                            dead_lovers.append(opponent)
        random.shuffle(dead_lovers)
        return dead_lovers

    def kill_immoral(self):
        fox_ = [
            p.player_name for p in self.global_object.players_alive  if p.role.role_enum is ROLES.FOX_SPIRIT]
        immoral_ = [
            p.player_name for p in self.global_object.players_alive  if p.role.role_enum is ROLES.IMMORAL]
        if (not fox_) and (immoral_):  # foxがいなくて、immoralがいる
            random.shuffle(immoral_)
            return immoral_
        return []

    def kill_chain(self, temp_dead_list):
        for dead in temp_dead_list:
            self.delete_player(dead)
        i = 0
        while i < len(temp_dead_list) and not self.check_game_finish():
            added = False
            # 背徳者
            dead_immoral = self.kill_immoral()
            for p in dead_immoral:
                if (not p in temp_dead_list):
                    self.broadcast_data(f"{p} が 妖狐の後を追って自殺しました．")
                    self.global_object.dead_log.append(
                        f"{self.global_object.day}日目:妖狐の後を追い、背徳者{p}が死亡")
                    temp_dead_list.append(p)
                    self.delete_player(p)
                    added = True
                    if self.check_game_finish():
                        return

            dead_user = temp_dead_list[i]
            # 恋人
            dead_lovers = self.kill_lovers(dead_user)
            for p in dead_lovers:
                print(p, (not p in temp_dead_list),
                      (p in self.global_object.players_alive))
                if not p in temp_dead_list:
                    self.broadcast_data(
                        f"{p} が恋人 {dead_user} を失った悲しみに耐えきれず、後追い自殺をしてしまいました..")
                    self.global_object.dead_log.append(
                        f"{self.global_object.day}日目:恋人{dead_user}の後を追い、{p}が死亡")
                    temp_dead_list.append(p)
                    self.delete_player(p)
                    added = True
                    if self.check_game_finish():
                        return

            # ハンター猫又
            if self.global_object.players[dead_user].role.role_enum == ROLES.HUNTER or self.global_object.players[dead_user].role.role_enum == ROLES.MONSTER_CAT:
                if self.global_object.players[dead_user].role.role_enum == ROLES.HUNTER:
                    self.broadcast_data(f"死亡した {dead_user} はハンターでした.")
                    killed_user = self.global_object.players[dead_user].role.hunt(
                    )
                    self.broadcast_data(
                        f"ハンターの一撃により {killed_user} が犠牲となりました.")
                    self.global_object.dead_log.append(
                        f"{self.global_object.day}日目:ハンター{dead_user}の一撃により、{killed_user}が死亡")
                else:
                    self.broadcast_data(f"死亡した {dead_user} は猫又でした．")
                    killed_user = self.global_object.players[dead_user].role.bit_explusion(
                    )
                    self.broadcast_data(f"{killed_user} が道連れになりました．")
                    self.global_object.dead_log.append(
                        f"{self.global_object.day}日目:猫又{dead_user}が{killed_user}を道連れにし、{killed_user}が死亡")
                added = True
                temp_dead_list.append(killed_user)
                self.delete_player(killed_user)
                if self.check_game_finish():
                    return
            if added:
                dead_list_str = ",".join(temp_dead_list)
                self.broadcast_data(f"今回の犠牲者一覧:\n{dead_list_str}\n")
            i += 1

    def announce_cupid(self):
        if self.global_object.lovers_dict:  # なんか登録されてたら..
            for p_name, l_s in self.global_object.lovers_dict.items():
                p = self.global_object.players[p_name]
                l_s_str = ", ".join(l_s)
                p.send_data(f"あなたは {l_s_str} と結ばれています.")

    def anounce_vote_result(self):
        top_user = statistics.multimode(
            self.global_object.vote_list)  # modeのlistを返す
        execution_user = random.choice(top_user)  # 重複があるとランダムに1人
        self.broadcast_data(f"投票の結果、{execution_user} に決定しました")
        self.global_object.dead_log.append(
            f"{self.global_object.day}日目:投票により、{execution_user}が処刑")
        if (self.global_object.players[execution_user].role.role_enum == ROLES.HANGED) and (self.global_object.day >= HANGED_WIN_DATE.hanged_win_date(self.global_object.player_num)):
            self.global_object.finish_condition.win_players_hanged.append(execution_user) # 勝ったリストに追加

        self.kill_chain([execution_user])

        self.global_object.voted_user = execution_user
        self.global_object.vote_list = []

    def anounce_suspect_result(self):
        top_user = statistics.multimode(
            self.global_object.suspect_list)  # modeのlistを返す
        suspected_user = random.choice(top_user)  # 重複があるとランダムに1人
        self.broadcast_data(f"最も強く疑われている人物は {suspected_user} です")
        self.global_object.suspect_list = []

    def anounce_attack_result(self):
        dead_list = []

        # 占い師が妖狐を占ったかの確認
        fox_fortuned_taller = [(k, v) for k, v in self.global_object.fortune_dict.items(
        ) if self.global_object.players[v].role.role_enum == ROLES.FOX_SPIRIT]
        for f, name in fox_fortuned_taller:
            if not name in dead_list:
                self.global_object.dead_log.append(
                    f"{self.global_object.day}日目:占い師{f}が妖狐{name}を占い、{name}が死亡")
                dead_list.append(name)

        # 人狼いろいろ
        max_val = max(self.global_object.attack_target.values())  # 最大値をとる
        top_user = [k for k, v in self.global_object.attack_target.items(
        ) if v == max_val]  # 最大値な人を全部取ってくる
        attacked_user = random.choice(top_user)  # 重複があるとランダムに1人

        # サイコキラーについて考える
        for k, v in self.global_object.cupid_dict.items():
            if not k in dead_list:
                will_cupid_die = False
                p1, p2 = v
                if self.global_object.players[p1].role.role_enum == ROLES.PSYCHO_KILLER:
                    will_cupid_die = True
                if self.global_object.players[p2].role.role_enum == ROLES.PSYCHO_KILLER:
                    will_cupid_die = True
                    p1, p2 = p2, p1
                if will_cupid_die:
                    dead_list.append(k)
                    self.global_object.dead_log.append(
                        f"{self.global_object.day}日目:キューピッド{k}がサイコキラー{p1}と{p2}を恋人にし、{k}が死亡")
        self.global_object.cupid_dict = defaultdict(str) # 後々、使いまわしたいなぁ

        # 騎士がサイコキラーを守っていたかどうか
        for k, v in self.global_object.guard_dict.items():
            if not k in dead_list:
                if self.global_object.players[v].role.role_enum == ROLES.PSYCHO_KILLER:
                    dead_list.append(k)
                    self.global_object.dead_log.append(
                        f"{self.global_object.day}日目:騎士{k}がサイコキラー{v}を庇い、{k}が死亡")
        # 後で使うので騎士dictはまだ初期化しない

        # 占い師がサイコキラーを占っていたかどうか
        for k, v in self.global_object.fortune_dict.items():
            if not k in dead_list:
                if self.global_object.players[v].role.role_enum == ROLES.PSYCHO_KILLER:
                    dead_list.append(k)
                    self.global_object.dead_log.append(
                        f"{self.global_object.day}日目:占い師{k}がサイコキラー{v}を占い、{k}が死亡")
        self.global_object.fortune_dict = defaultdict(str)

        # attacked_user がサイコキラーだった場合、襲撃しようとした人狼(の内一人)が返り討ちに遭う
        if self.global_object.players[attacked_user].role.role_enum == ROLES.PSYCHO_KILLER:
            revenged_wolf = self.global_object.players[attacked_user].role.revenge_wolf(
            )
            if not revenged_wolf in dead_list:
                dead_list.append(revenged_wolf)
                self.global_object.dead_log.append(
                    f"{self.global_object.day}日目:人狼{revenged_wolf}がサイコキラー{attacked_user}を襲い、{revenged_wolf}が死亡")

        # ここで、騎士の守りをチェック
        guard_list = self.global_object.guard_dict.values()
        self.global_object.attack_target = defaultdict(int)  # 初期化
        self.global_object.guard_target = []

        # マジシャンが人狼を奪って, 襲撃が無効化
        for dead_person in self.global_object.dead_list_for_magician:
            if not dead_person in dead_list:
                dead_list.append(dead_person)  # 元人狼死亡
                self.global_object.dead_log.append(
                    f"{self.global_object.day}日目:人狼{dead_person}がマジシャンに役職を奪われ、{dead_person}が死亡")
        self.global_object.dead_list_for_magician = []
        if (attacked_user not in guard_list) and (self.global_object.players[attacked_user].role.role_enum is not ROLES.FOX_SPIRIT) and (self.global_object.players[attacked_user].role.role_enum is not ROLES.PSYCHO_KILLER) and not self.global_object.stealed_wolf:
            if not attacked_user in dead_list:
                self.global_object.dead_log.append(
                    f"{self.global_object.day}日目:人狼が{attacked_user}を襲い、{attacked_user}が死亡")
                dead_list.append(attacked_user)
                if self.global_object.players[attacked_user].role.role_enum == ROLES.MONSTER_CAT or self.global_object.players[attacked_user].role.role_enum == ROLES.BLACK_CAT:
                    bitten_user = self.global_object.players[attacked_user].role.bit_attacked(
                    )
                    rolename = "黒猫"
                    if self.global_object.players[attacked_user].role.role_enum == ROLES.MONSTER_CAT:
                        rolename = "猫又"
                    if not bitten_user in dead_list:
                        self.global_object.dead_log.append(
                            f"{self.global_object.day}日目:瀕死の{rolename}{attacked_user}が{bitten_user}を道連れにし、{bitten_user}が死亡")
                        dead_list.append(bitten_user)

        dead_list_str = "いません"
        if len(dead_list) > 0:
            random.shuffle(dead_list)
            dead_list_str = ",".join(dead_list)
        self.broadcast_data(f"昨晩の犠牲者は {dead_list_str} でした.")

        self.kill_chain(dead_list)

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
            if len(alived_baker_bread) > 0:
                self.broadcast_data(
                    f"今日は パン屋の方から {random.choice(alived_baker_bread)} が 皆さんの手元に届けられました！")
            else:
                self.broadcast_data(f"パンは 届きませんでした…")

        # print(self.global_object.players_alive)
    

    def check_cuples_alive(self):
        p_set = set([p.player_name for p in self.global_object.players_alive])
        alive_cuples = dict()
        for c, l in self.global_object.cupid_lovers_dict.items():
            if set(l) <= p_set:
                alive_cuples[c] = l
        return alive_cuples # returns alive {"cupid": [p1,p2], "cupid2": [p3,p4], }

    def announce_magician_result(self):
        target = self.global_object.magic_target
        if self.global_object.day == 1 and target and self.global_object.players[target].alive:
            self.global_object.players[target].send_data("あなたは役職を奪われた為, \"市民\" になりました.\n")


    def check_game_finish(self):
        wolf_side_ = [
            p for p in self.global_object.players_alive if p.role.role_enum in ROLES.WEREWOLF_SIDE] # only WOLF
        citizen_side_ = [
            p for p in self.global_object.players_alive if p.role.role_enum in ROLES.CITIZEN_SIDE] # CITIZEN, FORTUNE_TELLER, etc...
        third_force_ = [
            p for p in self.global_object.players_alive if p.role.role_enum in ROLES.THIRD_FORCE_SIDE] # only FOX_SPIRIT
        alive_cuples = self.check_cuples_alive() # returns alive {"cupid": [p1,p2], "cupid2": [p3,p4], }
        lovers_set = set(self.global_object.lovers_dict.keys())

        # このあと、勝者をリストかなんかに入れておいて、後で全体/個人アナウンスで利用
        # self.global_object.finish_condition.win_playersに入れる
        if len(wolf_side_) == 0:  # 全ての人狼が追放
            self.global_object.finish_condition.finish = True
            self.global_object.finish_condition.finish_triger = FINISH_TRIGER.NO_WOLFS
            if alive_cuples: # 恋人いた -> 生きている [(キューピット,恋人1,恋人2), ..] の勝利
                self.global_object.finish_condition.finish_type = WIN_CONDITION.CUPIT_CUPLE
                # 勝者を記録
                for k, v in alive_cuples.items():
                    self.global_object.finish_condition.win_players.append(k)
                    self.global_object.finish_condition.win_players.append(v[0])
                    self.global_object.finish_condition.win_players.append(v[1])
            elif third_force_:  # 妖狐いた -> 妖狐,背徳者の勝利
                self.global_object.finish_condition.finish_type = WIN_CONDITION.THIRD_FORCE
                winners_ = [p.player_name for p in self.global_object.players.values() if (p.role.role_enum in ROLES.THIRD_FORCE_SIDE_WINNER) and (p.player_name not in lovers_set)]
                self.global_object.finish_condition.win_players = winners_
            else:  # 恋人も妖狐いない
                self.global_object.finish_condition.finish_type = WIN_CONDITION.NO_WOLFS
                winners_ = [p.player_name for p in self.global_object.players.values() if (p.role.role_enum in ROLES.CITIZEN_SIDE_WINNER)  and (p.player_name not in lovers_set)]
                self.global_object.finish_condition.win_players = winners_

            return True

        elif len(wolf_side_) >= len(citizen_side_):  # 市民が人狼以下
            self.global_object.finish_condition.finish = True
            self.global_object.finish_condition.finish_triger = FINISH_TRIGER.WOLF_EQ_OR_MORE_THAN_CITIZEN
            if alive_cuples: # 恋人いた -> 生きている [(キューピット,恋人1,恋人2), ..] の勝利
                self.global_object.finish_condition.finish_type = WIN_CONDITION.CUPIT_CUPLE
                # 勝者を記録
                for k, v in alive_cuples.items():
                    self.global_object.finish_condition.win_players.append(k)
                    self.global_object.finish_condition.win_players.append(v[0])
                    self.global_object.finish_condition.win_players.append(v[1])
            elif third_force_:  # 妖狐いた -> 妖狐,背徳者の勝利
                self.global_object.finish_condition.finish_type = WIN_CONDITION.THIRD_FORCE
                winners_ = [p.player_name for p in self.global_object.players.values() if (p.role.role_enum in ROLES.THIRD_FORCE_SIDE_WINNER) and (p.player_name not in lovers_set)]
                self.global_object.finish_condition.win_players = winners_
            else:  # 恋人も妖狐いない
                self.global_object.finish_condition.finish_type = WIN_CONDITION.WOLF_EQ_OR_MORE_THAN_CITIZEN
                winners_ = [p.player_name for p in self.global_object.players.values() if (p.role.role_enum in ROLES.WEREWOLF_SIDE_WINNER) and (p.player_name not in lovers_set)]
                self.global_object.finish_condition.win_players = winners_
            return True

        return False

    def finish_statement(self):
        # 終了トリガのアナウンス
        if self.global_object.finish_condition.finish_triger == FINISH_TRIGER.NO_WOLFS:
            self.broadcast_data("この村から全ての人狼が追放されました\n")
        elif self.global_object.finish_condition.finish_triger == FINISH_TRIGER.NO_WOLFS:
            self.broadcast_data("この村の市民と人狼が同数となりました\n")
        else:
            pass # 上のどっちかのはず.

        # 勝者の報告
        # 市民勝利
        if self.global_object.finish_condition.finish_type == WIN_CONDITION.NO_WOLFS:
            self.broadcast_data("よって、市民陣営の勝利です!\n")
        # 人狼勝利
        elif self.global_object.finish_condition.finish_type == WIN_CONDITION.WOLF_EQ_OR_MORE_THAN_CITIZEN:
            self.broadcast_data("よって、人狼陣営の勝利です!\n")
        # 妖狐の勝利
        elif self.global_object.finish_condition.finish_type == WIN_CONDITION.THIRD_FORCE:
            if self.global_object.finish_condition.finish_triger == FINISH_TRIGER.NO_WOLFS:
                self.broadcast_data("市民陣営の勝利...かと思われましたが、")
            elif self.global_object.finish_condition.finish_triger == FINISH_TRIGER.NO_WOLFS:
                self.broadcast_data("人狼陣営の勝利...かと思われましたが、")
            else:
                pass # 上のどっちかのはず.
            self.broadcast_data("ここで、妖狐が現れました!\よって、妖狐陣営の勝利です!\n")

        # 恋人たちの勝利
        elif self.global_object.finish_condition.finish_type == WIN_CONDITION.CUPIT_CUPLE:
            if self.global_object.finish_condition.finish_triger == FINISH_TRIGER.NO_WOLFS:
                self.broadcast_data("市民陣営の勝利...かと思われましたが、")
            elif self.global_object.finish_condition.finish_triger == FINISH_TRIGER.NO_WOLFS:
                self.broadcast_data("人狼陣営の勝利...かと思われましたが、")
            else:
                pass # 上のどっちかのはず.
            cuplies_dict_ = self.check_cuples_alive()
            s_ = ", ".join([f"{c}の結びつけた{l[0]}-{l[1]}" for c, l in cuplies_dict_.items()])
            self.broadcast_data(f"恋人が生き残っていました!\nよって、{s_} たちの勝利です!\n")
        else:
            pass

        # この後追加でてるてるの確認
        if self.global_object.finish_condition.win_players_hanged:
            p_str = ", ".join(self.global_object.finish_condition.win_players_hanged)
            self.broadcast_data(f"また、{HANGED_WIN_DATE.hanged_win_date(self.global_object.player_num)}日以降に吊られた てるてる の {p_str} も勝利となります!\n")

        
        # 勝者一覧のbroadcast
        game_winners_ = self.global_object.finish_condition.win_players
        game_winners_ += self.global_object.finish_condition.win_players_hanged
        game_winners_str = '\n'.join(game_winners_)
        self.broadcast_data(f"\n########## 勝者たち ##########\n{game_winners_str}\n")



    def show_roles(self):
        players_ = self.global_object.players
        players_role_dict = {
            name: p.role.role_name for name, p in players_.items()}
        p_r_dict_sorted = sorted(players_role_dict.items(), key=lambda x: x[1])
        p_r_dict_sorted_str = "\n".join(
            [f"{p_role}: {p_name}" for p_name, p_role in p_r_dict_sorted])
        self.broadcast_data("役職は以下の通りでした.\n" + p_r_dict_sorted_str)

    def show_alive_players(self):
        p_dict = self.alive_players_dict()
        p_dict_str = "\n".join(
            [f"{str(pid)}:{name}"for pid, name in p_dict.items()])
        self.broadcast_data("現在の生存者\n" + p_dict_str)

    def show_dead_logs(self):
        self.broadcast_data("\n今回の死亡原因一覧:")
        for log in self.global_object.dead_log:
            self.broadcast_data(log)

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

            self.check_fox_immoral()

            # 0日目の処理
            self.broadcast_data(f"\n---------- 恐ろしい夜がやってきました ----------\n")
            print(self.print_header, "0 day")
            self.global_object.suspect_list = []  # 村人疑う用配列の初期化
            self.global_object.event_wait_next.set()
            self.global_object.event_wait_next.clear()

            self.wait_answer_start()

            self.announce_cupid()

            self.magician_swtich_phase()

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

                self.show_alive_players()

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
                self.announce_magician_result() # 魔術師が役職を奪った旨を当事者に通知
                self.global_object.suspect_list = []  # 市民疑う用配列の初期化
                self.global_object.attack_target = defaultdict(
                    int)  # 人狼襲撃用配列の初期化
                self.global_object.fortune_dict = {}
                self.global_object.magician_dict = {}
                self.global_object.event_wait_next.set()
                self.global_object.event_wait_next.clear()

                self.wait_answer_start()

        self.show_roles()
        self.show_dead_logs()

        self.broadcast_data("---------- game end! ----------\n")
        self.end_game()
        self.global_object.event_wait_next.set()
