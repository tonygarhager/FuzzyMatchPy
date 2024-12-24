from Recognizer import *
from LanguageResources import LanguageResources

class NumberFSTRecognizer(Recognizer):
    def __init__(self):
        pass
    @staticmethod
    def create(settings:RecognizerSettings, access:LanguageResources, culture_name:str, priority:int) -> Recognizer:
        return NumberFSTRecognizer()#mod