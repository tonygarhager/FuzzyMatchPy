from abc import ABC, abstractmethod

class SegmentElement:
    class Similarity:
        Non = 0
        IdenticalType = 1
        IdenticalValueAndType = 2

    @abstractmethod
    def duplicate(self):
        pass

    @abstractmethod
    def get_similarity(self, other):
        pass

    @abstractmethod
    def get_similarity_param(self, other, allow_compatibility):
        return self.get_similarity(other)

