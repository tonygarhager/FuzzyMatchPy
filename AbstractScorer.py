from AnnotatedSegment import AnnotatedSegment
from AnnotatedTranslationMemory import AnnotatedTranslationMemory
from BuiltinRecognizers import BuiltinRecognizers
from CultureInfoExtensions import CultureInfoExtensions
from EditDistance import EditOperation, EditDistanceResolution, EditDistance
from Field import Field
from LanguageTools import LanguageTools
from Penalty import PenaltyType
from Placeable import PlaceableAssociation, PlaceableType
from ScoringResult import ScoringResult, TextContextMatch
from SearchResults import SearchResult
from SearchSettings import SearchSettings, SearchMode
from abc import ABC, abstractmethod
from typing import List, Tuple, Set, Dict
from Segment import Segment
from SegmentEditDistanceComputer import SegmentEditDistanceComputer
from SegmentElement import SegmentElement
from SimpleToken import SimpleToken
from StringUtils import StringUtils
from TagToken import TagToken
from TermFinder import TermFinder
from Token import Token, TokenType, ILocalizableToken
from Tokenizer import Tokenizer
from TokenizerHelper import TokenizerHelper
from TokenizerSetup import TokenizerSetupFactory
from TranslationUnit import TranslationUnitOrigin, ConfirmationLevel
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

    @staticmethod
    def apply_small_change_adjustment(culture_name:str) -> bool:
        regionNeutralName = StringUtils.get_iso_language_code(culture_name)
        return (regionNeutralName != "ko") and (regionNeutralName != "ja") and (regionNeutralName != "cz")

    def check_placeable_format(self, doc_segment, search_result, document_placeables):
        if document_placeables is None:
            return

        for plc in document_placeables:
            placeable_associations = search_result.placeable_associations
            placeable_association = None
            if placeable_associations:
                placeable_association = next(
                    (element for element in placeable_associations if element.document == plc), None
                )

            if placeable_association and placeable_association.memory and placeable_association.memory.source_token_index >= 0:
                localizable_token = doc_segment.tokens[
                    placeable_association.document.source_token_index] if placeable_association.document.source_token_index >= 0 else None
                token = search_result.memory_translation_unit.src_segment.tokens[
                    placeable_association.memory.source_token_index] if placeable_association.memory.source_token_index >= 0 else None

                if isinstance(localizable_token, ILocalizableToken) and isinstance(token, ILocalizableToken):
                    if not localizable_token.does_format_match(token):
                        scoring_result = search_result.scoring_result
                        scoring_result.placeable_format_changes += 1

    def check_and_delete_memory_tags(self, search_result:SearchResult):
        if not search_result.memory_placeables:
            return

        scoring_result = search_result.scoring_result

        for placeable in search_result.memory_placeables:
            if placeable.type in [PlaceableType.PairedTagStart, PlaceableType.PairedTagEnd,
                                  PlaceableType.StandaloneTag] and placeable.source_token_index >= 0:
                num = scoring_result.edit_distance.find_target_item_index(placeable.source_token_index)
                if num >= 0:
                    operation = scoring_result.edit_distance.items[num].operation
                    scoring_result.edit_distance.set_resolution_at(num, EditDistanceResolution.Deletion)
                    scoring_result.resolved_placeables += 1
                    scoring_result.memory_tags_deleted = True

        if scoring_result.memory_tags_deleted:
            penalty = self.settings.find_penalty(PenaltyType.MemoryTagsDeleted)
            if penalty:
                scoring_result.apply_penalty(penalty)

    def apply_tag_mismatch_penalty(self, result, search_result, ed_item, plc, tag_mismatch:bool)->bool:
        if ed_item >= 0 and result.edit_distance.items[ed_item].resolution == EditDistanceResolution.Non:
            search_result.scoring_result.edit_distance.set_resolution_at(ed_item, EditDistanceResolution.Other)

            penalty = None
            if plc.type != PlaceableType.PairedTagEnd:
                penalty = search_result.settings.find_penalty(PenaltyType.TagMismatch)

            if penalty:
                result.apply_penalty(penalty)

            tag_mismatch = True
        return tag_mismatch

    def check_tag_mismatch_penalty(self, search_result:SearchResult, document_placeables)->bool:
        scoring_result = search_result.scoring_result
        flag = False

        # Check memory placeables
        if search_result.memory_placeables:
            for plc2 in search_result.memory_placeables:
                placeable_associations = search_result.placeable_associations
                if not any(association.memory == plc2 for association in placeable_associations) and plc2.is_tag:
                    num = scoring_result.edit_distance.find_target_item_index(plc2.source_token_index)
                    flag = self.apply_tag_mismatch_penalty(scoring_result, search_result, num, plc2, flag)

        # Check document placeables
        if document_placeables:
            for plc in document_placeables:
                placeable_associations2 = search_result.placeable_associations
                if not any(association.document == plc for association in placeable_associations2) and plc.is_tag:
                    num2 = scoring_result.edit_distance.find_source_item_index(plc.source_token_index)
                    flag = self.apply_tag_mismatch_penalty(scoring_result, search_result, num2, plc, flag)

        return flag

    def compute_simplified_match_score(self, ed:EditDistance, doc_src_tokens, mem_src_tokens, apply_small_change_adjustment,
                                       normalize_char_widths):
        num = 0
        matching_placeholders_by_value = 0
        char_width_difference = False

        num2, num3, num4 = AbstractScorer.count_words(doc_src_tokens)
        tmp, num5, num6 = AbstractScorer.count_words(mem_src_tokens)
        num2 += tmp
        num7, num8, num9 = 0, 0, 0

        for edit_distance_item in ed.items:
            if edit_distance_item.operation == EditOperation.Identity:
                if edit_distance_item.resolution == EditDistanceResolution.Substitution and doc_src_tokens[
                    edit_distance_item.source].is_placeable:
                    matching_placeholders_by_value += 1
                if doc_src_tokens[edit_distance_item.source].is_word:
                    if AbstractScorer.is_stopword(doc_src_tokens[edit_distance_item.source]):
                        num7 += 1
                    else:
                        num8 += 1
            elif edit_distance_item.operation == EditOperation.Change:
                resolution = edit_distance_item.resolution
                if resolution != EditDistanceResolution.Non:
                    if resolution == EditDistanceResolution.Substitution:
                        num9 += 1
                elif normalize_char_widths:
                    if doc_src_tokens[edit_distance_item.source].text == mem_src_tokens[edit_distance_item.target].text:
                        char_width_difference = True
                elif AbstractScorer.is_whitespace_or_punctuation(
                        doc_src_tokens[edit_distance_item.source]) and AbstractScorer.is_whitespace_or_punctuation(
                        mem_src_tokens[edit_distance_item.target]):
                    num += 0.1
                elif isinstance(doc_src_tokens[edit_distance_item.source], TagToken) and isinstance(mem_src_tokens[edit_distance_item.target], TagToken):
                    if edit_distance_item.resolution != EditDistanceResolution.Non:
                        num += 0.5
                elif edit_distance_item.costs < 0.06:
                    num += 0.2
                elif edit_distance_item.costs < 0.3:
                    num += 0.7
                else:
                    num += 1.5
            elif edit_distance_item.operation == EditOperation.Move:
                if edit_distance_item.resolution == EditDistanceResolution.Non:
                    num += 0.8
                else:
                    num += 0.5
            elif edit_distance_item.operation == EditOperation.Insert:
                if edit_distance_item.resolution == EditDistanceResolution.Non:
                    if mem_src_tokens[edit_distance_item.target].is_whitespace or mem_src_tokens[edit_distance_item.target].is_punctuation:
                        num += 0.1
                    elif apply_small_change_adjustment and len(mem_src_tokens[edit_distance_item.target].text) <= 2:
                        num += 0.7
                    else:
                        num += 1.5
            elif edit_distance_item.operation == EditOperation.Delete:
                if edit_distance_item.resolution == EditDistanceResolution.Non:
                    if doc_src_tokens[edit_distance_item.source].is_whitespace or doc_src_tokens[edit_distance_item.source].is_punctuation:
                        num += 0.1
                    elif apply_small_change_adjustment and len(doc_src_tokens[edit_distance_item.source].text) <= 2:
                        num += 0.7
                    else:
                        num += 1.5

        if num2 <= 0:
            num2 = 1

        num10 = int(num * 100 / num2)

        if num3 > 5 and num5 > 5 and num7 + num8 > 0:
            num11 = num4 / num3
            num12 = num6 / num5
            num13 = num7 / (num7 + num8 + num9)
            num10 += AbstractScorer.compute_stopword_ratio_malus(num11, num12, num13, num3, num5, 7)
        elif num10 > 0 and num7 > 0:
            num14 = num7 / (num7 + num8)
            num15 = int(150 / num2)
            num10 += int(num14 * num15)

        if num10 > 100:
            return 0

        if num10 == 0 and num > 0:
            num10 += 1

        return 100 - num10, matching_placeholders_by_value, char_width_difference

    @staticmethod
    def compute_stopword_ratio_malus(src_stop_ratio, tgt_stop_ratio, identical_stop_ratio, src_words, tgt_words,
                                     max_penalty):
        if src_words <= 5 or tgt_words <= 5:
            return 0

        num = (src_stop_ratio + tgt_stop_ratio) / 2.0

        if num >= identical_stop_ratio:
            return 0
        elif num <= identical_stop_ratio * 0.65:
            return max_penalty
        elif num <= identical_stop_ratio * 0.8:
            return max_penalty // 2
        return 0

    def compare_with_edit_distance(self, doc_src_segment:AnnotatedSegment, doc_tgt_segment:AnnotatedSegment,
                                   document_placeables, result:ScoringResult, search_result:SearchResult, is_duplicate_search:bool, score_diagonal_only:bool):
        characters_normalize_safely = StringUtils.get_iso_language_code(doc_src_segment.segment.culture_name) != 'ko'
        apply_small_change_adjustment = AbstractScorer.apply_small_change_adjustment(doc_src_segment.segment.culture_name)
        segment_edit_distance_computer = SegmentEditDistanceComputer()
        disable_auto_substitutions = BuiltinRecognizers.RecognizeNone
        result.edit_distance, _ = segment_edit_distance_computer.compute_edit_distance(doc_src_segment.segment.tokens,
                                                                 search_result.memory_translation_unit.src_segment.tokens,
                                                                 is_duplicate_search,
                                                                 disable_auto_substitutions,
                                                                 characters_normalize_safely,
                                                                 apply_small_change_adjustment,
                                                                 is_duplicate_search or score_diagonal_only)
        result.resolved_placeables = 0
        self.target_tools.stem(search_result.memory_translation_unit.trg_segment)
        if search_result.memory_placeables is None:
            search_result.memory_placeables = search_result.memory_translation_unit.compute_placeables()
        src_tag_count = 0

        if document_placeables is not None:
            src_tag_count = len([plc for plc in document_placeables if plc.is_tag])
        AbstractScorer.compute_placeable_associations(search_result, doc_src_segment.segment, document_placeables)
        self.resolve_placeables(search_result, doc_src_segment.segment)
        self.check_placeable_format(doc_src_segment.segment, search_result, document_placeables)

        if is_duplicate_search == False:
            if src_tag_count == 0:
                self.check_and_delete_memory_tags(search_result)
            else:
                result.tag_mismatch = self.check_tag_mismatch_penalty(search_result, document_placeables)

        flag = self._normalize_char_width and CultureInfoExtensions.use_full_width(doc_src_segment.segment.culture_name)
        num, search_result.matching_placeholder_tokens, char_width_difference = self.compute_simplified_match_score(result.edit_distance,
                                                                                             doc_src_segment.segment.tokens,
                                                                                             search_result.memory_translation_unit.src_segment.tokens,
                                                                                             apply_small_change_adjustment,
                                                                                             flag)
        ##self.legacy_source_tokenizer is None, ignore some lines
        return num, char_width_difference

    @staticmethod
    def safe_get_token(segment: Segment, index: int) -> Token:
        if segment.tokens is None or index < 0 or index >= len(segment.tokens):
            return None
        return segment.tokens[index]

    @staticmethod
    def get_placeholder_key(tok: Token) -> str:
        if tok.type in [TokenType.Abbreviation, TokenType.Variable, TokenType.Acronym,
                        TokenType.Uri, TokenType.OtherTextPlaceable, TokenType.AlphaNumeric]:
            return tok.text
        elif tok.type in [TokenType.Date, TokenType.Number, TokenType.Measurement]:
            return tok.text
        return None

    @staticmethod
    def get_mem_source_placeable_indexes_per_unique_value(search_result: SearchResult) -> Dict[TokenType, Dict[str, Set[int]]]:
        dictionary = {}
        flag = False

        for placeable in search_result.memory_placeables:
            if placeable.source_token_index != -1 and placeable.target_token_index != -1:
                token = AbstractScorer.safe_get_token(search_result.memory_translation_unit.src_segment, placeable.source_token_index)
                if token:
                    placeholder_key = AbstractScorer.get_placeholder_key(token)
                    if placeholder_key:
                        if token.type not in dictionary:
                            dictionary[token.type] = {}
                        if placeholder_key not in dictionary[token.type]:
                            dictionary[token.type][placeholder_key] = {placeable.source_token_index}
                        else:
                            dictionary[token.type][placeholder_key].add(placeable.source_token_index)
                            flag = True

        return dictionary if flag else None

    @staticmethod
    def get_mem_source_indexes_by_doc_placeable_value(search_result, doc_src_segment):
        dictionary = {}
        for placeable_association in search_result.placeable_associations:
            if placeable_association.document.source_token_index != -1 and placeable_association.memory.source_token_index != -1:
                token = AbstractScorer.safe_get_token(doc_src_segment, placeable_association.document.source_token_index)
                if token:
                    placeholder_key = AbstractScorer.get_placeholder_key(token)
                    if placeholder_key:
                        if token.type not in dictionary:
                            dictionary[token.type] = {}
                        if placeholder_key not in dictionary[token.type]:
                            dictionary[token.type][placeholder_key] = {placeable_association.memory.source_token_index}
                        else:
                            dictionary[token.type][placeholder_key].add(placeable_association.memory.source_token_index)
        return dictionary

    @staticmethod
    def get_ambiguous_mem_source_placeables(search_result: SearchResult, doc_src_segment: Segment) -> Set[int]:
        ambiguous_mem_source_placeables = set()
        mem_source_placeable_indexes_per_unique_value = AbstractScorer.get_mem_source_placeable_indexes_per_unique_value(
            search_result)
        if not mem_source_placeable_indexes_per_unique_value:
            return ambiguous_mem_source_placeables

        mem_source_indexes_by_doc_placeable_value = AbstractScorer.get_mem_source_indexes_by_doc_placeable_value(
            search_result, doc_src_segment)
        list_of_sets = []

        for token_type, value_dict in mem_source_indexes_by_doc_placeable_value.items():
            list_of_sets.extend(value_dict.values())

        for token_type, value_dict in mem_source_placeable_indexes_per_unique_value.items():
            for unique_value, mem_source_indexes_for_this_value in value_dict.items():
                if len(mem_source_indexes_for_this_value) > 1:
                    if not any(
                            not mem_source_indexes_for_this_value.intersection(other_set)
                            for other_set in list_of_sets
                    ):
                        ambiguous_mem_source_placeables.update(mem_source_indexes_for_this_value)

        return ambiguous_mem_source_placeables

    def resolve_placeables(self, search_result, doc_src_segment):
        if search_result.placeable_associations is None or len(search_result.placeable_associations) == 0:
            return

        ambiguous_mem_source_placeables = AbstractScorer.get_ambiguous_mem_source_placeables(search_result,
                                                                                             doc_src_segment)
        scoring_result = search_result.scoring_result

        for placeable_association in search_result.placeable_associations:
            if placeable_association.memory.source_token_index not in ambiguous_mem_source_placeables:
                document = placeable_association.document
                memory = placeable_association.memory
                num = scoring_result.edit_distance.find_source_item_index(document.source_token_index)
                token = doc_src_segment.tokens[document.source_token_index]
                flag = token.is_substitutable and search_result.memory_translation_unit.src_segment.tokens[
                    memory.source_token_index].is_substitutable
                operation = scoring_result.edit_distance[num].operation

                if operation > EditOperation.Change:
                    if operation == EditOperation.Move:
                        if flag and self.settings.auto_localization_settings is not None:
                            flag = self.settings.auto_localization_settings.attempt_auto_substitution(token)
                        if flag:
                            scoring_result.edit_distance.set_resolution_at(num, EditDistanceResolution.Move)
                else:
                    if flag and not memory.is_tag:
                        if memory.target_token_index < 0 or not \
                        search_result.memory_translation_unit.trg_segment.tokens[
                            memory.target_token_index].is_substitutable:
                            flag = False
                        if flag and self.settings.auto_localization_settings is not None:
                            flag = self.settings.auto_localization_settings.attempt_auto_substitution(token)
                    if flag:
                        scoring_result.edit_distance.set_resolution_at(num, EditDistanceResolution.Substitution)
                        scoring_result.resolved_placeables += 1

    @staticmethod
    def compute_placeable_associations(search_result, doc_src_segment, source_placeables):
        if search_result.placeable_associations is None:
            if search_result.memory_placeables is not None and len(search_result.memory_placeables) != 0:
                if source_placeables is not None and len(source_placeables) != 0:
                    result = search_result.scoring_result
                    associations = []
                    bound_mem_placeables = [False] * len(search_result.memory_placeables)

                    for src_plc in source_placeables:
                        if src_plc.source_token_index >= 0:
                            ed_item = result.edit_distance.find_source_item_index(src_plc.source_token_index)
                            if ed_item < 0:
                                raise Exception('Internal Error')

                            operation = result.edit_distance[ed_item].operation
                            if operation > EditOperation.Change:
                                if operation == EditOperation.Move:
                                    for i in range(len(search_result.memory_placeables)):
                                        if not bound_mem_placeables[i]:
                                            placeable = search_result.memory_placeables[i]
                                            if placeable.source_token_index == result.edit_distance[
                                                ed_item].target and placeable.type == src_plc.type:
                                                associations.append(PlaceableAssociation(src_plc, placeable))
                                                bound_mem_placeables[i] = True
                                                break
                            else:
                                for mem_plc_idx in range(len(search_result.memory_placeables)):
                                    if not bound_mem_placeables[mem_plc_idx]:
                                        mem_plc = search_result.memory_placeables[mem_plc_idx]
                                        flag = mem_plc.source_token_index != result.edit_distance[ed_item].target
                                        if not flag:
                                            task_result = AbstractScorer.are_placeables_assignable(src_plc,
                                                                                                   mem_plc,
                                                                                                   doc_src_segment,
                                                                                                   search_result.memory_translation_unit.src_segment)
                                            flag = not task_result
                                        if not flag:
                                            associations.append(PlaceableAssociation(src_plc, mem_plc))
                                            bound_mem_placeables[mem_plc_idx] = True
                                            break

                    if len(associations) > 0:
                        search_result.placeable_associations = associations

    @staticmethod
    def are_placeables_assignable(src_plc, mem_plc, doc_segment, mem_segment):
        if not PlaceableAssociation.are_associable(src_plc, mem_plc):
            return False

        similarity = doc_segment.tokens[src_plc.source_token_index].get_similarity_param(
            mem_segment.tokens[mem_plc.source_token_index], True)
        if similarity >= SegmentElement.Similarity.IdenticalType:
            return True
        elif (src_plc.type == PlaceableType.StandaloneTag and mem_plc.type == PlaceableType.TextPlaceholder) or (
                src_plc.type == PlaceableType.TextPlaceholder and mem_plc.type == PlaceableType.StandaloneTag):
            if doc_segment.tokens[src_plc.source_token_index] is not None and mem_segment.tokens[
                mem_plc.source_token_index] is not None:
                if doc_segment.tokens[src_plc.source_token_index].type == TokenType.Tag and mem_segment.tokens[
                    mem_plc.source_token_index].type == TokenType.Tag:
                    return True
        return False

    def compare_tokens(self, doc_src_segment:AnnotatedSegment, doc_tgt_segment:AnnotatedSegment, document_placeables,
                       result:ScoringResult, search_result:SearchResult, is_duplicate_search:bool, score_diagonal_only:bool):
        num = 0
        flag = False

        if doc_src_segment.segment.tokens is not None:
            if SegmentEditDistanceComputer.can_compute_edit_distance(len(doc_src_segment.segment.tokens), len(search_result.memory_translation_unit.src_segment.tokens)):
                num, flag = self.compare_with_edit_distance(doc_src_segment, doc_tgt_segment, document_placeables, result, search_result, is_duplicate_search, score_diagonal_only)
            else:
                num = 100 if str(doc_src_segment.segment) == str(search_result.memory_translation_unit.src_segment) else 0
        return num, flag

    def compute_scores(self, search_result:SearchResult, doc_src_segment:AnnotatedSegment, doc_tgt_segment:AnnotatedSegment,
                       document_places:[], tu_context_data:TuContextData, is_duplicate_search:bool,
                       used_index:FuzzyIndexes, score_diagonal_only:bool = False, skip_filters:bool = True):
        char_width_difference = False
        scoring_result = ScoringResult()

        if search_result.scoring_result is None:
            search_result.scoring_result = scoring_result
        else:
            scoring_result = search_result.scoring_result

        if self.settings.is_concordance_search:
            num = self.get_concordance_score(search_result, doc_src_segment, doc_tgt_segment)
        else:
            if doc_src_segment.segment.tokens is None:
                self.source_tools.ensure_tokenized_segment(doc_src_segment.segment)
            self.source_tools.stem(doc_src_segment.segment)
            self.source_tools.stem(search_result.memory_translation_unit.src_segment)
            num, char_width_difference = self.compare_tokens(doc_src_segment, doc_tgt_segment, document_places, scoring_result, search_result, is_duplicate_search, score_diagonal_only)

        if num > 100:
            num = 100
        elif num < 0:
            num = 0
        scoring_result.base_score = num
        search_result.scoring_result.text_context_match = TextContextMatch.NoMatch

        if num <= 0:
            return
        if scoring_result.is_exact_match and self.settings.is_concordance_search == False:
            self.check_different_target(search_result, document_places, doc_tgt_segment)
            self.check_contexts(search_result, tu_context_data)

        self.apply_penalties(search_result, char_width_difference)

    def check_text_context(self, search_result, left_context):
        search_result.scoring_result.text_context_match = TextContextMatch.NoMatch
        if left_context is None or search_result.memory_translation_unit.contexts is None:
            return
        text_context_match = TextContextMatch.NoMatch
        for tu_context in search_result.memory_translation_unit.contexts.values():
            if self._text_context_match_type == TextContextMatchType.PrecedingSourceAndTarget:
                text_context_match = TextContextMatch.SourceMatch
            if left_context.context2 == tu_context.context2:
                text_context_match = TextContextMatch.SourceTargetMatch
                if self._text_context_match_type == TextContextMatchType.PrecedingAndFollowingSource:
                    text_context_match = TextContextMatch.PrecedingAndFollowingSourceMatch
                    break
                break
        search_result.scoring_result.text_context_match = text_context_match

    @staticmethod
    def check_structure_context_(settings, search_result, current_structure_context_override):
        scoring_result = search_result.scoring_result
        scoring_result.is_structure_context_match = False
        text = current_structure_context_override or (settings.current_structure_context if settings else None)

        if not text or not search_result.memory_translation_unit.field_values:
            return

        multiple_string_field_value = search_result.memory_translation_unit.field_values.get(Field.STRUCTURE_CONTEXT_FIELD_NAME)
        if multiple_string_field_value:
            scoring_result.is_structure_context_match = multiple_string_field_value.has_value(text)

    def check_structure_context(self, search_result, current_structure_context_override):
        AbstractScorer.check_structure_context_(self.settings, search_result, current_structure_context_override)

    @staticmethod
    def check_id_context(search_result, id_context):
        if not id_context:
            return
        if not search_result.memory_translation_unit.id_contexts:
            return
        search_result.scoring_result.id_context_match = search_result.memory_translation_unit.id_contexts.has_value(
            id_context)

    def check_contexts(self, search_result, tu_context_data):
        if tu_context_data is None:
            return
        self.check_text_context(search_result, tu_context_data.text_context)
        self.check_structure_context(search_result, tu_context_data.current_structure_context_override)
        AbstractScorer.check_id_context(search_result, tu_context_data.id_context)

    def are_target_segments_equal(self, doc_trg_seg, mem_trg_seg, search_result, document_placeables):
        flag = False
        if not SegmentEditDistanceComputer.can_compute_edit_distance(len(doc_trg_seg.tokens), len(mem_trg_seg.tokens)):
            flag = doc_trg_seg.to_string() == mem_trg_seg.to_string()
        else:
            segment_edit_distance_computer = SegmentEditDistanceComputer(False)
            auto_localization_settings = self.settings.auto_localization_settings
            builtin_recognizers = auto_localization_settings.disable_auto_substitution if auto_localization_settings else BuiltinRecognizers.RecognizeNone

            item2, _ = segment_edit_distance_computer.compute_edit_distance(
                doc_trg_seg.tokens,
                mem_trg_seg.tokens,
                True,
                builtin_recognizers,
                True,
                True,
                False
            )
            flag2 = True

            if item2.distance > 0:
                num = 0
                while num < len(item2.items) and flag2:
                    item = item2.items[num]
                    operation = item.operation

                    if operation != EditOperation.Change:
                        if EditOperation.Move <= operation <= EditOperation.Delete:
                            flag2 = False
                    else:
                        if search_result.scoring_result.resolved_placeables == 0 or not search_result.placeable_associations:
                            flag2 = False
                        else:
                            flag2 = any(
                                x.document.target_token_index == item.source and x.memory.target_token_index == item.target
                                for x in search_result.placeable_associations
                            )
                            if not flag2:
                                flag2 = any(
                                    x.document.target_token_index == item.source
                                    for x in search_result.placeable_associations
                                ) and any(
                                    x.memory.target_token_index == item.target
                                    for x in search_result.placeable_associations
                                )

                        if not flag2 and isinstance(doc_trg_seg.tokens[item.source], TagToken) and isinstance(
                                mem_trg_seg.tokens[item.target], TagToken):
                            flag2 = (
                                    document_placeables is not None and
                                    any(x.source_token_index == -1 and x.target_token_index == item.source for x in
                                        document_placeables) and
                                    search_result.memory_placeables is not None and
                                    any(x.source_token_index == -1 and x.target_token_index == item.target for x in
                                        search_result.memory_placeables)
                            )

                    num += 1

            flag = flag2
        return flag

    def check_different_target(self, search_result, document_placeables, doc_trg_segment):
        if doc_trg_segment is not None:
            mem_trg_segment = self.get_annotated_segment(search_result.memory_translation_unit.trg_segment, True,
                                                         True, True)

            if not mem_trg_segment.segment.tokens:
                self.target_tools.ensure_tokenized_segment(mem_trg_segment.segment)

            if not doc_trg_segment.segment.tokens:
                self.target_tools.ensure_tokenized_segment(doc_trg_segment.segment)

            flag = len(doc_trg_segment.segment.tokens) == len(mem_trg_segment.segment.tokens)

            if flag:
                segment_hash_doc = AbstractScorer.get_segment_hash(doc_trg_segment)
                segment_hash_mem = AbstractScorer.get_segment_hash(mem_trg_segment)
                flag = segment_hash_doc == segment_hash_mem

            flag2 = flag

            if flag2:
                flag2 = self.are_target_segments_equal(doc_trg_segment.segment, mem_trg_segment.segment,
                                                                   search_result, document_placeables)

            if not flag2:
                search_result.scoring_result.target_segment_differs = True

    def apply_penalties(self, search_result:SearchResult, char_width_difference:bool):
        if char_width_difference:
            self.apply_char_width_penalty(search_result)
        self.apply_filter_penalties(search_result)
        self.apply_provider_penalty(search_result)
        self.apply_alignment_penalty(search_result)
        self.apply_confirm_level_penalties(search_result)

    def apply_alignment_penalty(self, search_result:SearchResult):
        penalty = self.settings.find_penalty(PenaltyType.Alignment)
        if penalty is None:
            return
        if (search_result.memory_translation_unit.origin != TranslationUnitOrigin.Alignment or
            search_result.memory_translation_unit.system_fields.creation_date != search_result.memory_translation_unit.system_fields.change_date):
            return
        if penalty.malus > 0:
            search_result.scoring_result.apply_penalty(penalty)

    def apply_confirm_level_penalty(self, search_result:SearchResult, confirmation_level:ConfirmationLevel, pt:PenaltyType):
        penalty = self.settings.find_penalty(pt)
        if (penalty is not None and
            penalty.malus > 0 and
            search_result.memory_translation_unit.confirmation_level == confirmation_level):
            search_result.scoring_result.apply_penalty(penalty)

    def apply_confirm_level_penalties(self, search_result:SearchResult):
        self.apply_confirm_level_penalty(search_result, ConfirmationLevel.Unspecified, PenaltyType.NotTranslated)
        self.apply_confirm_level_penalty(search_result, ConfirmationLevel.Draft, PenaltyType.Draft)
        self.apply_confirm_level_penalty(search_result, ConfirmationLevel.Translated, PenaltyType.Translated)
        self.apply_confirm_level_penalty(search_result, ConfirmationLevel.ApprovedSignOff, PenaltyType.ApprovedSignOff)
        self.apply_confirm_level_penalty(search_result, ConfirmationLevel.ApprovedTranslation, PenaltyType.ApprovedTranslation)
        self.apply_confirm_level_penalty(search_result, ConfirmationLevel.RejectedTranslation, PenaltyType.RejectedTranslation)
        self.apply_confirm_level_penalty(search_result, ConfirmationLevel.RejectedSignOff, PenaltyType.RejectedSignOff)

    def apply_provider_penalty(self, search_result:SearchResult):
        penalty = self.settings.find_penalty(PenaltyType.ProviderPenalty)
        if penalty is None:
            return
        if penalty.malus > 0:
            search_result.scoring_result.apply_penalty(penalty)

    def apply_char_width_penalty(self, search_result:SearchResult):
        penalty = self.settings.find_penalty(PenaltyType.CharacterWidthDifference)
        if penalty is None:
            return
        if penalty.malus > 0:
            search_result.scoring_result.apply_penalty(penalty)

    def apply_filter_penalties(self, search_result:SearchResult):
        scoring_result = search_result.scoring_result
        if self.settings.filters is None:
            return
        #plmod
        return

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

