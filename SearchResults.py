from DateTimeToken import DateTimeToken
from NumberToken import NumberToken, MeasureToken
from SortSpecification import *
from typing import List

from Sorter_T import Sorter_T
from Token import TokenType
from TranslationUnit import *
from typing import Callable
from ScoringResult import *
from Placeable import *
from datetime import datetime
from TuContext import *
from functools import cmp_to_key

class SearchResult:
    def __init__(self, tm_tu:TranslationUnit = None):
        self.memory_translation_unit = tm_tu
        self.metadata = {}
        self.scoring_result:ScoringResult = None
        self.memory_placeables:List[Placeable] = None
        self.placeable_associations:List[PlaceableAssociation] = None
        self.translation_proposal:TranslationUnit = None
        self.context_data:TuContext = None
        self.cascade_entry_index:int = -1
        self.matching_placeholder_tokens = 0

class SearchResults:
    default_sort_order = 'Sco/D ChD/D UsC/D'
    default_sort_order_concordance = 'Sco/D ChD/D UsC/D'

    def __init__(self, default_sort_order:SortSpecification = None):
        self.results = []
        self.sort_order = default_sort_order or SearchResults.get_default_sort_order()
        self.multiple_translations:bool = False
        self.source_segment: Segment = None

    @staticmethod
    def get_default_sort_order() -> SortSpecification:
        return SortSpecification(SearchResults.default_sort_order)

    def sort(self, sort_order:SortSpecification, disambiguator:Callable[[SearchResult, SearchResult], int] = None) -> None:
        self.sort_order = sort_order or SearchResults.get_default_sort_order()

        if not self.results or len(self.results) < 2 or len(self.sort_order) == 0:
            return

        comparer = SearchResultFieldValueComparer()
        comparer2 = Sorter_T(comparer, self.sort_order)
        self.results.sort(key=cmp_to_key(comparer2.compare))

    def sort_by_order(self, sort_order:str) -> None:
        if not sort_order or len(sort_order) == 0:
            self.sort(self.sort_order)
        self.sort(SortSpecification(sort_order))

    @staticmethod
    def check_cm_validity(r, prev_results):
        if prev_results is not None and (
                len(prev_results) == 0 or prev_results[0].scoring_result.match != 100):
            for search_result in filter(
                    lambda x: x is not None and x.scoring_result.text_context_match == TextContextMatch.SourceTargetMatch,
                    r.results):
                search_result.scoring_result.text_context_match = TextContextMatch.SourceMatch

    @staticmethod
    def post_merge_fixup(search_results_per_segment, settings):
        if settings and not settings.is_document_search:
            return

        if search_results_per_segment is None:
            raise ValueError("search_results_per_segment cannot be None")

        num = 0
        previous_search_results = None

        for current_search_results in search_results_per_segment:
            if num > 0 and current_search_results is not None:
                SearchResults.check_cm_validity(current_search_results, previous_search_results)

            if current_search_results is not None:
                current_search_results.check_for_multiple_translations(settings)

            previous_search_results = current_search_results
            num += 1

    def check_for_multiple_translations(self, settings):
        if self.results is None:
            return
        if settings is not None and settings.is_concordance_search:
            return
        #self.check_for_multiple_translations_m(settings, [x for x in self.results if x.translation_proposal is not None])
        self.check_for_multiple_translations_m(settings, self.results)

    def remove_multiple_translation_penalty(self, exact_matches):
        for search_result in exact_matches:
            search_result.scoring_result.remove_penalty(PenaltyType.MultipleTranslations)

    @staticmethod
    def first_match_is_visibly_better(first:SearchResult, second:SearchResult)->bool:
        return (first.scoring_result.is_full_cm and not second.scoring_result.is_full_cm) or \
            first.scoring_result.text_replacements < second.scoring_result.text_replacements or \
            first.scoring_result.placeable_format_changes < second.scoring_result.placeable_format_changes

    def to_normalized_string(s:Segment):
        if s.tokens is None:
            return str(s)

        try:
            string_builder = []
            for token in s.tokens:
                if token:
                    if token.type in [TokenType.Date, TokenType.Time]:
                        date_time_token = token if isinstance(token, DateTimeToken) else None
                        if date_time_token:
                            formatted_date = date_time_token.value.strftime(
                                '%d' if date_time_token.is_date_token else '%t')
                            string_builder.append(f"{formatted_date}{date_time_token.date_time_pattern_type}")
                    elif token.type == TokenType.Number:
                        number_token = token if isinstance(token, NumberToken) else None
                        if number_token:
                            string_builder.append(str(number_token.value))
                    elif token.type == TokenType.Measurement:
                        measure_token = token if isinstance(token, MeasureToken) else None
                        if measure_token:
                            string_builder.append(str(measure_token.value))
                            if measure_token.unit_separator != '\0':
                                string_builder.append(measure_token.unit_separator)
                            string_builder.append(measure_token.unit_string)
                    else:
                        string_builder.append(str(token))
            text = ''.join(string_builder)
        except Exception:
            text = str(s)

        return text

    def check_for_multiple_translations_m(self, settings, search_results):
        if search_results is None:
            return
        if settings is not None and settings.is_concordance_search:
            return
        self.multiple_translations = False
        exact_matches = []

        for search_result in search_results:
            if search_result is not None and search_result.scoring_result is not None and search_result.scoring_result.is_exact_match:
                exact_matches.append(search_result)

        if len(exact_matches) < 2:
            self.remove_multiple_translation_penalty(exact_matches)
            return

        self.multiple_translations = True
        exact_matches.sort(key=lambda aa, bb: SearchResultFieldValueComparer.compare(bb, aa, True))

        num = SearchResultFieldValueComparer.score_without_multiple_translation_penalty(exact_matches[0])
        num2 = SearchResultFieldValueComparer.score_without_multiple_translation_penalty(exact_matches[1])
        flag = num == 100 and num2 == 100 and not SearchResults.first_match_is_visibly_better(exact_matches[0],
                                                                                              exact_matches[1])

        if flag:
            list_matches = [x for x in exact_matches[1:] if
                            SearchResultFieldValueComparer.score_without_multiple_translation_penalty(
                                x) == 100 and not SearchResults.first_match_is_visibly_better(exact_matches[0], x)]
            flag2 = False
            text = self.to_normalized_string(exact_matches[0].translation_proposal.trg_segment)

            for item in list_matches:
                text2 = self.to_normalized_string(item.translation_proposal.trg_segment)
                if text != text2:
                    flag2 = True
                    break

            flag = flag2

        if not flag:
            self.remove_multiple_translation_penalty(exact_matches)
            return

        if settings is not None:
            penalty = settings.find_penalty(PenaltyType.MultipleTranslations)
            if penalty is None:
                return

            for search_result2 in [x for x in exact_matches if
                                   SearchResults.can_apply_multiple_translations_penalty(x)]:
                search_result2.scoring_result.apply_penalty(penalty)

    @staticmethod
    def can_apply_multiple_translations_penalty(search_result):
        if not search_result or not search_result.scoring_result or not search_result.scoring_result.is_exact_match:
            return False

        if search_result.scoring_result.applied_penalties is None:
            return True

        for penalty in search_result.scoring_result.applied_penalties:
            if penalty.malus > 0:
                if penalty.type in [PenaltyType.TagMismatch, PenaltyType.MemoryTagsDeleted,
                                    PenaltyType.AutoLocalization,
                                    PenaltyType.FilterPenalty, PenaltyType.ProviderPenalty,
                                    PenaltyType.TextReplacement]:
                    return False
        return True


