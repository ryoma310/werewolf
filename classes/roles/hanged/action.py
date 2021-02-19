from classes.abst_classes.action_abst import Action_AbstClass
from classes.util import TIME_OF_DAY, ROLES
import sys

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
        # # 疑う対象の一覧を取得
        # p_dict = self.master_.alive_players_dict()
        # # 選択肢をbroadcast
        # p_dict_str = "\n".join([ f"{k}: {v}" for k, v in p_dict.items()])
        # self.player_.send_data("suspect user:\n" + p_dict_str + "\n")

        # # 疑う
        # p_dict = self.master_.alive_players_dict()
        # # 問い合わせ
        # ok_send = self.player_.send_data("suspect > ", with_CR=False)
        # while True:
        #     if not ok_send:
        #         sys.exit(0)
        #     ok_recv, data = self.player_.recv_data()
        #     if not ok_recv:
        #         sys.exit(0)
        #     if data.isdigit() and (int(data) in p_dict.keys()):
        #         suspected_player = p_dict[int(data)]
        #         self.master_.submit_answer(submit_type="suspect", user=suspected_player) # 選択を登録
        #         ok_send = self.player_.send_data(f"suspect {p_dict[int(data)]}\n")
        #         return
        #     else:
        #         ok_send = self.player_.send_data("please enter player number\nsuspect > ", with_CR=False)
        pass



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
        # 疑う対象の一覧を取得
        p_dict = self.master_.alive_players_dict()
        # 選択肢をbroadcast
        p_dict_str = "\n".join([f"{k}: {v}" for k, v in p_dict.items()])
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
                self.master_.submit_answer(submit_type="suspect", user=suspected_player) # 選択を登録
                ok_send = self.player_.send_data(f"suspect {p_dict[int(data)]}\n")
                return
            else:
                ok_send = self.player_.send_data("please enter player number\nsuspect > ", with_CR=False)



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
