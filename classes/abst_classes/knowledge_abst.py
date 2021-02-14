from abc import ABCMeta, abstractmethod, abstractproperty


class Knowledge_AbstClass(metaclass=ABCMeta):
    @abstractmethod
    def knowledge(self, player_, master_):
        # masterのdbをみて回答
        pass
