from classes.abst_classes.role_abst import Role_AbstClass
from classes.abst_classes.action_abst import Action_AbstClass
from classes.util import WIN_CONDITION, TIME_OF_DAY, ROLES

from .knowledge import Knowledge
from .action import Action
import random

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


class Black_Cat_Role(Role_AbstClass):
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

    # 襲撃された際に実行
    def bit_attacked(self):
        p_dict = self.master_.alive_players_dict()
        not_wolfs = [v for k, v in p_dict.items() if (
            self.master_.global_object.players[v].role.role_enum is not ROLES.WEREWOLF) and (self.player_.player_name != v)]
        attacked_citizen = random.choice(not_wolfs)
        return attacked_citizen

    # 役職定数: abstractproperty implementation
    @property
    def role_enum(self):
        return ROLES.BLACK_CAT  # ここを変更

    # 勝利条件: abstractproperty implementation

    @property
    def win_condition(self) -> WIN_CONDITION:
        return WIN_CONDITION.WOLF_EQ_OR_MORE_THAN_CITIZEN  # ここを変更

    ###################### ここから下は共通 #############################
    # 各役割の行動: abstractproperty implementation

    def take_action(self, time_of_day: TIME_OF_DAY):
        # action は messageとselectを実装
        self.__actions.action_dict[time_of_day].action()

    # 各役割の知識用: abstractproperty implementation

    def get_knowledge(self, time_of_day: TIME_OF_DAY):
        self.__knowledges.knowledge_dict[time_of_day].knowledge()
