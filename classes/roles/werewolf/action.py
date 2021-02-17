from classes.abst_classes.action_abst import Action_AbstClass
from classes.util import TIME_OF_DAY


######################################################################
"""
message: property
    action時の初回メッセージを想定
select: method
    actionに対する選択などのやりとりを想定
"""
# ここから下をいじる
class _ZERO(Action_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def action(self):
        # 誰を襲撃しようとしたかを初期化
        self.player_.role.try_attack = None
        # 疑う対象の一覧を取得
        p_dict = self.master_.alive_players_dict()
        # 選択肢をbroadcast
        p_dict_str = "\n".join([ f"{k}: {v}" for k, v in p_dict.items()])
        self.player_.send_data("suspect user:\n" + p_dict_str + "\n")

        # 疑う
        p_dict = self.master_.alive_players_dict()
        # 問い合わせ
        ok_send = self.player_.send_data("suspect > ", with_CR=False)
        while True:
            if not ok_send:
                sys.exit(0)
            ok_recv, data = self.player_.recv_data()
            if not ok_recv:
                sys.exit(0)
            if data.isdigit() and (int(data) in p_dict.keys()):
                suspected_player = p_dict[int(data)]
                self.player_.role.try_attack = suspected_player # 誰を襲撃しようとした人物を保存
                self.master_.submit_answer(submit_type="suspect", user=suspected_player) # 選択を登録
                ok_send = self.player_.send_data(f"suspect {p_dict[int(data)]}\n")
                return
            else:
                ok_send = self.player_.send_data("please enter player number\nsuspect > ", with_CR=False)


class _MORNING(Action_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def action(self):
        pass


class _DAYTIME(Action_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def action(self):
        # 投票
        pass


class _MIDNIGHT(Action_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def action(self):
        # 襲撃対象の一覧を取得
        p_list = [p.player_name for p in self.master_.global_object.players_alive] # 循環importのため無理矢理 type(self.player_.role)はwolfのはず
        p_dict = {i:n for i, n in enumerate(p_list)}
        # 選択肢を送信
        p_dict_str = "\n".join([ f"{k}: {v}" for k, v in p_dict.items()])
        self.player_.send_data("attack user:\n" + p_dict_str + "\n")

        # 問い合わせ (誰を?)
        ok_send = self.player_.send_data("attack > ", with_CR=False)
        while True:
            if not ok_send:
                sys.exit(0)
            ok_recv, data = self.player_.recv_data()
            if not ok_recv:
                sys.exit(0)
            if data.isdigit() and (int(data) in p_dict.keys()):
                attack_player = p_dict[int(data)]
                # self.master_.submit_answer(submit_type="attack", user=attack_player) # 選択を登録
                # ok_send = self.player_.send_data(f"attack {p_dict[int(data)]}\n")
                break
            else:
                ok_send = self.player_.send_data("please enter player number\nattack > ", with_CR=False)
        
        # 問い合わせ (どのくらい?)
        ok_send = self.player_.send_data("どのくらい襲撃したいですか? (1:普通, 2:わりと, 3:絶対)\n> ", with_CR=False)
        while True:
            if not ok_send:
                sys.exit(0)
            ok_recv, data = self.player_.recv_data()
            if not ok_recv:
                sys.exit(0)
            if data.isdigit() and (int(data) in [1, 2, 3]):
                priority_ = int(data)
                self.master_.submit_answer(submit_type="attack", user=attack_player, priority=priority_) # 選択を登録
                ok_send = self.player_.send_data(f"submit: {attack_player}を優先度{priority_}で襲撃\n")
                return
            else:
                ok_send = self.player_.send_data("1,2,3を入力してください!\n> ", with_CR=False)



# ここまで
######################################################################
class Action:
    def __init__(self, player_, master_):
        zero = _ZERO(player_, master_)
        morning = _MORNING(player_, master_)
        daytime = _DAYTIME(player_, master_)
        midnight = _MIDNIGHT(player_, master_)
        self.action_dict: Dict[TIME_OF_DAY, Action_AbstClass] = {
            TIME_OF_DAY.ZERO: zero,
            TIME_OF_DAY.MORNING: morning,
            TIME_OF_DAY.DAYTIME: daytime,
            TIME_OF_DAY.MIDNIGHT: midnight
        }
