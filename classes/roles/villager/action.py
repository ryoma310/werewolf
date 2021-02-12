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
class _MORNING(Action_AbstClass):
    def message(self):
        pass
    
    def select(self):
        pass


class _DAYTIME(Action_AbstClass):
    def message(self):
        pass
    
    def select(self):
        pass

class _MIDNIGHT(Action_AbstClass):
    def message(self):
        pass
    
    def select(self):
        pass

# ここまで
######################################################################
class Action:
    def __init__(self):
        morning = _MORNING()
        daytime = _DAYTIME()
        midnight = _MIDNIGHT()
        self.action_dict: Dict[TIME_OF_DAY, Action_AbstClass] = {
            TIME_OF_DAY.MORNING: morning,
            TIME_OF_DAY.DAYTIME: daytime,
            TIME_OF_DAY.MIDNIGHT: midnight
        }
    
    def get_action(self, time_of_day: TIME_OF_DAY) -> Action_AbstClass:
        return self.action_dict[time_of_day]