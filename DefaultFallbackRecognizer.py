from typing import Tuple

from StringUtils import StringUtils
from Recognizer import *
from CultureInfoExtensions import CultureInfoExtensions
from Token import Token
from Trie import Trie
from SimpleToken import SimpleToken

class DefaultFallbackRecognizer(Recognizer):
    def __init__(self, settings, type, _priority, culture_name:str, _data_accessor):
        super().__init__(settings, type, _priority, None, 'DefaultFallbackRecognizer', False, culture_name)

        self.language_resources = _data_accessor
        self._is_fallback_recognizer = True

        leadingClitics = CultureInfoExtensions.get_leading_clitics(culture_name=culture_name)
        if not leadingClitics:
            return
        num = 0
        self._leading_clitics = Trie()
        for text in leadingClitics:
            self._leading_clitics.insert(text, num)
            num += 1

        #self.settings = {}
        #self.settings['BreakOnHyphen'] = True
        #self.settings['BreakOnDash'] = True
        #self.settings['BreakOnApostrophe'] = False

    @staticmethod
    def is_hard_token_terminator(c, settings:RecognizerSettings):
        unicode_category = StringUtils.get_unicode_category(c)

        if unicode_category in ['Zs', 'Zl', 'Zp', 'Pi', 'Pf']:
            return True

        if unicode_category == 'Po' and settings.break_on_apostrophe and StringUtils.is_apostrophe(c):
            return True
        elif unicode_category == 'Pi' or unicode_category == 'Pf':
            return True

        return (c == '/' or c == '\\' or StringUtils.is_colon(c) or
                StringUtils.is_semicolon(c) or
                (StringUtils.is_hyphen(c) and settings.break_on_hyphens) or
                (StringUtils.is_dash(c) and settings.break_on_dash) or
                (StringUtils.is_apostrophe(c) and settings.break_on_apostrophe))

    @staticmethod
    def is_separable_punct(c):
        unicode_category = StringUtils.get_unicode_category(c)
        return (unicode_category == 'Ps' or  # Open Punctuation
                unicode_category == 'Pe' or  # Close Punctuation
                unicode_category == 'Pf' or  # Final Quote Punctuation
                unicode_category == 'Pi' or  # Initial Quote Punctuation
                unicode_category == 'Sm' or  # Math Symbol
                (unicode_category == 'Po' and c != '.'))  # Other Punctuation (except dot)

    def recognize(self, s: str, from_idx: int, allow_token_bundles: bool, consumed_length: int) -> Tuple[Token, int]:
        consumed_length = 0

        if not s:
            return None, consumed_length

        length = len(s)
        num = from_idx

        while num < length and (StringUtils.is_white_space(s[num]) or StringUtils.is_separator(s[num])):
            num += 1

        if num > from_idx:
            consumed_length = num - from_idx
            token = SimpleToken(s[from_idx:from_idx + consumed_length], TokenType.Whitespace)
            token.culture_name = self.culture_name
            return token, consumed_length

        if DefaultFallbackRecognizer.is_hard_token_terminator(s[num], self._settings):
            consumed_length = 1
            token = SimpleToken(s[from_idx:from_idx + consumed_length], TokenType.GeneralPunctuation)
            token.culture_name = self.culture_name
            return token, consumed_length

        #mod if (this._leadingClitics != null) line:97
        c = s[num]
        flag = StringUtils.is_cjk_char(c)
        while (num < length and
               not StringUtils.is_white_space(c) and
               not StringUtils.is_separator(c) and
               not DefaultFallbackRecognizer.is_hard_token_terminator(s[num], self._settings)):
            flag2 = StringUtils.is_cjk_char(c)

            if flag != flag2:
                break
            num += 1
            if num < length:
                c = s[num]
                flag = flag2

        num3 = num
        num = from_idx

        while num < num3 and (DefaultFallbackRecognizer.is_separable_punct(s[num]) or s[num] == '.'):
            num += 1

        if num > from_idx:
            consumed_length = num - from_idx
            token = SimpleToken(s[from_idx:from_idx + consumed_length], TokenType.GeneralPunctuation)
            token.culture_name = self.culture_name
            return token, consumed_length

        flag3 = False
        flag4 = True

        while flag4:
            flag4 = False
            while num3 - 1 > num and DefaultFallbackRecognizer.is_separable_punct(s[num3 - 1]):
                num3 -= 1
                flag4 = True
            num4 = 0
            while num3 - 1 - num4 > num and s[num3 - 1 - num4] == '.':
                num4 += 1

            if num4 > 1:
                num3 -= num4
                flag4 = True
            elif num4 == 1:
                if not self.language_resources or not self.language_resources.is_abbreviation(s[from_idx:num3]):
                    num3 -= 1
                    flag4 = True
                else:
                    flag3 = True

        consumed_length = num3 - from_idx

        tt = TokenType.Word
        if flag3:
            tt = TokenType.Abbreviation
        token = SimpleToken(s[from_idx:from_idx + consumed_length], tt)
        token.is_stopword = self.language_resources.is_stopword(token.text.lower())
        token.culture_name = self.culture_name
        return token, consumed_length

class DefaultJAZHFallbackRecognizer(DefaultFallbackRecognizer):
    def __init__(self, settings:RecognizerSettings, t:TokenType, priority:int, culture_name:str, accessor):
        super().__init__(settings, t, priority, culture_name, accessor)
        self._is_fallback_recognizer = True

    def recognize(self, s: str, from_idx: int, allow_token_bundles: bool, consumed_length: int) -> Tuple[Token, int]:
        if s is None or len(s) == 0 or from_idx >= len(s):
            return None, consumed_length
        consumed_length = 0
        if StringUtils.is_cjk_punctuation(s[from_idx]):
            if from_idx < len(s) and StringUtils.is_cjk_punctuation(s[from_idx]):
                consumed_length += 1
            token = SimpleToken(s[from_idx:from_idx+consumed_length], TokenType.GeneralPunctuation)
            token.culture_name = self.culture_name
            return token, consumed_length
        if StringUtils.is_cjk_char(s[from_idx]) == False:
            return super().recognize(s, from_idx, allow_token_bundles, consumed_length)
        if from_idx < len(s) and StringUtils.is_cjk_char(s[from_idx]):
            consumed_length += 1
        token = SimpleToken(s[from_idx:from_idx + consumed_length], TokenType.CharSequence)
        token.culture_name = self.culture_name
        return token, consumed_length







