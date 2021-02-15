from enum import Flag, auto

class TIME_OF_DAY(Flag):
    MORNING = auto()
    DAYTIME = auto()
    MIDNIGHT = auto()
    ZERO = auto()

class WIN_CONDITION(Flag):
    NO_WOLFS = auto()
    WOLF_EQ_OR_MORE_THAN_CITIZEN = auto()
