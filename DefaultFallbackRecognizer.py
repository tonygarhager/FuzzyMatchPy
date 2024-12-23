from StringUtils import StringUtils
from Recognizer import Recognizer

class DefaultFallbackRecognizer(Recognizer):
    def __init__(self, _language_resources, _priority):
        self.priority = _priority
        self.language_resources = _language_resources
        self.settings = {}
        self.settings['BreakOnHyphen'] = True
        self.settings['BreakOnDash'] = True
        self.settings['BreakOnApostrophe'] = False

    @staticmethod
    def is_hard_token_terminator(c, settings):
        unicode_category = StringUtils.get_unicode_category(c)

        if unicode_category in ['Zs', 'Zl', 'Zp', 'Pi', 'Pf']:
            return True

        if unicode_category == 'Po' and settings['BreakOnApostrophe'] and StringUtils.is_apostrophe(c):
            return True
        elif unicode_category == 'Pi' or unicode_category == 'Pf':
            return True

        return (c == '/' or c == '\\' or StringUtils.is_colon(c) or
                StringUtils.is_semicolon(c) or
                (StringUtils.is_hyphen(c) and settings['BreakOnHyphen']) or
                (StringUtils.is_dash(c) and settings['BreakOnDash']) or
                (StringUtils.is_apostrophe(c) and settings['BreakOnApostrophe']))

    @staticmethod
    def is_separable_punct(c):
        unicode_category = StringUtils.get_unicode_category(c)
        return (unicode_category == 'Ps' or  # Open Punctuation
                unicode_category == 'Pe' or  # Close Punctuation
                unicode_category == 'Pf' or  # Final Quote Punctuation
                unicode_category == 'Pi' or  # Initial Quote Punctuation
                unicode_category == 'Sm' or  # Math Symbol
                (unicode_category == 'Po' and c != '.'))  # Other Punctuation (except dot)

    def recognize(self, s, fro, allow_token_bundles):
        consumed_length = 0

        if not s:
            return None, consumed_length

        length = len(s)
        num = fro

        while num < length and (StringUtils.is_white_space(s[num]) or StringUtils.is_separator(s[num])):
            num += 1

        token = {}
        if num > fro:
            consumed_length = num - fro
            token['string'] = s[fro:fro+consumed_length]
            token['type'] = 'Whitespace'
            return token, consumed_length

        if DefaultFallbackRecognizer.is_hard_token_terminator(s[num], self.settings):
            consumed_length = 1
            token['string'] = s[fro:fro+consumed_length]
            token['type'] = 'GeneralPunctuation'
            return token, consumed_length

        c = s[num]
        flag = StringUtils.is_cjk_char(c)
        while num < length and \
            not StringUtils.is_white_space(c) and \
            not StringUtils.is_separator(c) and \
            not DefaultFallbackRecognizer.is_hard_token_terminator(s[num], self.settings):
            flag2 = StringUtils.is_cjk_char(c)

            if flag != flag2:
                break
            num += 1
            if num < length:
                c = s[num]
                flag = flag2

        num3 = num
        num = fro

        while num < num3 and (DefaultFallbackRecognizer.is_separable_punct(s[num]) or s[num] == '.'):
            num += 1

        if num > fro:
            consumed_length = num - fro
            token['string'] = s[fro:fro+consumed_length]
            token['type'] = 'GeneralPunctuation'
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
                if not self.language_resources or not self.language_resources.is_abbreviation(s[fro:num3]):
                    num3 -= 1
                    flag4 = True
                else:
                    flag3 = True

        consumed_length = num3 - fro
        token['string'] = s[fro:fro+consumed_length]
        if flag3:
            token['type'] = 'Abbreviation'
        else:
            token['type'] = 'Word'

        token['isstopword'] = self.language_resources.is_stopword(token['string'].lower())
        return token, consumed_length





