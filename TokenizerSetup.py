from CultureInfoExtensions import CultureInfoExtensions
from BuiltinRecognizers import BuiltinRecognizers

class TokenizerFlags:
    NoFlags = 0
    BreakOnHyphen = 1
    BreakOnDash = 2
    BreakOnApostrophe = 4
    AllFlags = 3
    DefaultFlags = 7

class TokenizerSetup:
    def __init__(self):
        self.culture_name:str = ''
        self.create_whitespace_tokens:bool = False
        self.break_on_whitespace:bool = False
        self.separate_clitics:bool = False
        self.builtin_recognizers:int = 0
        self.tokenizer_flags:int = 0

class TokenizerSetupFactory:
    @staticmethod
    def create(culture_name:str, recognizers:BuiltinRecognizers, flags:TokenizerFlags = TokenizerFlags.DefaultFlags):
        setup = TokenizerSetup()
        setup.culture_name = culture_name
        setup.builtin_recognizers = recognizers
        setup.tokenizer_flags = flags
        setup.create_whitespace_tokens = False
        setup.break_on_whitespace = CultureInfoExtensions.use_blank_as_word_separator(culture_name)
        return setup
