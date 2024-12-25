from Recognizer import *

class MeasureFSTRecognizer(Recognizer):
    def __init__(self, settings, culture_name, priority, accessor):
        super().__init__(settings, TokenType.Measurement, priority, 'Measurement', 'MeasureFSTRecognizer', False, culture_name)
        #mod

    @staticmethod
    def create(settings:RecognizerSettings, resource_data_accessor, culture_name, priority):
        recognizer = MeasureFSTRecognizer(settings, culture_name, priority, resource_data_accessor)
        recognizer = MeasureFSTRecognizer.set_additional_options(recognizer)
        return recognizer

    @staticmethod
    def set_additional_options(result:Recognizer):
        result.only_if_followed_by_nonword_character = True
        result.override_fallback_recognizer = True
        return result

    def recognize(self, s: str, from_idx: int, allow_token_bundles: bool, consumed_length: int) -> Tuple[Token, int]:
        return None, consumed_length#mod

class CurrencyFSTRecognizer(Recognizer):
    def __init__(self, settings, priority, fst_recog, fst_ex, number_fst_ex, culture_name):
        super().__init__(settings, TokenType.Measurement, priority, 'Currency', 'CurrencyFSTRecognizer', False, culture_name)
        self._fst_recog = fst_recog
        self._currency_fst_ex = fst_ex
        self._number_fst_ex = number_fst_ex
        #mod

    @staticmethod
    def create(settings, culture_name, priority, accessor, fst_ex):
        #mod
        currency_fst_recognizer = CurrencyFSTRecognizer(settings, priority, None, None, None, culture_name)
        currency_fst_recognizer = CurrencyFSTRecognizer.set_additional_options(currency_fst_recognizer)
        return currency_fst_recognizer
    @staticmethod
    def set_additional_options(result:Recognizer):
        result.only_if_followed_by_nonword_character = True
        result.override_fallback_recognizer = True
        return result

    def recognize(self, s: str, from_idx: int, allow_token_bundles: bool, consumed_length: int) -> Tuple[Token, int]:
        return None, consumed_length#mod