
class TokenizerSetup:
    def __init__(self):
        self.culture_name:str = ''
        self.create_whitespace_tokens:bool = False
        self.break_on_whitespace:bool = False
        self.separate_clitics:bool = False
        self.builtin_recognizers:int = 0
        self.tokenizer_flags:int = 0
