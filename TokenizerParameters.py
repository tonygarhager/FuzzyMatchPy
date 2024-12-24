from Tokenizer import TokenizerFlags
from Wordlist import Wordlist
from StringUtils import StringUtils
from DefaultFallbackRecognizer import DefaultFallbackRecognizer
from LanguageResource import *
from LanguageResources import LanguageResources
from TokenizerSetup import TokenizerSetup
from Recognizer import *
from DateTimeRecognizer import *
from NumberFSTRecognizer import *
from AlphanumRecognizer import *
from CultureInfoExtensions import CultureInfoExtensions
from AcronymRecognizer import AcronymRecognizer
from RegexRecognizer import *
from CharacterSet import CharacterSet
from Token import *
from MeasureFSTRecognizer import *
from TokenizerHelper import *

class BuiltinRecognizers:
    RecognizeNone = 0
    RecognizeDates = 1
    RecognizeTimes = 2
    RecognizeNumbers = 4
    RecognizeAcronyms = 8
    RecognizeVariables = 16
    RecognizeMeasurements = 32
    RecognizeAlphaNumeric = 64
    RecognizeAll = 127

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

    def __init__(self, setup:TokenizerSetup, access: LanguageResources):
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

        culture_name = self.culture_name

        settings = RecognizerSettings()
        settings.break_on_dash = ((setup.tokenizer_flags & TokenizerFlags.BreakOnDash) > TokenizerFlags.NoFlags)
        settings.break_on_hyphens = ((setup.tokenizer_flags & TokenizerFlags.BreakOnHyphen) > TokenizerFlags.NoFlags)
        settings.break_on_apostrophe = ((setup.tokenizer_flags & TokenizerFlags.BreakOnApostrophe) > TokenizerFlags.NoFlags)

        if (setup.builtin_recognizers & BuiltinRecognizers.RecognizeDates) != BuiltinRecognizers.RecognizeNone:
            self.add_recognizer(DateTimeRecognizer.create(settings, access, culture_name, DateTimePatternType.LongDate | DateTimePatternType.ShortDate, 80))
        if (setup.builtin_recognizers & BuiltinRecognizers.RecognizeTimes) != BuiltinRecognizers.RecognizeNone:
            self.add_recognizer(DateTimeRecognizer.create(settings, access, culture_name, DateTimePatternType.ShortTime | DateTimePatternType.LongTime, 75))
        if (setup.builtin_recognizers & BuiltinRecognizers.RecognizeNumbers) != BuiltinRecognizers.RecognizeNone:
            self.add_recognizer(NumberFSTRecognizer.create(settings, access, culture_name, 70))
        if (setup.builtin_recognizers & BuiltinRecognizers.RecognizeAlphaNumeric) != BuiltinRecognizers.RecognizeNone:
            recognizer = AlphanumRecognizer(settings, 60, culture_name)
            self.add_recognizer(recognizer)
        if (setup.builtin_recognizers & BuiltinRecognizers.RecognizeAcronyms) != BuiltinRecognizers.RecognizeNone:
            recognizer = TokenizerParameters.create_acronym_recognizer(settings, culture_name, 85)

            if recognizer is not None:
                self.reclassify_achronyms = True
                self.add_recognizer(recognizer)
            self.add_recognizer(TokenizerParameters.create_uri_recognizer(settings, culture_name, 100, culture_name))
            self.add_recognizer(TokenizerParameters.create_ip_address_recognizer(settings, 65, culture_name))
            self.add_recognizer(TokenizerParameters.create_email_recognizer(settings, culture_name, 100, culture_name))

        if (setup.builtin_recognizers & BuiltinRecognizers.RecognizeVariables) != BuiltinRecognizers.RecognizeNone:
            try:
                wordlist = Wordlist()
                stream = access.accessor.read_resource_data(culture_name, LanguageResourceType.Variables, True)
                if stream is not None:
                    wordlist.load_stream(stream, True)
                self.variables = TokenizerParameters.initialize_variables(culture_name, wordlist.words)
            except Exception as e:
                pass
        if (setup.builtin_recognizers & BuiltinRecognizers.RecognizeMeasurements) != BuiltinRecognizers.RecognizeNone:
            self.add_recognizer(MeasureFSTRecognizer.create(settings, access, culture_name, 95))
            self.add_recognizer(TokenizerParameters.create_currency_recognizer(settings, access, culture_name))

        separate_clitics = setup.separate_clitics and CultureInfoExtensions.use_clitics(culture_name)

        default_fallback_recognizer = self.create_default_fallback_recognizer(settings, separate_clitics, access)
        self.add_recognizer(default_fallback_recognizer)

        if TokenizerHelper.uses_advanced_tokenization(culture_name):
            try:
                wordlist = Wordlist()
                stream = access.read_resource_data(culture_name, LanguageResourceType.Stopwords, True)
                if stream is not None:
                    wordlist.load_stream(stream, True)
                self.advanced_tokenization_stopword_list = wordlist.words
            except Exception as e:
                pass

        self.sort_recognizer()

    @staticmethod
    def create_currency_recognizer(settings: RecognizerSettings, access: LanguageResources, culture_name: str):
        return CurrencyFSTRecognizer.create()#mod

    @staticmethod
    def create_acronym_recognizer(settings: RecognizerSettings, culture_name: str, priority: int):
        recognizer = AcronymRecognizer(settings, priority, culture_name)
        recognizer.only_if_followed_by_nonword_character = CultureInfoExtensions.use_blank_as_word_separator(culture_name)
        return recognizer

    @staticmethod
    def create_uri_recognizer(settings, actual_culture, priority, culture):
        regex_recognizer = RegexRecognizer(settings, "Uri", priority, "URI", "DEFAULT_URI_RECOGNIZER", False, culture)
        character_set = CharacterSet()
        character_set.add('h')
        character_set.add('H')
        character_set.add('m')
        character_set.add('M')
        character_set.add('f')
        character_set.add('F')

        uri_pattern = r"((https|http|ftp|file)://)[\w\d\-['\"<>]]*[\w\d/\-]"
        regex_recognizer.add(uri_pattern, character_set, case_insensitive=True)

        # Assuming a helper method exists for culture-specific conditions
        regex_recognizer.only_if_followed_by_nonword_character = CultureInfoExtensions.use_blank_as_word_separator(actual_culture)

        return regex_recognizer
    @staticmethod
    def create_email_recognizer(settings, actual_culture, priority, culture):
        email_recognizer = EmailRecognizer(settings, priority, culture)
        email_recognizer.only_if_followed_by_nonword_character = CultureInfoExtensions.use_blank_as_word_separator(actual_culture)
        return email_recognizer

    @staticmethod
    def create_ip_address_recognizer(settings, priority, culture):
        try:
            character_set = CharacterSet()
            character_set.add('0', '9')  # Add the range of digits '0' to '9'

            regex_recognizer = RegexRecognizer(
                settings,
                TokenType.OtherTextPlaceable,
                priority,
                "IPADDRESS",
                "DEFAULT_IPADDRESS_RECOGNIZER",
                True,
                culture
            )

            # Regular expression pattern for matching IP addresses
            ip_pattern = r"\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))){3})\b"
            regex_recognizer.add(ip_pattern, character_set)

            # Set the flag for only recognizing if followed by a non-word character
            regex_recognizer.only_if_followed_by_nonword_character = True

            return regex_recognizer
        except Exception:
            return None

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

    def create_default_fallback_recognizer(self, settings:RecognizerSettings, separate_clitics, accessor):
        twoletter = StringUtils.half_width_to_full_width(self.culture_name)

        if twoletter is not None:
            if twoletter == 'ja' or twoletter == 'zh':
                return DefaultJAZHFallbackRecognizer(settings, TokenType.Unknown, 0, self.culture_name, accessor)
            if twoletter == 'th' or twoletter == 'km':
                return DefaultThaiFallbackRecognizer(settings, TokenType.Unknown, 0, self.culture_name, accessor);
            if twoletter == 'ko':
                if any(recognizer.type == TokenType.Number for recognizer in self.recognizers):
                    return DefaultKoreanFallbackRecognizer(settings, TokenType.Unknown, 0, self.culture_name, accessor)
                else:
                    return DefaultFallbackRecognizer(settings, TokenType.Unknown, 0, self.culture_name, accessor)

        return DefaultFallbackRecognizer(settings, TokenType.Unknown, 0, self.culture_name, accessor)

    def sort_recognizer(self):
        self.recognizers.sort(key=lambda recognizer: recognizer.priority, reverse=True)

if __name__ == '__main__':
    setup = {}
    setup['break_on_whitespace'] = True
    setup['create_whitespace_tokens'] = True
    setup['culture_name'] = 'en-US'
    parameters = TokenizerParameters(setup)
    print(parameters.culture_name)
