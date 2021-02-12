from .role import *

"""
usage:
    import villager
    player = villager.player_instance(name)
"""

def player_instance(name):
    return Villager_Role(name)
