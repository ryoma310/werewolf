from classes.abst_classes.role_abst import Role_AbstClass
from classes.abst_classes.action_abst import Action_AbstClass
from classes.util import WIN_CONDITION, TIME_OF_DAY, ROLES

from .knowledge import Knowledge
from .action import Action

"""
values: (本当にただの変数)
    role_name (str):    役職名
    player_name (str):  名前
    log (str):          これまでの送信ログをためておく

functions: (といいつつannotationでpropertyなものも)
    win_condition() -> WIN_CONDITION:   勝利条件
    zero_day() -> None:                 0日目の行動, 未実装
    actions(TIME_OF_DAY) -> None:       朝,昼,晩の行動
    knowledges(TIME_OF_DAY) -> str:     朝,昼,晩に得られる知識
"""

class Hunter_Role(Role_AbstClass):
    def __init__(self, name, player_, master_):
        super().__init__(name)
        self.player_ = player_
        self.master_ = master_
        self.__actions = Action(self.player_, self.master_)
        self.__knowledges = Knowledge(self.player_, self.master_)

    # 親クラスで、
    # player_name -> プレーヤー名を返す
    # role_name -> role_enum.valueを返す
    # を実装

    # 襲撃or追放時に道連れ
    def hunt(self):
        p_dict = self.master_.alive_players_dict()
        p_dict_str = "\n".join([ f"{k}: {v}" for k, v in p_dict.items()])
        self.player_.send_data("alive user:\n" + p_dict_str + "\n")
        ok_send = self.player_.send_data("attack > ", with_CR=False)
        while True:
            if not ok_send:
                sys.exit(0)
            ok_recv, data = self.player_.recv_data()
            if not ok_recv:
                sys.exit(0)
            if data.isdigit() and (int(data) in p_dict.keys()):
                attack_player = p_dict[int(data)]
                #self.master_.submit_answer(submit_type="attack", user=suspected_player) # 選択を登録
                ok_send = self.player_.send_data(f"submit: {attack_player}を襲撃\n")
                return attack_player
            else:
                ok_send = self.player_.send_data("please enter player number\nattack > ", with_CR=False)

        pass
        

    # 役職定数: abstractproperty implementation
    @property
    def role_enum(self):
        return ROLES.HUNTER # ここを変更


    # 勝利条件: abstractproperty implementation
    @property
    def win_condition(self) -> WIN_CONDITION:
        return WIN_CONDITION.NO_WOLFS # ここを変更



    ###################### ここから下は共通 #############################
    # 各役割の行動: abstractproperty implementation
    def take_action(self, time_of_day: TIME_OF_DAY):
        # action は messageとselectを実装
        self.__actions.action_dict[time_of_day].action()


    # 各役割の知識用: abstractproperty implementation
    def get_knowledge(self, time_of_day: TIME_OF_DAY):
        self.__knowledges.knowledge_dict[time_of_day].knowledge()
