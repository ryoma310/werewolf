from .role import *

"""
usage:
    import villager
    player = villager.player_instance(name)
"""

def player_instance(name, player_, master_):
    return Fortune_Teller_Role(name, player_, master_)
