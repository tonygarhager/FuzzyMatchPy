from Recognizer import *
from LanguageResources import LanguageResources
from CultureInfoExtensions import CultureInfoExtensions

class NumberFSTRecognizer(Recognizer):
    def __init__(self, settings:RecognizerSettings, culture_name:str, priority:int, accessor:LanguageResources):
        super().__init__(settings, TokenType.Number, priority, 'Number', 'NumberFSTRecognizer', False, culture_name)
        #mod
        # self._culture_specific_text_constraints = self.get_culture_specific_text_constraints(culture_name)

    @staticmethod
    def create(settings:RecognizerSettings, access:LanguageResources, culture_name:str, priority:int) -> Recognizer:
        result = NumberFSTRecognizer(settings, culture_name, priority, access)
        result = NumberFSTRecognizer.set_additional_options(result, culture_name)
        return result

    @staticmethod
    def set_additional_options(result, culture_name:str):
        result.only_if_followed_by_nonword_character = CultureInfoExtensions.use_blank_as_word_separator(culture_name)

        if result.additional_terminators is None:
            result.additional_terminators = CharacterSet()

        result.additional_terminators.add('-')
        result.override_fallback_recognizer = True
        return result

    def recognize(self, s: str, from_idx: int, allow_token_bundles: bool, consumed_length: int) -> Tuple[Token, int]:
        return None, consumed_length#mod