class SearchResultFieldValueComparer:
    @staticmethod
    def compare_to(x, y):
        return (x > y) - (x < y)

    @staticmethod
    def compare_datetime(x: datetime, y: datetime):
        if x > y:
            return 1
        elif x < y:
            return -1
        return 0

    @staticmethod
    def score_without_multiple_translation_penalty(sr:SearchResult):
        if sr.scoring_result.applied_penalties is None or len(sr.scoring_result.applied_penalties) == 0:
            return sr.scoring_result.match
        applied_penalty = next(
            (x for x in sr.scoring_result.applied_penalties if x.type == PenaltyType.MultipleTranslations), None)
        return sr.scoring_result.match + (0 if applied_penalty is None else applied_penalty.malus)

    def compare(self, a: SearchResult, b:SearchResult, field_name: str) -> int:
        if not a or not b or not field_name or len(field_name) == 0:
            raise('ArgumentNullException')
        text = field_name.lower()

        if text is not None:
            if text == 'sco':
                num = a.scoring_result.match - b.scoring_result.match
                if num == 0 and a.scoring_result.id_context_match != b.scoring_result.id_context_match:
                    num = -1
                    if a.scoring_result.id_context_match:
                        num = 1
                if num == 0 and a.scoring_result.target_segment_differs != b.scoring_result.target_segment_differs:
                    num = 1
                    if a.scoring_result.target_segment_differs:
                        num = -1
                if num == 0:
                    num = a.matching_placeholder_tokens - b.matching_placeholder_tokens
                if num == 0:
                    num = a.scoring_result.text_context_match - b.scoring_result.text_context_match
                if num == 0 and a.scoring_result.is_structure_context_match != b.scoring_result.is_structure_context_match:
                    num = -1
                    if a.scoring_result.is_structure_context_match:
                        num = 1
                if num == 0 and a.scoring_result.memory_tags_deleted != b.scoring_result.memory_tags_deleted:
                    num = 1
                    if a.scoring_result.memory_tags_deleted:
                        num = -1
                if num == 0 and a.scoring_result.text_replacements != b.scoring_result.text_replacements:
                    num = SearchResultFieldValueComparer.compare_to(b.scoring_result.text_replacements, a.scoring_result.text_replacements)
                if num == 0 and a.scoring_result.placeable_format_changes != b.scoring_result.placeable_format_changes:
                    num = SearchResultFieldValueComparer.compare_to(b.scoring_result.placeable_format_changes, a.scoring_result.placeable_format_changes)
                return num
            elif text == 'usc':
                return a.memory_translation_unit.system_fields.use_count - b.memory_translation_unit.system_fields.use_count
            elif text == 'usd':
                return SearchResultFieldValueComparer.compare_datetime(a.memory_translation_unit.system_fields.use_date,
                                                                       b.memory_translation_unit.system_fields.use_date)
            elif text == 'crd':
                return SearchResultFieldValueComparer.compare_datetime(
                    a.memory_translation_unit.system_fields.creation_date,
                    b.memory_translation_unit.system_fields.creation_date)
            elif text == 'chd':
                return SearchResultFieldValueComparer.compare_datetime(
                    a.memory_translation_unit.system_fields.change_date,
                    b.memory_translation_unit.system_fields.change_date)
        applied_penalty_a = a.scoring_result.find_applied_filter(text)
        applied_penalty_b = b.scoring_result.find_applied_filter(text)

        if (applied_penalty_a is None and applied_penalty_b is None) or (
                applied_penalty_a is not None and applied_penalty_b is not None):
            num = 0
        elif applied_penalty_a is None:
            num = 1
        else:
            num = -1

        return num


