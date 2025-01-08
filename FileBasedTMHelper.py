from AnnotatedTranslationUnit import AnnotatedTranslationUnit
from SearchResults import SearchResults
from FileBasedTranslationMemory import FileBasedTranslationMemory
from Segment import Segment
from TranslationUnit import TranslationUnit
from SearchSettings import *
from bs4 import BeautifulSoup as BS
from bs4.element import NavigableString
from Tag import *

class FileBasedTMHelper:
    @staticmethod
    def get_search_setting(_target, _max_results, _min_score) -> SearchSettings:
        if _target:
            mode = SearchMode.TargetConcordanceSearch
        else:
            mode = SearchMode.ConcordanceSearch
        return SearchSettings(mode, _max_results, _min_score)

    @staticmethod
    def get_search_setting_full(_max_results, _min_score) -> SearchSettings:
        mode = SearchMode.FullSearch
        return SearchSettings(mode, _max_results, _min_score)

    @staticmethod
    def create_segment(item, lang) -> Segment:
        segment = Segment(lang)
        anchor = 1
        for child in item:
            if isinstance(child, NavigableString):
                segment.add_text(child)
            elif child.name == 'x':
                id = str(int(child.attrs['id']) - 1)
                segment.add(Tag(TagType.Standalone, id, anchor))
                anchor += 1
            elif child.name == 'g':
                id = str(int(child.attrs['id']) - 1)
                segment.add(Tag(TagType.Start, id))
                segment.add_text(child.text)
                segment.add(Tag(TagType.End, id, anchor))
                anchor += 1

        return segment
    @staticmethod
    def get_translation_units_from_xliff(fn:str) -> List[TranslationUnit]:
        with open(fn, 'r', encoding='utf-8') as file:
            xml = file.read()
        soup = BS(xml)
        lst = []
        for file in soup.find_all('file'):
            src_lang = file.attrs['source-language']
            dst_lang = file.attrs['target-language']
            for t in file.find_all('trans-unit'):
                src_segment = FileBasedTMHelper.create_segment(t.find('source'), src_lang)
                trg_segment = FileBasedTMHelper.create_segment(t.find('target'), dst_lang)
                tu = TranslationUnit(src_segment, trg_segment)
                lst.append(tu)
        return lst

    @staticmethod
    def fuzzy_search_query(tm_path:str, query:str, max_results:int, min_score:int) -> SearchResults:
        tm = FileBasedTranslationMemory(tm_path)
        org_segment = Segment(tm.tm.languageDirection['srcLang'])
        org_segment.add_text(query)
        tgt_segment = Segment(tm.tm.languageDirection['trgLang'])
        tu = TranslationUnit(org_segment, tgt_segment)

        return tm.search_translation_unit(FileBasedTMHelper.get_search_setting(False, 5, 70), tu)

    @staticmethod
    def fuzzy_search_file(tm_path:str, query:str, max_results:int, min_score:int) -> SearchResults:
        tus = FileBasedTMHelper.get_translation_units_from_xliff(query)
        tm = FileBasedTranslationMemory(tm_path)
        anno_tm = tm.get_annotated_translation_memory(tm.tm.id)
        tm.anno_tm = anno_tm

        for tu in tus:
            anno_tu = AnnotatedTranslationUnit(anno_tm, tu, False, True)
            settings = FileBasedTMHelper.get_search_setting_full(5, 70)
            tu_indexes_to_fuzzy_search = [0]
            tus_ = [anno_tu]
            search_results = tm.fuzzy_search_batch(settings, tus_, 100, tu_indexes_to_fuzzy_search)

