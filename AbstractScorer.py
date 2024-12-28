from AnnotatedSegment import AnnotatedSegment
from AnnotatedTranslationMemory import AnnotatedTranslationMemory
from CultureInfoExtensions import CultureInfoExtensions
from LanguageTools import LanguageTools
from ScoringResult import ScoringResult, TextContextMatch
from SearchResults import SearchResult
from SearchSettings import SearchSettings, SearchMode
from abc import ABC, abstractmethod
from typing import List, Tuple
from Segment import Segment
from SimpleToken import SimpleToken
from TagToken import TagToken
from TermFinder import TermFinder
from Token import Token
from Tokenizer import Tokenizer
from TokenizerHelper import TokenizerHelper
from TokenizerSetup import TokenizerSetupFactory
from TuContext import TuContextData

class FuzzyIndexes:
    SourceWordBased = 1
    SourceCharacterBased = 2
    TargetCharacterBased = 4
    TargetWordBased = 8

class TextContextMatchType:
    PrecedingSourceAndTarget = 1
    PrecedingAndFollowingSource = 2

class AbstractScorer(ABC):
    word_delete_or_insert_penalty:float = 6.0
    minor_change_penalty:float = 1.0
    medium_change_penalty:float = 3.0

    def __init__(self, settings: SearchSettings, text_context_match_type:TextContextMatchType, normalize_char_width:bool = False):
        self.settings = settings
        self._text_context_match_type = text_context_match_type
        self._normalize_char_width = normalize_char_width

    @abstractmethod
    def recognizers(self) -> int:
        pass

    @abstractmethod
    def get_source_tools(self) -> LanguageTools:
        pass

    @abstractmethod
    def get_target_tools(self) -> LanguageTools:
        pass

    @abstractmethod
    def get_annotated_segment(self, segment:Segment, is_target_segment:bool, keep_tokens:bool, keep_peripheral_whitespace:bool):
        pass

    @property
    def source_tools(self):
        return self.get_source_tools()

    @property
    def target_tools(self):
        return self.get_target_tools()

    @staticmethod
    def get_segment_hash(s:AnnotatedSegment):
        return s.hash

    @staticmethod
    def is_whitespace_or_punctuation(t:Token) -> bool:
        return t.is_whitespace or t.is_punctuation

    @staticmethod
    def get_length_based_change_score(l:float) -> float:
        if l <= 3.0:
            return AbstractScorer.medium_change_penalty
        if l >= 6.0:
            return AbstractScorer.word_delete_or_insert_penalty
        num:float = AbstractScorer.minor_change_penalty + (l - 3.0) * (AbstractScorer.word_delete_or_insert_penalty - AbstractScorer.minor_change_penalty) / 3.0
        if num >= AbstractScorer.minor_change_penalty and num <= AbstractScorer.word_delete_or_insert_penalty:
            return num
        return AbstractScorer.word_delete_or_insert_penalty

    @staticmethod
    def count_words(tokens:[]) -> Tuple[float, int, int]:
        num:float = 0
        total_words = 0
        stop_words = 0
        for token in tokens:
            if token.is_whitespace or token.is_punctuation:
                num += 0.1
            elif isinstance(token, TagToken) == False:
                num + 1.0
            if token.is_word:
                total_words += 1
                if AbstractScorer.is_stopword(token):
                    stop_words += 1
        return num, total_words, stop_words

    @staticmethod
    def is_stopword(t:Token) -> bool:
        return isinstance(t, SimpleToken) and t.is_stopword

    def compute_scores(self, search_result:SearchResult, doc_src_segment:AnnotatedSegment, doc_tgt_segment:AnnotatedSegment,
                       document_places:[], tu_context_data:TuContextData, is_duplicate_search:bool,
                       used_index:FuzzyIndexes, score_diagonal_only:bool = False):
        char_width_difference = False
        scoring_result = ScoringResult()

        if search_result.scoring_result is None:
            search_result.scoring_result = scoring_result
        else:
            scoring_result = search_result.scoring_result

        if self.settings.is_concordance_search:
            num = self.get_concordance_score(search_result, doc_src_segment, doc_tgt_segment)
        else:
            pass#mod

        if num > 100:
            num = 100
        elif num < 0:
            num = 0
        scoring_result.base_score = num
        search_result.scoring_result.text_context_match = TextContextMatch.NoMatch

        if num <= 0:
            return
        if scoring_result.is_exact_match and self.settings.is_concordance_search == False:
            pass#mod
        self.apply_penalties(search_result, char_width_difference)

    def apply_penalties(self, search_result:SearchResult, char_width_difference:bool):
        pass#mod

    def get_concordance_score(self, search_result:SearchResult, doc_src_segment:AnnotatedSegment, doc_tgt_segment:AnnotatedSegment):
        if self.settings.mode == SearchMode.ConcordanceSearch:
            annotated_segment = doc_src_segment
            annotated_segment2 = self.get_annotated_segment(search_result.memory_translation_unit.src_segment, False, True, False)
            self.source_tools.ensure_tokenized_segment(annotated_segment.segment)
            self.source_tools.ensure_tokenized_segment(annotated_segment2.segment)
        else:
            annotated_segment = doc_tgt_segment
            annotated_segment2 = self.get_annotated_segment(search_result.memory_translation_unit.trg_segment, True, True, False)
            self.target_tools.ensure_tokenized_segment(annotated_segment.segment)
            self.target_tools.ensure_tokenized_segment(annotated_segment2.segment)

        use_width_normalization = self._normalize_char_width and CultureInfoExtensions.use_full_width(annotated_segment2.segment.culture_name)
        term_finder_result = TermFinder.find_terms(annotated_segment.segment, annotated_segment2.segment, True, use_width_normalization)
        if not (term_finder_result.matching_ranges if term_finder_result else None) or len(
                term_finder_result.matching_ranges) == 0:
            return 0

        search_result.scoring_result.matching_concordance_ranges = term_finder_result.matching_ranges
        return term_finder_result.score


