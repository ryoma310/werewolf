from enum import Flag, auto

class TIME_OF_DAY(Flag):
    MORNING = auto()
    DAYTIME = auto()
    MIDNIGHT = auto()

class WIN_CONDITION(Flag):
    VILLAGER_MORE_THAN_WOLF = auto()
    WOLF_MORE_THAN_VILLAGER = auto()