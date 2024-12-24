
from Recognizer import *
from LanguageResources import *
from CultureInfoExtensions import *

class DateTimePatternType:
    Unknown = 0
    LongDate = 1
    ShortDate = 2
    ShortTime = 4
    LongTime = 8

class DateTimeRecognizer(Recognizer):
    def __init__(self, settings:RecognizerSettings, priority:int, patterns, datetime_fstexmap, culture_name:str):
        super().__init__(settings, TokenType.Date, priority, 'DateTime', 'DateTimeRecognizer', False, culture_name)
        self._calendar_patterns = patterns
        self.patterns_computed_per_type = datetime_fstexmap

    @staticmethod
    def create(settings: RecognizerSettings, access:LanguageResources, culture_name:str, types: DateTimePatternType, priority:int) -> Recognizer:
        dateTimeFstExMap = {}
        patterns = []
        #mod
        recognizer = DateTimeRecognizer(settings, priority, patterns, dateTimeFstExMap, culture_name)
        recognizer.only_if_followed_by_nonword_character = CultureInfoExtensions.use_blank_as_word_separator(culture_name)
        return recognizer