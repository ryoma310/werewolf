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

class Villager_Role(Role_AbstClass):
    def __init__(self, name):
        super().__init__(name)
        self.__role_name = "villager"
        self.__actions = Action()
        self.__knowledges = Knowledge()


    # 役職名: abstractproperty implementation
    @property
    def role_name(self) -> str:
        return self.__role_name


    # 勝利条件: abstractproperty implementation
    @property
    def win_condition(self) -> WIN_CONDITION:
        return WIN_CONDITION.VILLAGER_MORE_THAN_WOLF


    # 0日目の行動: abstractproperty implementation
    @property
    def zero_day(self):
        pass


    # 各役割の行動: abstractproperty implementation
    """
        Action_AbstClass:
            message: property
            select: method
    """
    def actions(self, time_of_day: TIME_OF_DAY):
        # action は messageとselectを実装
        action: Action_AbstClass = self.__actions.get_action(time_of_day)
        
        ## TODO messageを表示したり、selectを受け取って送信したり..


    # 各役割の知識用: abstractproperty implementation
    """
    usage: 
        player = Villager_Role(name)
        player.knowledges(TIME_OF_DAY.MORNING)
        player.knowledges(TIME_OF_DAY.DAYTIME)
        player.knowledges(TIME_OF_DAY.MIDNIGHT)
    """
    @property
    def knowledges(self, time_of_day: TIME_OF_DAY) -> str:
        return self.__knowledges.get_knowledge(time_of_day)
