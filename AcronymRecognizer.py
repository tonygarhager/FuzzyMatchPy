from Recognizer import Recognizer, RecognizerSettings
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
