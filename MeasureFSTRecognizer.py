from Recognizer import *

class MeasureFSTRecognizer(Recognizer):
    def __init__(self):
        pass

    @staticmethod
    def create(settings:RecognizerSettings, resource_data_accessor, culture_name, priority):
        return MeasureFSTRecognizer()

class CurrencyFSTRecognizer(Recognizer):
    def __init__(self):
        pass

    @staticmethod
    def create():
        return CurrencyFSTRecognizer()