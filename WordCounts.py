from typing import Tuple

from CultureInfoExtensions import CultureInfoExtensions
from StringUtils import StringUtils
from Token import TokenType, Token
from Tokenizer import Tokenizer
from TokenizerHelper import TokenizerHelper
from TokenizerParameters import BuiltinRecognizers
from TokenizerSetup import TokenizerSetupFactory


class WordCountsOptions:
    def __init__(self):
        self.break_on_hyphen = False
        self.break_on_dash = False
        self.break_on_tag = False
        self.break_on_apostrophe = False
        self.break_advanced_tokens_by_character = False

class WordCountFlags:
    NoFlags = 0
    BreakOnHyphen = 1
    BreakOnDash = 2
    BreakOnTag = 4
    BreakOnApostrophe = 8
    AllFlags = 7
    DefaultFlags = 4

class WordCounts:
    def __init__(self, tokens:[], options:WordCountsOptions, culture_name:str):
        if (options.break_advanced_tokens_by_character and
                CultureInfoExtensions.use_blank_as_word_separator(culture_name) == False and
                TokenizerHelper.tokenizes_to_words(culture_name)):
            tokenizer = Tokenizer.create_from_setup(TokenizerSetupFactory.create(culture_name, BuiltinRecognizers.RecognizeNone))
            list = []
            for token in tokens:
                if token.type != TokenType.Word:
                    list.append(token)
                else:
                    tokens2 = tokenizer.get_tokens(token.text, False)
                    list.extend(tokens2)
            tokens = list
        self.words:int = 0
        self.characters:int = 0
        self.placeables = 0
        self.tags = 0

        self.do_word_counts(tokens, options.break_on_hyphen, options.break_on_dash, options.break_on_tag, options.break_on_apostrophe)

    def handle_word_characters_count(self, t:Token, was_word:bool, apostrophe_repetitions:int, hyphen_repetitions:int, dash_repetitions:int, tag_repetitions:int) -> Tuple[bool, int, int, int, int]:
        if t.text is not None and len(t.text) > 0:
            self.characters += len(t.text)
            was_word = True
        if (apostrophe_repetitions != 1 and
            apostrophe_repetitions != 2 and
            hyphen_repetitions != 1 and
            dash_repetitions != 1 and
            tag_repetitions <= 0):
            return was_word, apostrophe_repetitions, hyphen_repetitions, dash_repetitions, tag_repetitions
        self.words -= 1
        apostrophe_repetitions = 0
        hyphen_repetitions = 0
        dash_repetitions = 0
        tag_repetitions = 0

        return was_word, apostrophe_repetitions, hyphen_repetitions, dash_repetitions, tag_repetitions

    def set_default_repetitions(self):
        return 0, 0, 0, 0, False

    def do_word_counts(self, tokens:[], break_on_hyphen:bool, break_on_dash:bool, break_on_tag:bool, break_on_apostrophe:bool):
        self.Segments = 1
        flag = False
        b = b2 = b3 = b4 = 0

        if not tokens:
            return

        for token in tokens:
            if token:
                if token.type in [TokenType.Word, TokenType.Abbreviation, TokenType.UserDefined]:
                    self.words += 1
                    flag, b, b2, b3, b4 = self.handle_word_characters_count(token, flag, b, b2, b3, b4)

                elif token.type == TokenType.CharSequence:
                    if token.text:
                        self.words += len(token.text)
                        flag, b, b2, b3, b4 = self.handle_word_characters_count(token, flag, b, b2, b3, b4)

                elif token.type == TokenType.GeneralPunctuation:
                    if token.text:
                        if len(token.text) == 1:
                            if flag and StringUtils.is_hyphen(token.text[0]):
                                if not break_on_hyphen:
                                    b2 += 1
                                else:
                                    b, b2, b3, b4, flag = self.set_default_repetitions()
                            elif flag and StringUtils.is_dash(token.text[0]):
                                if not break_on_dash:
                                    b3 += 1
                                else:
                                    b, b2, b3, b4, flag = self.set_default_repetitions()
                            elif (flag or b == 1) and StringUtils.is_apostrophe(token.text[0]):
                                if not break_on_apostrophe:
                                    b += 1
                                else:
                                    b, b2, b3, b4, flag = self.set_default_repetitions()
                        self.characters += len(token.text)

                elif token.type in [TokenType.OpeningPunctuation, TokenType.ClosingPunctuation]:
                    b, b2, b3, b4, flag = self.set_default_repetitions()
                    if token.text:
                        self.characters += len(token.text)

                elif token.type in [
                    TokenType.Date, TokenType.Time, TokenType.Variable, TokenType.Number,
                    TokenType.Measurement, TokenType.Acronym, TokenType.Uri,
                    TokenType.OtherTextPlaceable, TokenType.AlphaNumeric
                ]:
                    self.words += 1
                    self.placeables += 1
                    flag, b, b2, b3, b4 = self.handle_word_characters_count(token, flag, b, b2, b3, b4)

                elif token.type == TokenType.Whitespace:
                    b, b2, b3, b4, flag = self.set_default_repetitions()

                elif token.type == TokenType.Tag:
                    self.placeables += 1
                    self.tags += 1
                    if flag:
                        # Handle tag-specific logic (assumed logic here for illustration)
                        pass
                    b, b2, b3, b4, flag = self.set_default_repetitions()





