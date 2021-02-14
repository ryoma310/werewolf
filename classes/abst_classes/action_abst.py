from abc import ABCMeta, abstractmethod, abstractproperty
# from game.player import PlayerThread
# from game.master import MasterThread

class Action_AbstClass(metaclass=ABCMeta):
    @abstractproperty
    def action(self, player_, master_):
        pass