class Scorer(AbstractScorer):
    def __init__(self, tm:AnnotatedTranslationMemory, settings:SearchSettings, normalize_char_width:bool = False):
        super().__init__(settings, tm.tm.text_context_match_type, normalize_char_width)
        self._tm = tm
        self.setup_legacy_tokenizers()

    def setup_legacy_tokenizers(self):
        if (self.settings.advanced_tokenization_legacy_scoring and
            CultureInfoExtensions.use_blank_as_word_separator(self._tm.tm.languageDirection['srcLang']) and
            TokenizerHelper.tokenizes_to_words(self._tm.tm.languageDirection['srcLang'])):
            setup = TokenizerSetupFactory.create(self._tm.tm.languageDirection['srcLang'], self.recognizers())
            self.legacy_source_tokenizer = Tokenizer(setup)
        if (self.settings.advanced_tokenization_legacy_scoring and
            CultureInfoExtensions.use_blank_as_word_separator(self._tm.tm.languageDirection['trgLang']) and
            TokenizerHelper.tokenizes_to_words(self._tm.tm.languageDirection['trgLang'])):
            setup = TokenizerSetupFactory.create(self._tm.tm.languageDirection['trgLang'], self.recognizers())
            self.legacy_target_tokenizer = Tokenizer(setup)

    def recognizers(self) -> int:
        return self._tm.tm.recognizers

    def get_source_tools(self) -> LanguageTools:
        return self._tm.source_tools

    def get_target_tools(self) -> LanguageTools:
        return self._tm.target_tools

    def get_annotated_segment(self, segment: Segment, is_target_segment: bool, keep_tokens: bool,
                              keep_peripheral_whitespace: bool):
        return AnnotatedSegment(self._tm, segment, is_target_segment, keep_tokens, keep_peripheral_whitespace)

