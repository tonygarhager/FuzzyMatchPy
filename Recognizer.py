from CharacterSet import *
from typing import Callable
from Token import Token, TokenType
from StringUtils import *
from abc import *

class RecognizerSettings:
    def __init__(self):
        self.break_on_hyphens: bool = False
        self.break_on_dash: bool = False
        self.break_on_apostrophe: bool = False

class IRecognizerTextFilter(ABC):
    @abstractmethod
    def exclude_text(self, s:str)->bool:
        pass

class Recognizer:
    def __init__(self, settings:RecognizerSettings, t:TokenType, priority:int,
                 token_class_name:str, recognizer_name:str, auto_substitutable:bool, culture_name:str):
        self._override_fallback_recognizer = False
        self._is_fallback_recognizer = False
        self._settings = settings
        self._type = t
        self._priority = priority
        self.token_class_name = token_class_name
        self.recognizer_name = recognizer_name
        self.auto_substitutable = auto_substitutable
        self.culture_name = culture_name
        self._additional_terminators:CharacterSet = None
        self._culture_specific_text_constraints:Callable[[str, int, Token], bool] = None
        self.only_if_followed_by_nonword_character:bool = False

    @property
    def type(self):
        return self._type

    @property
    def is_fallback_recognizer(self):
        return self._is_fallback_recognizer

    @property
    def override_fallback_recognizer(self):
        return self._override_fallback_recognizer

    @override_fallback_recognizer.setter
    def override_fallback_recognizer(self, value):
        self._override_fallback_recognizer = value

    @property
    def priority(self):
        return self._priority

    @property
    def additional_terminators(self):
        return self._additional_terminators
    @additional_terminators.setter
    def additional_terminators(self, value):
        self._additional_terminators = value

    def verify_context_constraints(self, s:str, p:int, t:Token = None)->bool:
        if self._culture_specific_text_constraints is not None:
            return self._culture_specific_text_constraints(s, p, t)
        return self.default_text_constraints(s, p, True)

    def default_text_constraints(self, s:str, p:int, break_on_cjk:bool = True)->bool:
        if self.only_if_followed_by_nonword_character == False or p >= len(s):
            return True
        c = s[p]
        return ((self._additional_terminators is not None and c in self._additional_terminators) or
                StringUtils.is_white_space(c) or
                StringUtils.is_punctuation(c) or
                StringUtils.is_separator(c) or
                StringUtils.is_symbol(c) or
                (break_on_cjk and StringUtils.is_cjk_char(c)))




