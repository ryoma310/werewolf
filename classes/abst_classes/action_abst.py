from abc import ABCMeta, abstractmethod, abstractproperty

class Action_AbstClass(metaclass=ABCMeta):    
    @abstractproperty
    def message(self):
        pass
    
    @abstractmethod
    def select(self):
        pass