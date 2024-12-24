from SortSpecification import *
from typing import List
from TranslationUnit import *
from typing import Callable

class SearchResult:
    def __init__(self, tm_tu:TranslationUnit):
        self.memory_translation_unit = tm_tu
        self.metadata = {}

class SearchResults:
    def __init__(self, default_sort_order:SortSpecification):
        self.results = List[SearchResult]()
        self.sort_order = default_sort_order or SearchResults.get_default_sort_order()

    @staticmethod
    def get_default_sort_order() -> SortSpecification:
        return SortSpecification(SearchResults.default_sort_order)

    def sort(self, sort_order:SortSpecification):
        self.sort2(sort_order, None)

    def sort2(self, sort_order:SortSpecification, disambiguator:Callable[[SearchResult, SearchResult], int]) -> None:
        self.sort_order = sort_order or SearchResults.get_default_sort_order()

        if not self.results or len(self.results) < 2 or len(self.sort_order) == 0:
            return

        #mod
