from CultureInfoExtensions import CultureInfoExtensions
from typing import List

from SegmentRange import SegmentRange
from SimpleToken import SimpleToken
from StringUtils import StringUtils
from Token import Token, TokenType
from Wordlist import Wordlist
from sortedcontainers import SortedSet

class TokenizerHelper:
    @staticmethod
    def is_cj_culture(culture_name:str) -> bool:
        return culture_name in ["zh-CHT", "zh-TW", "zh-CN", 'zh-HK', 'zh-SG', 'zh-MO', 'ja-JP']

    @staticmethod
    def uses_advanced_tokenization(culture_name:str) -> bool:
        return TokenizerHelper.is_cj_culture(culture_name)

    #AdvancedTokenization.TokenizesToWords
    @staticmethod
    def tokenizes_to_words(culture_name:str) -> bool:
        return CultureInfoExtensions.use_blank_as_word_separator(culture_name) or TokenizerHelper.uses_advanced_tokenization(culture_name)

    def tokenize_icu(self, tokens:List[Token], culture_name:str, stopword_list:Wordlist) -> List[Token]:
        if TokenizerHelper.is_cj_culture(culture_name) == False:
            return tokens

        flag = culture_name[:2] == 'ja'
        list = []
        text = ''
        first:SegmentRange = None
        last:SegmentRange = None

        for token in tokens:
            if (token.type == TokenType.CharSequence or
                    (flag and token.text is not None and
                     len(token.text) == 1 and
                     StringUtils.is_ja_long_vowel_marker(token.text[0]))):
                if text == '':
                    first = token.span
                last = token.span
                text += token.text
            else:
                if text != '':
                    list.extend(TokenizerHelper.get_icu_tokens(text, first, last, culture_name))
                    text = ''
                list.append(token)

        if text != '':
            list.extend(TokenizerHelper.get_icu_tokens(text, first, last, culture_name))
        if not stopword_list:
            return list

        for i in range(len(list)):
            if isinstance(list[i], SimpleToken) and stopword_list.contains(list[i].text):
                list[i].is_stopword = True
        return list

    @staticmethod
    def get_icu_tokens(sequence:str, first:SegmentRange, last:SegmentRange, culture_name:str) -> List[Token]:
        list = []

        if len(sequence) == 1:
            simple_token = SimpleToken(sequence, TokenType.Word)
            simple_token.span = SegmentRange.create_3i(first.fro.index, first.fro.position, last.fro.position)
            simple_token.culture_name = culture_name
            list.append(simple_token)
            return list

        flag = False
        if culture_name == 'ja-JP':
            flag = True
            word_boundary_finder = TokenizerHelper.get_word_boundary_finder()
            list2 = word_boundary_finder.find_ja_boundaries(sequence)
        else:
            word_boundary_finder = TokenizerHelper.get_word_boundary_finder()
            list2 = word_boundary_finder.find_zh_boundaries(sequence)

        if len(list2) > 1:
            list2.pop()

        sorted_set = SortedSet(list2)
        list3 = []

        for num in sorted_set:
            if num < 0 or num > len(sequence) - 1:
                list3.append(num)
            elif flag and StringUtils.is_ja_long_vowel_marker(sequence[num]):
                list3.append(num)

        for item in list3:
            sorted_set.remove(item)

        if len(sorted_set) < 1:
            simple_token = SimpleToken(sequence, TokenType.Word)
            simple_token.span = SegmentRange.create_3i(first.fro.index, first.fro.position, last.fro.position)
            simple_token.culture_name = culture_name
            list.append(simple_token)
            return list

        num2 = 0
        num3 = 0
        for num4 in sorted_set:
            text = sequence[num2:num4]
            simple_token = SimpleToken(text, TokenType.Word)
            simple_token.span = SegmentRange.create_3i(first.fro.index, first.fro.position + num3, first.fro.position + num4 - 1)
            simple_token.culture_name = culture_name
            list.append(simple_token)
            num3 += simple_token.span.length
            num2 = num4

        text = sequence[num2:]
        simple_token = SimpleToken(text, TokenType.Word)
        simple_token.span = SegmentRange.create_3i(last.fro.index, list[len(list) - 1].span.into.position + 1, last.fro.position)
        simple_token.culture_name = culture_name
        list.append(simple_token)
        return list




