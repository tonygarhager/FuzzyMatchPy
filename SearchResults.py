from SortSpecification import *
from typing import List
from TranslationUnit import *
from typing import Callable
from ScoringResult import *
from Placeable import *
from datetime import datetime
from TuContext import *

class SearchResult:
    def __init__(self, tm_tu:TranslationUnit):
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

    def __init__(self, default_sort_order:SortSpecification):
        self.results = List[SearchResult]
        self.sort_order = default_sort_order or SearchResults.get_default_sort_order()
        self.multiple_translations:bool = False
        self.source_segment: Segment = None

    @staticmethod
    def get_default_sort_order() -> SortSpecification:
        return SortSpecification(SearchResults.default_sort_order)

    def sort(self, sort_order:SortSpecification):
        self.sort2(sort_order, None)

    def sort2(self, sort_order:SortSpecification, disambiguator:Callable[[SearchResult, SearchResult], int]) -> None:
        self.sort_order = sort_order or SearchResults.get_default_sort_order()

        if not self.results or len(self.results) < 2 or len(self.sort_order) == 0:
            return

        comparer = SearchResultFieldValueComparer()
        #mod
        self.results.sort()

    def sort_by_order(self, sort_order:str) -> None:
        if not sort_order or len(sort_order) == 0:
            self.sort(self.sort_order)
        self.sort(SortSpecification(sort_order))

    #mod

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
                if num == 0 and a.scoring_result.text_placements != b.scoring_result.text_placements:
                    num = SearchResultFieldValueComparer.compare_to(b.scoring_result.text_placements, a.scoring_result.text_placements)
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


