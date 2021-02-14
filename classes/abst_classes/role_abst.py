from abc import ABCMeta, abstractmethod, abstractproperty
from classes.util import WIN_CONDITION, TIME_OF_DAY

class Role_AbstClass(metaclass=ABCMeta):
    def __init__(self, name):
        self._player_name = name
        self.log = "----------log----------\n"


    @property
    def player_name(self):
        return self._player_name


    @abstractproperty
    def role_name(self):
        pass

    @abstractproperty
    def win_condition(self) -> WIN_CONDITION:
        pass


    @abstractproperty
    def zero_day(self):
        pass


    @abstractmethod
    def actions(self, time_of_day: TIME_OF_DAY):
        pass

    @abstractproperty
    def knowledges(self, time_of_day: TIME_OF_DAY):
        pass


