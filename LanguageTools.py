from LanguageResources import LanguageResources
from StringUtils import StringUtils
from Tokenizer import *
from Segment import Segment
from typing import Tuple
from typing import List
from TokenizerHelper import TokenizerHelper
from IStemmer import IStemmer
from TokenizerSetup import TokenizerSetup
from Hash import Hash
from TokenizerParameters import TokenizerParameters

class FeatureVectorType:
    ForTranslationMemory = 0
    ForConcordance = 1

class LanguageTools:
    class TokenToFeatureMappingMode:
        Stem = 0
        Token = 1

    def __init__(self, resources:LanguageResources, recognizers:int, flags:int=TokenizerFlags.DefaultFlags, use_alternate_stemmers:bool=False, normalize_char_widths:bool=False):
        self._resources = resources
        self._recognizers = recognizers
        self._tokenizer_flags = flags
        self._use_alternate_stemmers = use_alternate_stemmers
        self._normalize_char_widths = (normalize_char_widths and StringUtils.use_fullwidth(resources.culture_name))
        self._tokenizer:Tokenizer = None
        self.tokens = []
        self._stemmer:IStemmer = None

    def ensure_tokenized_segment(self, segment:Segment, force_retokenization:bool=False, allow_token_bundles:bool=False) -> None:
        if not force_retokenization and segment.tokens is not None:
            return
        segment.tokens = self.tokenizer.tokenize(segment, allow_token_bundles)

    def stem(self, s:Segment) -> None:
        self.ensure_tokenized_segment(s)
        for token in s.tokens:
            type = token.type
            if type == TokenType.Word or type == TokenType.CharSequence or (type == TokenType.Acronym and self._use_alternate_stemmers):
                if isinstance(token, SimpleToken) and token.stem is None and not any(char.isdigit() for char in token.text):
                    if token.type == TokenType.CharSequence:
                        token.stem = token.text
                    else:
                        token.stem = self.stemmer.stem(token.text)
                        if (self._normalize_char_widths):
                            token.stem = StringUtils.half_width_to_full_width(token.stem)

    def is_non_blank_language(self) -> bool:
        return not CultureInfoExtensions.use_blank_as_word_separator(self._resources.culture_name)

    def compute_identity_string(self, segment:Segment, mode:int, position_token_association:[SegmentRange]) -> Tuple[str, List[SegmentRange]]:
        flag = TokenizerHelper.tokenizes_to_words(segment.culture_name)
        self.ensure_tokenized_segment(segment)

        if mode == LanguageTools.TokenToFeatureMappingMode.Stem:
            self.stem(segment)
        flag2 = position_token_association is not None

        if flag2:
            position_token_association.clear()

        sb = ''
        if flag:
            sb = '|'
            if flag2:
                position_token_association.append(None)

        for token in segment.tokens:
            text:str = None
            flag3:bool = True

            if token.type == TokenType.Word or token.type == TokenType.Uri:
                if isinstance(token, SimpleToken):
                    if mode == LanguageTools.TokenToFeatureMappingMode.Stem:
                        text = token.stem or token.text.lower()
                    else:
                        text = token.text.lower()
            elif token.type == TokenType.Abbreviation:
                text = token.text.lower()
            elif token.type == TokenType.CharSequence:
                text = token.text.lower()
                flag3 = False
            elif token.type == TokenType.GeneralPunctuation or token.type == TokenType.OpeningPunctuation or token.type == TokenType.ClosingPunctuation or token.type == TokenType.Whitespace or token.type == TokenType.Tag:
                continue
            elif token.type == TokenType.Date or token.type == TokenType.Time or token.type == TokenType.Variable or token.type == TokenType.Number or token.type == TokenType.Measurement or token.type == TokenType.Acronym or token.type == TokenType.AlphaNumeric:
                if mode == LanguageTools.TokenToFeatureMappingMode.Stem:
                    text = chr(61696 + token.type)
                else:
                    text = token.text.lower()
            elif token.type == TokenType.OtherTextPlaceable:
                if isinstance(token, SimpleToken):
                    if token.is_substitutable():
                        if mode == LanguageTools.TokenToFeatureMappingMode.Stem:
                            text = chr(61696 + token.type)
                        else:
                            text = token.text.lower()
                    elif mode == LanguageTools.TokenToFeatureMappingMode.Stem:
                        text = token.stem or token.text.lower()
                    else:
                        text = token.text.lower()
            elif token.type == TokenType.UserDefined:
                if mode == LanguageTools.TokenToFeatureMappingMode.Stem:
                    text = chr(61696 + token.Type)
                else:
                    text = token.text.lower()

            if text is not None:
                sb += text
                if flag2:
                    for i in range(len(text)):
                        if flag3:
                            position_token_association.append(token.span)
                        else:
                            position_token_association.append(SegmentRange.create_3i(token.span.fro['index'], token.span.fro['position'] + i, token.span.fro['position'] + i))
                if flag:
                    sb += '|'
                    if flag2:
                        position_token_association.append(None)

        return sb, position_token_association

    @property
    def stemmer(self) -> IStemmer:
        if self._stemmer is not None:
            return self._stemmer
        #mod
        return self._stemmer

    @property
    def tokenizer(self) -> Tokenizer:
        if self._tokenizer is not None:
            return self._tokenizer
        tokenizer_setup = TokenizerSetup()
        tokenizer_setup.culture_name = self._resources.culture_name
        tokenizer_setup.create_whitespace_tokens = True
        tokenizer_setup.break_on_whitespace = CultureInfoExtensions.use_blank_as_word_separator(tokenizer_setup.culture_name)
        tokenizer_setup.builtin_recognizers = self._recognizers
        tokenizer_setup.tokenizer_flags = self._tokenizer_flags
        parameters = TokenizerParameters(tokenizer_setup, self._resources)
        self._tokenizer = Tokenizer(parameters)
        return self._tokenizer

    def compute_char_feature_vector(self, fvt:int, segment:Segment, n:int, unique:bool, feature_ranges:List[SegmentRange]) -> Tuple[List[int], List[SegmentRange]]:
        list:List[(int, int)] = None
        list2:List[SegmentRange] = None

        if feature_ranges is not None and unique == False:
            list = List[(int, int)]
            list2 = List[SegmentRange]
            feature_ranges.clear()
        s = ''
        if fvt != FeatureVectorType.ForTranslationMemory:
            if fvt != FeatureVectorType.ForConcordance:
                raise('Unexpected case')
            s, list2 = self.compute_identity_string(segment, LanguageTools.TokenToFeatureMappingMode.Token, list2)
        else:
            s, list2 = self.compute_identity_string(segment, LanguageTools.TokenToFeatureMappingMode.Stem, list2)

        result, list = self.compute_char_feature_vector4(s, n, unique, list)

        if not list2:
            return result, feature_ranges
        for pair in list:
            item = list2[pair.second]
            feature_ranges.append(item)
        return result, feature_ranges

    def compute_char_feature_vector4(self, s:str, n:int, unique:bool, feature_position_association):
        list = []
        flag = False
        if feature_position_association is not None:
            feature_position_association.clear()
            flag = (unique == False)
        if s is None or len(s) == 0:
            list.append(0)
        elif len(s) <= n:
            list.append(Hash.get_hashcode_int(s))
            if flag:
                feature_position_association.append((0, len(s) - 1))
        else:
            for i in range(len(s) - n + 1):
                hash_code_int = Hash.get_hashcode_int(s[i:i + n])
                if unique == False or hash_code_int not in list:
                    list.append(hash_code_int)
                    if flag:
                        feature_position_association.append((i, i + n - 1))

        if unique:
            list.sort()

        return list, feature_position_association

    def compute_token_feature_vector(self, segment:Segment, include_frequent:bool, unique:bool, feature_to_range_mapping:List[SegmentRange]) -> Tuple[List[int], List[SegmentRange]]:
        flag = feature_to_range_mapping is not None and unique == False
        list = List[int]
        if flag and len(feature_to_range_mapping) > 0:
            feature_to_range_mapping.clear()
        for token in segment.tokens:
            num = 0
            if token.type == TokenType.Word or token.type == TokenType.Abbreviation or token.type == TokenType.Acronym or token.type == TokenType.Uri or token.type == TokenType.OtherTextPlaceable:
                if isinstance(token, SimpleToken) and (include_frequent or self.is_stopword(token.text) == False):
                    num = Hash.get_hashcode_int(token.stem or token.text.lower())
            elif token.type == TokenType.CharSequence:
                list2 = None
                if flag:
                    list2 = []
                num2 = 0
                enumer2, list2 = self.compute_char_feature_vector4(token.text, 3, unique, list2)

                for num3 in enumer2:
                    if num3 != 0 and (unique == False or num3 not in list):
                        list.append(num3)
                        if flag:
                            num4 = token.span.fro['position'] + num2
                            feature_to_range_mapping.append(SegmentRange.create_3i(token.span.fro['index'], num4, num4))
                        num2 += 1
            elif token.type == TokenType.GeneralPunctuation or token.type == TokenType.OpeningPunctuation or token.type == TokenType.ClosingPunctuation or token.type == TokenType.Whitespace or token.type == TokenType.Tag:
                continue
            elif token.type == TokenType.Date or token.type == TokenType.Time or token.type == TokenType.Variable or token.type == TokenType.Number or token.type == TokenType.Measurement or token.type == TokenType.UserDefined or token.type == TokenType.AlphaNumeric:
                num = token.type

            if num == 0 or (unique and num in list):
                continue
            list.append(num)
            if flag:
                feature_to_range_mapping.append(token.span)
                continue

        list.sort()
        return list, feature_to_range_mapping

    def is_stopword(self, s:str) -> bool:
        return self._resources.is_stopword(s.lower())

    def get_stoplist_signature(self) -> str:
        return self._resources.get_stoplist_signature()

    def get_tokenizer_signature(self) -> str:
        return self._tokenizer.get_signature()

    def get_stemmer_signature(self) -> str:
        return self._stemmer.get_signature()

    def get_abbreviation_signature(self) -> str:
        return self._resources.get_abbreviation_signature()
