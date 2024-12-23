from TokenizerParameters import TokenizerParameters
from Segment import Segment
from Tag import Tag
from Token import *
from SegmentRange import SegmentRange
from CultureInfoExtensions import CultureInfoExtensions
from Text import Text
from StringUtils import StringUtils
from SimpleToken import SimpleToken
from NumberToken import NumberToken
from TokenBundle import TokenBundle
from DateTimeToken import DateTimeToken

class Tokenizer:
    max_acro_length = 6
    def __init__(self, parameters: TokenizerParameters):
        self.parameters = parameters

    def tokenize(self, s, allow_token_bundles):
        return self.get_tokens(s, allow_token_bundles, True)

    def get_tokens(self, s:Segment, allow_token_bundles, enhanced_asian):
        list = []
        num = -1

        for segment_element in s.elements:
            num += 1
            if not segment_element:
                continue

            if isinstance(segment_element, Tag):
                pass#mod
            elif isinstance(segment_element, Token):
                segment_element.span = SegmentRange.create_3i(num, 0, 0)
                segment_element.culture_name = self.parameters.culture_name
                list.append(segment_element)
            elif isinstance(segment_element, Text):
                list2 = self.tokenize_internal(segment_element.value, num, self.parameters.create_whitespace_tokens, allow_token_bundles, self.get_filtered_recognizers(segment_element.value))

                if enhanced_asian:
                    list2 = self.get_advanced_tokens(list2)
                if not list2 and len(list2) > 0:
                    list.extend(list2)

        self.reclassify_achronyms(list, enhanced_asian)
        self.adjust_number_range_tokenization(list)
        return list

    def tokenize_internal(self, s:str, current_run:int, create_whitespace_tokens:bool, allow_token_bundles:bool, recognizers:[]):
        list = []
        num = -1
        flag = not CultureInfoExtensions.use_blank_as_word_separator(self.parameters.culture_name)
        i = 0
        length = len(s)
        while i < length:
            num2 = i
            while i < length and StringUtils.is_white_space(s[i]):
                i += 1
            if i > num2:
                if create_whitespace_tokens:
                    token = SimpleToken(s[num2:i], TokenType.Whitespace)
                    token.culture_name = self.parameters.culture_name
                    token.span = SegmentRange.create_3i(current_run, num2, i - 1)
                    list.append(token)
                num2 = i
            if i >= length:
                break
            recognizer = None
            num3 = 0
            token2 = None
            for j in range(len(recognizers)):
                recognizer2 = recognizers[j]
                token3, num4 = recognizer2.recognize(s, num2, allow_token_bundles)

                if token3 is not None and (not flag or not isinstance(token3, NumberToken) or num2 + num4 >= length or StringUtils.is_latin_letter(s[num2 + num4])):
                    if not recognizer or (num3 < num4 and (not recognizer.override_fallback_recognizer or not recognizer.is_fallback_recognizer)):
                        token2 = token3
                        recognizer = recognizer2
                        num3 = num4
                        i = num2 + num4
                    elif recognizer.priority < recognizer2.priority:
                        token2 = token3
                        recognizer = recognizer2
                        num3 = num4
                        i = num2 + num4
            if token2 is not None:
                if isinstance(token2, TokenBundle):
                    if token2.count() == 1:
                        token2 = token2[0].token
            else:
                while i < length and StringUtils.get_unicode_category(s[i]) == StringUtils.get_unicode_category(s[num2]):
                    i += 1
                token2 = SimpleToken(s[num2:i], TokenType.Word)
                token2.culture_name = self.parameters.culture_name

            if not token2:
                raise('winningToken can\'t be null')

            token2.span = SegmentRange.create_3i(current_run, num2, i - 1)
            list.append(token2)

            if self.parameters.has_variable_recognizer():
                list, _ = self.apply_variable_recognizer(s, token2, list, num)

        return list
    
    def apply_variable_recognizer(self, s:str, token:Token, list:[], start_chain_token_position:int):
        if Tokenizer.is_variable_part(token):
            return self.check_for_variable_tokens(token, s, list, start_chain_token_position)
        start_chain_token_position = -1
        return list, start_chain_token_position

    @staticmethod
    def is_variable_part(token:Token):
        return isinstance(token, NumberToken) or isinstance(token, DateTimeToken) or (isinstance(token, SimpleToken) and token.type == TokenType.Word or token.type == TokenType.Variable or token.type == TokenType.GeneralPunctuation or token.type == TokenType.Acronym or token.type == TokenType.CharSequence) or token.type == TokenType.AlphaNumeric

    def check_for_variable_tokens(self, winning_token:Token, s:str, result:[], start_chain_token_position:int):
        if start_chain_token_position == -1:
            start_chain_token_position = len(result) - 1
        num = start_chain_token_position
        i = len(result) - num
        while i > 0:
            pos1 = result[num].span.fro['position']
            pos2 = winning_token.span.into['position']
            text = s[pos1:pos2 + 1]
            item = text
            if StringUtils.use_fullwidth(self.parameters.culture_name):
                item = StringUtils.half_width_to_full_width(text)
            if item in self.parameters.variables:
                result = Tokenizer.merge_last_tokens(text, i, result, num, self.parameters.culture_name)
                return result, start_chain_token_position
            num += 1
            while (num <= len(result) - 1 and not Tokenizer.is_variable_part(result[num])):
                num += 1
            i = len(result) - num
        return result, start_chain_token_position

    @staticmethod
    def merge_last_tokens(variable_candidate:str, nr_tokens:int, result:[], index_to_update:int, culture_name:str):
        span = result[index_to_update].span
        result[index_to_update] = SimpleToken(variable_candidate, TokenType.Variable)
        result[index_to_update].span = span
        result[index_to_update].culture_name = culture_name

        if nr_tokens <= 1:
            return result
        result[index_to_update].span = SegmentRange(result[index_to_update].span.fro, result[len(result) - 1].span.into)
        del result[index_to_update + 1, index_to_update + nr_tokens]
        return result
