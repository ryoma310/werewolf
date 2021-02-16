from abc import ABCMeta, abstractmethod, abstractproperty
from classes.util import WIN_CONDITION, TIME_OF_DAY, ROLES

class Role_AbstClass(metaclass=ABCMeta):
    def __init__(self, name):
        self._player_name = name
        self.log = "----------log----------\n"

    @property
    def player_name(self):
        return self._player_name

    
    @abstractproperty
    def role_enum(self) -> ROLES:
        pass


    @property
    def role_name(self):
        return self.role_enum.value


    @abstractproperty
    def win_condition(self) -> WIN_CONDITION:
        pass


    @abstractmethod
    def take_action(self, time_of_day: TIME_OF_DAY):
        pass


    @abstractmethod
    def get_knowledge(self, time_of_day: TIME_OF_DAY):
        pass


