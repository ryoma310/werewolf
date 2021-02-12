# import sys
# sys.path.append("../../..")

from classes.abst_classes.knowledge_abst import Knowledge_AbstClass
from classes.util import TIME_OF_DAY


######################################################################
# ここから下をいじる
class _MORNING(Knowledge_AbstClass):
    def knowledge(self):
        return ""


class _DAYTIME(Knowledge_AbstClass):
    def knowledge(self):
        return ""


class _MIDNIGHT(Knowledge_AbstClass):
    def knowledge(self):
        return ""


# ここまで
######################################################################
class Knowledge:
    def __init__(self):
        morning = _MORNING()
        daytime = _DAYTIME()
        midnight = _MIDNIGHT()
        self.knowledge_dict: Dict[TIME_OF_DAY, Knowledge_AbstClass] = {
            TIME_OF_DAY.MORNING: morning,
            TIME_OF_DAY.DAYTIME: daytime,
            TIME_OF_DAY.MIDNIGHT: midnight
        }
    
    def get_knowledge(self, time_of_day: TIME_OF_DAY) -> str:
        return self.knowledge_dict[time_of_day].knowledge()


# if __name__=="__main__":
#     v = Villager_Knowledge()
#     print(v.get_knowledge(TIME_OF_DAY.MORNING))
    

