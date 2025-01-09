from typing import List, Set
from AutoLocalizationSettings import CurrencySymbolPosition

class CurrencyFormat:
    def __init__(self):
        self._symbol = None
        self.category = None
        self.currency_symbol_positions: List[CurrencySymbolPosition] = []
        self._separators: Set[str] = set()

    @property
    def symbol(self) -> str:
        return self._symbol

    @symbol.setter
    def symbol(self, value: str):
        if value is not None and any(char.isspace() for char in value):
            raise ValueError("Whitespace is not permitted in currency symbols")
        self._symbol = value

    @property
    def separators(self) -> Set[str]:
        return self._separators

    @separators.setter
    def separators(self, value: Set[str]):
        if value is not None and any(x != '\0' and not x.isspace() for x in value):
            raise ValueError("Separator characters must be whitespace or the null character")
        self._separators = value

    def clone(self):
        cloned = CurrencyFormat()
        cloned.symbol = None if self.symbol is None else self.symbol[:]
        cloned.category = None if self.category is None else self.category[:]
        cloned.currency_symbol_positions = self.currency_symbol_positions[:] if self.currency_symbol_positions else []
        cloned.separators = self.separators.copy() if self.separators else set()
        return cloned
