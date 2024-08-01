from abc import ABCMeta, abstractmethod

class ScopeBase(metaclass=ABCMeta):
    @property
    @abstractmethod
    def ID(self): 
        pass

    

