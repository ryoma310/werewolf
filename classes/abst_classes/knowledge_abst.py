from abc import ABCMeta, abstractmethod, abstractproperty
from classes.util import TIME_OF_DAY


class Knowledge_AbstClass(metaclass=ABCMeta):
    @abstractmethod
    def knowledge(self):
        # masterのdbをみて回答
        pass
