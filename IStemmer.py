from abc import ABC, abstractmethod

class IStemmer(ABC):
    @abstractmethod
    def stem(self, word:str) -> str:
        pass
    @abstractmethod
    def get_signature(self) -> str:
        pass