from enum import Enum, Flag, auto
import dataclasses
from typing import ClassVar, List, Dict, Tuple

class TIME_OF_DAY(Flag):
    MORNING = auto()
    DAYTIME = auto()
    MIDNIGHT = auto()
    ZERO = auto()

class WIN_CONDITION(Flag):
    NO_WOLFS = auto()
    WOLF_EQ_OR_MORE_THAN_CITIZEN = auto()
    THIRD_FORCE = auto()
    CUPIT_CUPLE = auto()
    # WOLF_EQ_OR_MORE_THAN_CITIZEN_BUT_THIRD_FORCE = auto()
    # THIRD_FORCE_LEFT = NO_WOLFS_BUT_THIRD_FORCE & WOLF_EQ_OR_MORE_THAN_CITIZEN_BUT_THIRD_FORCE
    # HANGED_WIN_ALONE = auto() # てるてる一人勝ち


class FINISH_TRIGER(Flag):
    NO_WOLFS = auto()
    WOLF_EQ_OR_MORE_THAN_CITIZEN = auto()


@dataclasses.dataclass
class WIN_STATUS:
    finish: bool = False
    finish_triger: FINISH_TRIGER = None
    finish_type: WIN_CONDITION = None
    win_players: List[str] = dataclasses.field(default_factory=list)
    win_players_hanged: List[str] = dataclasses.field(default_factory=list)


class HANGED_WIN_DATE:
    @staticmethod
    def hanged_win_date(player_num):
        if player_num == 4:
            return 2
        elif player_num in [5, 6]:
            return 3
        elif player_num in [7, 8, 9, 10]:
            return 4
        else:
            return 5


class classproperty(object):
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
        return self.getter(owner)


class ROLES(Enum):
    CITIZEN = "市民"
    FORTUNE_TELLER = "占い師"
    KNIGHT = "騎士"
    SHAMAN = "霊媒師"
    HUNTER = "ハンター"
    SHARER = "共有者"
    BAKER = "パン屋"
    MONSTER_CAT = "猫又"
    POLICE_OFFICER = "警察官"

    WEREWOLF = "人狼"
    PSYCHO = "狂人"
    FANATIC = "狂信者" 
    PSYCHO_KILLER = "サイコキラー"
    BLACK_CAT = "黒猫"

    FOX_SPIRIT = "妖狐"
    IMMORAL = "背徳者"

    HANGED = "てるてる"

    CUPID = "キューピット"
    # LOVER = "恋人"

    MAGICIAN = "魔術師"


    @classproperty
    def CITIZEN_SIDE(cls):
        return (r for r in ROLES if r not in [cls.WEREWOLF, cls.FOX_SPIRIT]) # CITIZEN in CITIZEN_SIDE => True

    @classproperty
    def WEREWOLF_SIDE(cls):
      return (cls.WEREWOLF,)

    @classproperty
    def THIRD_FORCE_SIDE(cls):
      return (cls.FOX_SPIRIT,)

    @classproperty
    def ALL_ROLES(cls):
        return (r for r in ROLES)

    @classproperty
    def CITIZEN_SIDE_WINNER(cls):
        return (cls.CITIZEN,cls.FORTUNE_TELLER,cls.KNIGHT,cls.SHAMAN,cls.HUNTER,cls.SHARER,cls.BAKER,cls.MONSTER_CAT,cls.POLICE_OFFICER)

    @classproperty
    def WEREWOLF_SIDE_WINNER(cls):
      return (cls.WEREWOLF,cls.PSYCHO,cls.FANATIC,cls.PSYCHO_KILLER,cls.BLACK_CAT)

    @classproperty
    def THIRD_FORCE_SIDE_WINNER(cls):
      return (cls.FOX_SPIRIT,cls.IMMORAL)