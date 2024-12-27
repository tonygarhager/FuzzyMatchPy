from Segment import Segment
from typing import *

class TuContext:
    def __init__(self, context1:int = 0, context2:int = 0):
        self.context1 = context1
        self.context2 = context2
        self.segment1:Segment = None
        self.segment2:Segment = None

    @staticmethod
    def segment_match(s1: Segment, s2: Segment) -> bool:
        return (not s1 and not s2) or (s1 is not None and s2 is not None and s1 == s2)

class TuContextData:
    def __init__(self):
        self.text_context:TuContext = None
        self.id_context:str = ''
        self.current_structure_context_override:str = None

class TuContexts:
    def __init__(self, other: Optional["TuContexts"] = None):
        if other:
            self.values: Set[TuContext] = set(other.values)
        else:
            self.values: Set[TuContext] = set()

    @property
    def length(self) -> int:
        return len(self.values)

    def add(self, new_val: Optional[TuContext]) -> bool:
        if new_val is None or new_val in self.values:
            return False
        self.values.add(new_val)
        return True

    def add_range(self, contexts: Iterable[TuContext]):
        if contexts:
            self.values.update(contexts)

    def merge(self, values: Iterable[TuContext]) -> bool:
        if not values:
            return False
        initial_size = len(self.values)
        self.values.update(values)
        return len(self.values) > initial_size

    def assign(self, contexts: "TuContexts") -> bool:
        self.clear()
        self.add_range(contexts.values)
        return True

    def clear(self):
        self.values.clear()

    def has_value(self, val: TuContext) -> bool:
        return val in self.values

    def has_values(self, other: Optional["TuContexts"]) -> bool:
        if not other or other.length == 0:
            return True
        return all(self.has_value(val) for val in other.values)

    def equals(self, other: "TuContexts") -> bool:
        return self.has_values(other) and other.has_values(self)

class TuIdContexts:
    def __init__(self, other: Optional["TuIdContexts"] = None):
        """
        Initializes the TuIdContexts instance. If another instance is provided,
        its values are copied; otherwise, an empty set is initialized.
        """
        if other:
            self.values: Set[str] = set(other.values)
        else:
            self.values: Set[str] = set()

    @property
    def length(self) -> int:
        """Returns the number of elements in the values set."""
        return len(self.values)

    def add(self, new_val: Optional[str]) -> bool:
        """
        Adds a single string to the set. Returns False if the value is None or
        already exists in the set; otherwise, adds the value and returns True.
        """
        if new_val is None or new_val in self.values:
            return False
        self.values.add(new_val)
        return True

    def add_range(self, contexts: Iterable[str]):
        """Adds multiple strings to the set."""
        if contexts:
            self.values.update(contexts)

    def merge(self, values: Iterable[str]) -> bool:
        """
        Merges another set of strings into the current set.
        Returns True if new values were added; otherwise, False.
        """
        if not values:
            return False
        initial_size = len(self.values)
        self.values.update(values)
        return len(self.values) > initial_size

    def assign(self, contexts: "TuIdContexts") -> bool:
        """
        Clears the current set and assigns all values from another TuIdContexts instance.
        Returns True to indicate the operation was successful.
        """
        self.clear()
        self.add_range(contexts.values)
        return True

    def clear(self):
        """Clears all values in the set."""
        self.values.clear()

    def has_value(self, val: str) -> bool:
        """Checks if a specific string exists in the set."""
        return val in self.values

    def has_values(self, other: Optional["TuIdContexts"]) -> bool:
        """
        Checks if all values in another TuIdContexts instance exist in the current set.
        Returns True if other is None or has no values.
        """
        if not other or other.length == 0:
            return True
        return all(self.has_value(val) for val in other.values)

    def equals(self, other: "TuIdContexts") -> bool:
        """
        Checks if two TuIdContexts instances contain the same values.
        Returns True if both contain the same values, False otherwise.
        """
        return self.has_values(other) and other.has_values(self)