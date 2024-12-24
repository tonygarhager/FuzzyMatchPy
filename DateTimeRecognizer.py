
from Recognizer import *
from LanguageResources import *

class DateTimePatternType:
    Unknown = 0
    LongDate = 1
    ShortDate = 2
    ShortTime = 4
    LongTime = 8

class DateTimeRecognizer(Recognizer):
    def __init__(self):
        pass#mod
    @staticmethod
    def create(settings: RecognizerSettings, access:LanguageResources, culture_name:str, types: DateTimePatternType, priority:int) -> Recognizer:
        #mod
        return DateTimeRecognizer()