from CultureInfoExtensions import CultureInfoExtensions
from Segment import Segment
from StringUtils import StringUtils
from TagToken import TagToken
from TokenizerHelper import TokenizerHelper
import numpy as np
from collections import Counter
from CaseAwareCharSubsequenceScoreProvider import CaseAwareCharSubsequenceScoreProvider
from typing import *
from SequenceAlignmentComputer import *

T = TypeVar("T")

class TermFinderResult:
    def __init__(self):
        self.matching_ranges = []
        self.score = 0

class TermFinder:
    @staticmethod
    def find_terms(search_segment:Segment, text_segment:Segment, expect_continuous_match:bool, use_width_normalization:bool) -> TermFinderResult:
        if TokenizerHelper.tokenizes_to_words(search_segment.culture_name) == False:
            pass#mod
        use_character_decomposition = StringUtils.get_iso_language_code(search_segment.culture_name) != 'ko'
        return TermFinder.find_terms_word_based(search_segment, text_segment, expect_continuous_match, use_character_decomposition, use_width_normalization)

    @staticmethod
    def compute_token_association_scores(search_segment, text_segment, use_character_decomposition, normalize_widths):
        # Initialize the scores array
        scores = np.zeros((len(search_segment.tokens), len(text_segment.tokens)), dtype=int)
        temp_array = []
        temp_index = 0
        flag = False

        # Create the scorer object
        scorer = CaseAwareCharSubsequenceScoreProvider(use_character_decomposition, normalize_widths)

        # Iterate through tokens in the search segment
        for i, token in enumerate(search_segment.tokens):
            if not token.is_whitespace and not isinstance(token, TagToken):
                for j, token2 in enumerate(text_segment.tokens):
                    if not token2.is_whitespace and not isinstance(token2, TagToken):
                        scores[i, j] = 0
                        aligned_substrings = SequenceAlignmentComputer.compute_longest_common_subsequence(
                            list(token.text), list(token2.text), 0, scorer, None
                        )
                        if aligned_substrings:
                            num2 = sum(x.length for x in aligned_substrings)
                            if num2 != 0:
                                num3 = 2.0 * num2 / (len(token.text) + len(token2.text))
                                if num3 >= 0.7:
                                    scores[i, j] = int(num3 * 100)
                                    if scores[i, j] < 100:
                                        temp_array.append(j)
                                        temp_index += 1
                                    else:
                                        flag = True

                if flag:
                    for idx in temp_array[:temp_index]:
                        scores[i, idx] = 0
                    temp_array = []
                    temp_index = 0
                    flag = False

        return scores

    @staticmethod
    def find_terms_word_based(search_segment, text_segment, expect_continuous_match, use_character_decomposition,
                              use_width_normalization):
        normalize_widths = use_width_normalization and CultureInfoExtensions.use_full_width(text_segment.culture)
        flag = False
        association_scores = TermFinder.compute_token_association_scores(
            search_segment, text_segment, use_character_decomposition, normalize_widths
        )
        token_scores = [0] * len(search_segment.tokens)
        term_finder_result = TermFinderResult()
        term_finder_result.matching_ranges = []
        bit_array = [False] * len(text_segment.tokens)
        search_tokens = []
        matched_tokens = []
        num_non_whitespace_tokens = 0

        for i, search_token in enumerate(search_segment.tokens):
            if not search_token.is_whitespace:
                num_non_whitespace_tokens += 1
                search_tokens.append(search_token.text.lower())

            for j, text_token in enumerate(text_segment.tokens):
                if association_scores[i][j] > 0:
                    if not bit_array[j]:
                        term_finder_result.matching_ranges.append(text_token.span)
                        bit_array[j] = True
                    if association_scores[i][j] > token_scores[i]:
                        token_scores[i] = association_scores[i][j]

        if num_non_whitespace_tokens == 0:
            return None

        avg_score = sum(token_scores) // num_non_whitespace_tokens
        token_dict = {}

        for k, text_token in enumerate(text_segment.tokens):
            if bit_array[k]:
                if matched_tokens:
                    previous_index = TermFinder.get_previous_word_token_index(text_segment.tokens, k)
                    if previous_index > -1 and not bit_array[previous_index]:
                        matched_tokens.append("#")
                token_text = text_token.text.lower()
                if token_text not in token_dict:
                    token_dict[token_text] = 0
                matched_tokens.append(token_text)

        search_string = "~".join(search_tokens)
        matched_string = "~".join(matched_tokens)
        match_score = 0

        if (expect_continuous_match or avg_score < 100) and search_string and matched_string:
            scorer = CaseAwareCharSubsequenceScoreProvider(use_character_decomposition, normalize_widths)
            scorer_no_width_norm = CaseAwareCharSubsequenceScoreProvider(use_character_decomposition, False)
            source = list(search_string)
            target = list(matched_string)

            lcs = SequenceAlignmentComputer.compute_longest_common_subsequence(source, target, 1, scorer, None)
            lcs_length = sum(substring.length for substring in lcs)

            weight = 1.0
            if flag and lcs_length > 0:
                lcs_no_width_norm = SequenceAlignmentComputer.compute_longest_common_subsequence(
                    source, target, 1, scorer_no_width_norm, None
                )
                weighted_score = sum(substring.score for substring in lcs)
                no_width_score = sum(substring.score for substring in lcs_no_width_norm)
                adjusted_score = weighted_score + (weighted_score - no_width_score) * 0.6
                weight = adjusted_score / (lcs_length * 2)
                if weight > 1.0:
                    flag = False

            unique_tokens_count = TermFinder.remove_token_duplicates(matched_string, lcs)
            token_overlap = 2 * min(num_non_whitespace_tokens, len(token_dict)) / (
                        num_non_whitespace_tokens + len(token_dict))
            match_score = int((75 + 25 * token_overlap) * 2 * lcs_length / (len(search_string) + unique_tokens_count))

            if flag:
                match_score = int(weight * match_score)

            match_score = max(0, min(match_score, 100))

        if avg_score == 100 and match_score > 0:
            term_finder_result.score = (200 + match_score) // 3
        else:
            term_finder_result.score = max(avg_score, match_score)

        return term_finder_result

    @staticmethod
    def get_previous_word_token_index(tokens:[], current_token_index:int) -> int:
        """
            Finds the index of the previous token that is a word.

            :param tokens: A list of Token objects.
            :param current_token_index: The current token index to start searching from.
            :return: The index of the previous word token, or -1 if none is found.
            """
        for i in range(current_token_index - 1, -1, -1):
            if tokens[i].is_word:  # Assuming the Token class has an attribute or method `is_word`
                return i
        return -1

    @staticmethod
    def remove_token_duplicates(trg_concat:str, lcs:[]):
        if lcs is None:
            raise Exception('lcs is null')
        if len(lcs) == 0:
            raise Exception('lcs is empty')

        dictionary = {}
        str_prefix = trg_concat[:lcs[0].target.start]
        text = trg_concat[lcs[0].target.start:lcs[0].target.start + lcs[0].target.length]
        str_suffix = trg_concat[lcs[0].target.start + lcs[0].target.length:]

        for text_segment in (str_prefix + str_suffix).split("~"):
            if text_segment not in text and text_segment not in dictionary and text_segment != "#":
                dictionary[text_segment] = 0

        if len(dictionary) > 0:
            total_length = len(text) + sum(len(key) for key in dictionary.keys()) + len(dictionary)
            return total_length

        return len(text)

