from abc import ABC, abstractmethod
from typing import List
from typing import Tuple
from pyexpat import features
from TokenizerHelper import TokenizerHelper
from Segment import Segment
from LanguageTools import LanguageTools, FeatureVectorType
from SegmentRange import SegmentRange
from FeatureToRangeMapping import FeatureToRangeMapping

class IAnnotatedSegment(ABC):
    @abstractmethod
    def get_segment(self) -> Segment:
        pass
    @abstractmethod
    def get_hash(self) -> int:
        pass

class AbstractAnnotatedSegment(IAnnotatedSegment):
    def __init__(self, s: Segment, keep_tokens:bool, keep_peripheral_whitespace:bool):
        self.identity_string:str = None
        self.strict_identity_string:str = None
        if keep_peripheral_whitespace == False:
            self.trimmed_prefix = s.trim_start()
            self.trimmed_suffix = s.trim_end()
            self.tm_feature_vector:List[int] = None
            self.concordance_feature_vector:List[int] = None
            if not self.trimmed_prefix:
                pass#mod
        if keep_tokens == False:
            s.tokens = None
        self.segment = s

    @abstractmethod
    def get_lingua_language_tool(self) -> LanguageTools:
        pass

    def get_segment(self) -> Segment:
        return self.segment

    def get_tm_feature_vector(self) -> List[int]:
        if self.tm_feature_vector is not None:
            return self.tm_feature_vector
        list:List[SegmentRange] = None
        self.tm_feature_vector, list = self.compute_feature_vector(FeatureVectorType.ForTranslationMemory, True, list)
        return self.tm_feature_vector

    def get_concordance_feature_vector(self) -> List[int]:
        if self.concordance_feature_vector is not None:
            return self.concordance_feature_vector
        list: List[SegmentRange] = None
        self.concordance_feature_vector, list = self.compute_feature_vector(FeatureVectorType.ForConcordance, True, list)
        return self.concordance_feature_vector

    def compute_word_item_vector(self) -> List[FeatureToRangeMapping]:
        source = List[SegmentRange]()
        features, source = self.compute_feature_vector(FeatureVectorType.ForTranslationMemory, False, source)
        return [
            FeatureToRangeMapping(feature, range_value)
            for feature, range_value in zip(features, source)
        ]

    def compute_character_item_vector(self, feature_to_range_mapping:List[SegmentRange]) -> Tuple[List[int], List[SegmentRange]]:
        return self.compute_feature_vector(FeatureVectorType.ForConcordance, False, feature_to_range_mapping)

    def compute_feature_vector(self, type:int, sort_and_unique:bool, feature_to_range_mapping:List[SegmentRange]) -> Tuple[List[int], List[SegmentRange]]:
        list: List[int] = None
        self.get_lingua_language_tool().stem(self.segment)
        flag = TokenizerHelper.tokenizes_to_words(self.segment.culture_name)

        if type == FeatureVectorType.ForTranslationMemory:
            if flag:
                list, feature_to_range_mapping = self.get_lingua_language_tool().compute_token_feature_vector(self.segment, True, sort_and_unique, feature_to_range_mapping)
            else:
                list, feature_to_range_mapping = self.get_lingua_language_tool().compute_char_feature_vector(type, self.segment, 3, sort_and_unique, feature_to_range_mapping)
        elif type == FeatureVectorType.ForConcordance:
            if flag:
                list, feature_to_range_mapping = self.get_lingua_language_tool().compute_char_feature_vector(type, self.segment, 2, sort_and_unique, feature_to_range_mapping)
            else:
                list, feature_to_range_mapping = self.get_lingua_language_tool().compute_char_feature_vector(type, self.segment, 1, sort_and_unique, feature_to_range_mapping)

        if sort_and_unique and list is not None:
            list.sort()
        if feature_to_range_mapping is not None:
            pass
        return list, feature_to_range_mapping

    def get_identity_string(self):
        if self.identity_string is not None:
            return self.identity_string
        list: List[SegmentRange] = None
        self.identity_string, list = self.get_lingua_language_tool().compute_identity_string(self.segment, LanguageTools.TokenToFeatureMappingMode.Stem, list)
        return self.identity_string

    def get_strict_identity_string(self):
        if self.strict_identity_string is not None:
            return self.strict_identity_string
        self.strict_identity_string = self.compute_strict_identity_string(self.segment)
        return self.strict_identity_string

    #mod 






