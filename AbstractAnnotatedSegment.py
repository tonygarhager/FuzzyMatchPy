from abc import ABC, abstractmethod
from typing import List
from typing import Tuple
from pyexpat import features

from StringUtils import StringUtils
from Token import TokenType
from TokenizerHelper import TokenizerHelper
from Segment import Segment
from LanguageTools import LanguageTools, FeatureVectorType
from SegmentRange import SegmentRange
from FeatureToRangeMapping import FeatureToRangeMapping
from Hash import Hash

class IAnnotatedSegment(ABC):
    @property
    def segment(self) -> Segment:
        pass
    @property
    def hash(self) -> int:
        pass

class AbstractAnnotatedSegment(IAnnotatedSegment):
    IGNORE_WHITESPACE_IN_STRICT_IDENTITY_STRING = False
    def __init__(self, s: Segment, keep_tokens:bool, keep_peripheral_whitespace:bool):
        self._identity_string:str = None
        self._strict_identity_string:str = None
        if keep_peripheral_whitespace == False:
            self.trimmed_prefix = s.trim_start()
            self.trimmed_suffix = s.trim_end()
        if keep_tokens == False:
            s.tokens = None
        self._segment = s
        self._tm_feature_vector: List[int] = None
        self._concordance_feature_vector: List[int] = None

    @property
    def lingua_language_tools(self) -> LanguageTools:
        pass

    @property
    def segment(self) -> Segment:
        return self._segment

    @property
    def tm_feature_vector(self) -> List[int]:
        if self._tm_feature_vector is not None:
            return self._tm_feature_vector
        list = None
        self._tm_feature_vector, list = self.compute_feature_vector(FeatureVectorType.ForTranslationMemory, True, list)
        return self._tm_feature_vector
    @property
    def concordance_feature_vector(self) -> List[int]:
        if self._concordance_feature_vector is not None:
            return self._concordance_feature_vector
        list = None
        self._concordance_feature_vector, list = self.compute_feature_vector(FeatureVectorType.ForConcordance, True, list)
        return self._concordance_feature_vector

    def compute_word_item_vector(self) -> List[FeatureToRangeMapping]:
        source = []
        features, source = self.compute_feature_vector(FeatureVectorType.ForTranslationMemory, False, source)
        return [
            FeatureToRangeMapping(feature, range_value)
            for feature, range_value in zip(features, source)
        ]

    def compute_character_item_vector(self, feature_to_range_mapping:List[SegmentRange]) -> Tuple[List[int], List[SegmentRange]]:
        return self.compute_feature_vector(FeatureVectorType.ForConcordance, False, feature_to_range_mapping)

    def compute_feature_vector(self, type:int, sort_and_unique:bool, feature_to_range_mapping:List[SegmentRange]) -> Tuple[List[int], List[SegmentRange]]:
        list = None
        self.lingua_language_tools.stem(self.segment)
        flag = TokenizerHelper.tokenizes_to_words(self.segment.culture_name)

        if type == FeatureVectorType.ForTranslationMemory:
            if flag:
                list, feature_to_range_mapping = self.lingua_language_tools.compute_token_feature_vector(self.segment, True, sort_and_unique, feature_to_range_mapping)
            else:
                list, feature_to_range_mapping = self.lingua_language_tools.compute_char_feature_vector(type, self.segment, 3, sort_and_unique, feature_to_range_mapping)
        elif type == FeatureVectorType.ForConcordance:
            if flag:
                list, feature_to_range_mapping = self.lingua_language_tools.compute_char_feature_vector(type, self.segment, 2, sort_and_unique, feature_to_range_mapping)
            else:
                list, feature_to_range_mapping = self.lingua_language_tools.compute_char_feature_vector(type, self.segment, 1, sort_and_unique, feature_to_range_mapping)

        if sort_and_unique and list is not None:
            list.sort()
        if feature_to_range_mapping is not None:
            pass
        return list, feature_to_range_mapping

    @property
    def identity_string(self):
        if self._identity_string is not None:
            return self._identity_string
        list: List[SegmentRange] = None
        self._identity_string, list = self.lingua_language_tools.compute_identity_string(self.segment, LanguageTools.TokenToFeatureMappingMode.Stem, list)
        return self._identity_string

    @staticmethod
    def jenkins_hash(bytes_data):
        num = 0
        for b in bytes_data:
            num += b
            num += num << 10
            num ^= num >> 6
        num += num << 3
        num ^= num >> 11
        return num + (num << 15)

    @staticmethod
    def fnv1a_32_hash(array, ib_start, cb_size):
        num = 2166136261  # FNV offset basis for 32-bit hash
        for i in range(ib_start, cb_size):
            num ^= array[i]
            num *= 16777619  # FNV prime for 32-bit hash
            num &= 0xFFFFFFFF  # Ensure 32-bit unsigned behavior
        return num

    @staticmethod
    def get_strict_hash(s):
        bytes_data = s.encode('utf-16le')  # Encoding.Unicode in C# corresponds to UTF-16 LE
        num = AbstractAnnotatedSegment.fnv1a_32_hash(bytes_data, 0, len(bytes_data))
        num2 = AbstractAnnotatedSegment.jenkins_hash(bytes_data)
        num2 = num2 & 0xFFFFFFFFFFFF0000  # Apply the mask 18446744073709486080UL
        num3 = num + num2
        num3 += len(s) & 0xFFFF  # Include string length masked with 65535
        if num3 != 0 and num3 != -1:
            return num3
        return -2

    @property
    def strict_hash(self):
        AbstractAnnotatedSegment.get_strict_hash(self._strict_identity_string)

    @property
    def strict_identity_string(self):
        if self._strict_identity_string is None:
            self._strict_identity_string = self.compute_strict_identity_string(self._segment)
        return self._strict_identity_string

    @property
    def hash(self):
        return Hash.get_hash_code_long(self.identity_string)

    @abstractmethod
    def get_lingua_language_tools(self):
        pass

    @property
    def lingua_language_tools(self) -> LanguageTools:
        return self.get_lingua_language_tools()

    def compute_strict_identity_string(self, segment):
        self.lingua_language_tools.ensure_tokenized_segment(segment)
        result = []

        for token in segment.tokens:
            text = None

            if token.type in {
                TokenType.Unknown,
                TokenType.Word,
                TokenType.Abbreviation,
                TokenType.CharSequence,
                TokenType.GeneralPunctuation,
                TokenType.OpeningPunctuation,
                TokenType.ClosingPunctuation,
                TokenType.Uri
            }:
                text = StringUtils.escape_fn(token.text)

            elif token.type in {
                TokenType.Date,
                TokenType.Time,
                TokenType.Variable,
                TokenType.Number,
                TokenType.Measurement,
                TokenType.Acronym,
                TokenType.UserDefined,
                TokenType.AlphaNumeric
            }:
                text = f"\\{chr(61696 + token.type)}"

            elif token.type == TokenType.Whitespace:
                if not AbstractAnnotatedSegment.IGNORE_WHITESPACE_IN_STRICT_IDENTITY_STRING:
                    text = StringUtils.escape_fn(token.text)

            elif token.type == TokenType.OtherTextPlaceable:
                if token.is_substitutable:
                    text = f"\\{chr(61696 + token.type)}"
                else:
                    text = StringUtils.escape_fn(token.text)

            elif token.type == TokenType.Tag:
                text = "\\"

            if text is not None:
                result.append(text)

        return "".join(result)







