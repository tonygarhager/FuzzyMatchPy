from Wordlist import Wordlist
from StringUtils import StringUtils
from DefaultFallbackRecognizer import DefaultFallbackRecognizer
from LanguageResources import LanguageResources
from TokenizerSetup import TokenizerSetup

class TokenizerParameters:
    uri_priority = 100
    measurement_priority = 95
    currency_priority = 90
    acronym_priority = 85
    data_priority = 80
    time_priority = 75
    number_priority = 70
    ip_priority = 65
    alphanumeric_priority = 60
    fallback_priority = 0

    def __init__(self, setup:TokenizerSetup):
        self.advanced_tokenization_stopword_list = Wordlist()
        self.break_on_whitespace = False
        self.create_whitespace_tokens = False
        self.recognizers = []
        self.variables = []

        #constructor
        self.break_on_whitespace = setup.break_on_whitespace
        self.create_whitespace_tokens = setup.create_whitespace_tokens
        self.culture_name = setup.culture_name
        self.reclassify_achronyms = False
        #mod
        language_resources = LanguageResources(self.culture_name)
        default_fallback_recognizer = DefaultFallbackRecognizer(language_resources, TokenizerParameters.fallback_priority)
        self.add_recognizer(default_fallback_recognizer)
        self.sort_recognizer()

    def __getitem__(self, index):
        return self.recognizers[index]

    def count(self):
        return len(self.recognizers)

    def has_variable_recognizer(self):
        return self.variables is not None and len(self.variables) > 0

    def add_recognizer(self, recognizer):
        self.recognizers.append(recognizer)

    @staticmethod
    def initialize_variables(culture_name, list):
        if not StringUtils.use_fullwidth(culture_name):
            return list
        hash_set = []
        for input in list:
            hash_set.append(StringUtils.half_width_to_full_width(input))

        return hash_set

    def create_default_fallback_recognizer(self, settings, separate_clitics):
        #mod
        language_resources = LanguageResources(self.culture_name)
        return DefaultFallbackRecognizer(language_resources, TokenizerParameters.fallback_priority)

    def sort_recognizer(self):
        self.recognizers.sort(key=lambda recognizer: recognizer.priority, reverse=True)

if __name__ == '__main__':
    setup = {}
    setup['break_on_whitespace'] = True
    setup['create_whitespace_tokens'] = True
    setup['culture_name'] = 'en-US'
    parameters = TokenizerParameters(setup)
    print(parameters.culture_name)
