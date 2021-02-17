from .role import *

"""
usage:
    import villager
    player = villager.player_instance(name)
"""

def player_instance(name, player_, master_):
    return Black_Cat_Role(name, player_, master_)
