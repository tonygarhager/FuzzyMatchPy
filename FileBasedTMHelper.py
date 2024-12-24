from SearchResults import SearchResults
from FileBasedTranslationMemory import FileBasedTranslationMemory
from Segment import Segment
from TranslationUnit import TranslationUnit
from SearchSettings import *

class FileBasedTMHelper:
    def __init__(self):
        pass#mode

    @staticmethod
    def get_search_setting(_target, _max_results, _min_score):
        if _target:
            mode = SearchMode.TargetConcordanceSearch
        else:
            mode = SearchMode.ConcordanceSearch
        return SearchSettings(mode, _max_results, _min_score)

    def fuzzy_search(self, tm_path:str, query:str, max_results:int, min_score:int) -> SearchResults:
        tm = FileBasedTranslationMemory(tm_path)
        org_segment = Segment(tm.tm.languageDirection['srcLang'])
        org_segment.add(query)
        tgt_segment = Segment(tm.tm.languageDirection['trgLang'])
        tu = TranslationUnit(org_segment, tgt_segment)
        return tm.search_translation_unit(FileBasedTMHelper.get_search_setting(False, 5, 70), tu)
