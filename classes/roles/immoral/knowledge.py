# import sys
# sys.path.append("../../..")

from classes.abst_classes.knowledge_abst import Knowledge_AbstClass
from classes.util import TIME_OF_DAY, ROLES
import sys

######################################################################
# ここから下をいじる


class _ZERO(Knowledge_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def knowledge(self):
        #fox_list = [p.player_name for p in self.master_.global_object.players_alive if self.master_.global_object.players[p.player_name].role.role_enum is ROLES.FOX_SPIRIT]
        #fox_list_str = ",".join(fox_list)
        #self.player_.send_data(f"今回、妖狐は{fox_list_str}の{len(fox_list)}人です．\n")
        pass


class _MORNING(Knowledge_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def knowledge(self):
        pass
        # self.player_.send_data("knowledge: No info provided to your role\n")


class _DAYTIME(Knowledge_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def knowledge(self):
        # self.player_.send_data("knowledge: No info provided to your role\n") # 昼はいらないっか
        pass


class _MIDNIGHT(Knowledge_AbstClass):
    def __init__(self, player_, master_):
        self.player_ = player_
        self.master_ = master_

    def knowledge(self):
        fox_list = [p.player_name for p in self.master_.global_object.players_alive if self.master_.global_object.players[p.player_name].role.role_enum is ROLES.FOX_SPIRIT]
        fox_list_str = ",".join(fox_list)
        self.player_.send_data(f"今回、妖狐は{fox_list_str}の{len(fox_list)}人です．\n")
        # self.player_.send_data("knowledge: No info provided to your role\n")


# ここまで
######################################################################
class Knowledge:
    def __init__(self, player_, master_):
        zero = _ZERO(player_, master_)
        morning = _MORNING(player_, master_)
        daytime = _DAYTIME(player_, master_)
        midnight = _MIDNIGHT(player_, master_)
        self.knowledge_dict: Dict[TIME_OF_DAY, Knowledge_AbstClass] = {
            TIME_OF_DAY.ZERO: zero,
            TIME_OF_DAY.MORNING: morning,
            TIME_OF_DAY.DAYTIME: daytime,
            TIME_OF_DAY.MIDNIGHT: midnight
        }


# if __name__=="__main__":
#     v = Villager_Knowledge()
#     print(v.get_knowledge(TIME_OF_DAY.MORNING))
