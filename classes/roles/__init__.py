# from . import *
"""
classes/roles配下の__init__.pyがあるパッケージを全て読み込み

usage:
    from game import * # PlayerThread, MasterThread, GlobalObject, ReceptionThread
    import classes.roles
    roles_list = classes.roles.role_list()
    print(roles_list)
    classes.roles.villager.player_instance("abc")
"""

import os
import glob

role_list_fullpath = glob.glob(os.path.join(os.path.dirname(__file__), "*", "__init__.py"))
role_list_relpath = list(map(lambda x: os.path.relpath(x, os.path.dirname(__file__)), role_list_fullpath))
pkgs = list(map(lambda x: os.path.dirname(x), role_list_relpath))

__all__ = pkgs
from classes.roles import *


def role_list():
    return __all__
