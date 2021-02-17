from enum import Enum, Flag, auto

class TIME_OF_DAY(Flag):
    MORNING = auto()
    DAYTIME = auto()
    MIDNIGHT = auto()
    ZERO = auto()

class WIN_CONDITION(Flag):
    NO_WOLFS = auto()
    WOLF_EQ_OR_MORE_THAN_CITIZEN = auto()
    NO_WOLFS_BUT_THIRD_FORCE = auto()
    WOLF_EQ_OR_MORE_THAN_CITIZEN_BUT_THIRD_FORCE = auto()


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
    LOVER = "恋人"

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

