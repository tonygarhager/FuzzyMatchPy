from Recognizer import Recognizer, RecognizerSettings
from SimpleToken import SimpleToken
from Token import *
from StringUtils import *

class AcronymRecognizer(Recognizer):
    def __init__(self, settings: RecognizerSettings, priority: int, culture_name: str):
        super().__init__(settings, TokenType.Acronym, priority, 'ACR', 'AcronymRecognizer', False, culture_name)
        self.set_culture_specific_behaviour()

    def set_culture_specific_behaviour(self):
        twoletter = StringUtils.get_iso_language_code(self.culture_name)
        if twoletter is not None and twoletter == 'ko':
            self.override_fallback_recognizer = True

    def recognize(self, s: str, from_index: int, allow_token_bundles: bool, consumed_length: int) -> Tuple[Token, int]:
        consumed_length = 0
        if not s[from_index].isupper():
            return None, 0

        num = len(s) - 1
        i = from_index + 1
        consumed_length = 1

        while i <= num:
            c = s[i]
            if c.isupper():
                consumed_length = i - from_index + 1
            elif c != '&':
                break
            i += 1

        if consumed_length < 2:
            return None, 0

        text = s[from_index:from_index + consumed_length]
        simple_token = SimpleToken(text, TokenType.Acronym)
        simple_token.culture_name = self.culture_name
        return simple_token, consumed_length
