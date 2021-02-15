from classes.abst_classes.role_abst import Role_AbstClass
from classes.abst_classes.action_abst import Action_AbstClass
from classes.util import WIN_CONDITION, TIME_OF_DAY

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

class Werewolf_Role(Role_AbstClass):
    def __init__(self, name, player_, master_):
        super().__init__(name)
        self.__role_name = "werewolf"
        self.player_ = player_
        self.master_ = master_
        self.__actions = Action(self.player_, self.master_)
        self.__knowledges = Knowledge(self.player_, self.master_)


    # 役職名: abstractproperty implementation
    @property
    def role_name(self) -> str:
        return self.__role_name


    # 勝利条件: abstractproperty implementation
    @property
    def win_condition(self) -> WIN_CONDITION:
        return WIN_CONDITION.WOLF_EQ_OR_MORE_THAN_CITIZEN


    # 各役割の行動: abstractproperty implementation
    def take_action(self, time_of_day: TIME_OF_DAY):
        # action は messageとselectを実装
        self.__actions.action_dict[time_of_day].action()


    # 各役割の知識用: abstractproperty implementation
    def get_knowledge(self, time_of_day: TIME_OF_DAY):
        self.__knowledges.knowledge_dict[time_of_day].knowledge()
