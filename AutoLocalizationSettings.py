from enum import Enum
from typing import Optional

from BuiltinRecognizers import BuiltinRecognizers
from Token import *


class UnitSeparationMode(Enum):
    Auto = 0
    DeleteWhitespace = 1
    InsertSpace = 2
    InsertNonbreakingSpace = 3
    InsertSpecifiedSeparator = 4

class CurrencySymbolPosition(Enum):
    beforeAmount = 1
    afterAmount = 2

class AutoLocalizationSettings:
    def __init__(self):
        self.long_date_pattern: str = ""
        self.short_date_pattern: str = ""
        self.long_time_pattern: str = ""
        self.unit_separation_mode: UnitSeparationMode = UnitSeparationMode.Auto
        self._unit_separator: Optional[str] = None
        self.short_time_pattern: str = ""
        self.localization_parameters_source: str = ""
        self.disable_auto_substitution: BuiltinRecognizers = BuiltinRecognizers.RecognizeNone
        self.number_group_separator: str = ""
        self.number_decimal_separator: str = ""
        self.currency_group_separator: str = ""
        self.currency_decimal_separator: str = ""
        self.currency_symbol_position: Optional[CurrencySymbolPosition] = None
        self.format_date_time_uniformly: bool = False
        self.format_number_separators_uniformly: bool = False
        self.format_currency_separators_uniformly: bool = False
        self.format_currency_position_uniformly: bool = False

    @property
    def unit_separator(self):
        return self._unit_separator

    @unit_separator.setter
    def unit_separator(self, value: str):
        if value == '\0' or value.isspace():
            self._unit_separator = value
        else:
            raise ValueError("value must be a null character or whitespace")

    def attempt_auto_substitution(self, t: Token) -> bool:
        if t is None:
            raise ValueError("Token cannot be None")
        if not t.is_substitutable:
            return False

        if t.type == TokenType.Date:
            return self.disable_auto_substitution != BuiltinRecognizers.RecognizeDates
        elif t.type == TokenType.Time:
            return self.disable_auto_substitution != BuiltinRecognizers.RecognizeTimes
        elif t.type == TokenType.Variable:
            return self.disable_auto_substitution != BuiltinRecognizers.RecognizeVariables
        elif t.type == TokenType.Number:
            return self.disable_auto_substitution != BuiltinRecognizers.RecognizeNumbers
        elif t.type == TokenType.Measurement:
            return self.disable_auto_substitution != BuiltinRecognizers.RecognizeMeasurements
        elif t.type == TokenType.Acronym:
            return self.disable_auto_substitution != BuiltinRecognizers.RecognizeAcronyms
        elif t.type == TokenType.AlphaNumeric:
            return self.disable_auto_substitution != BuiltinRecognizers.RecognizeAlphaNumeric

        return True