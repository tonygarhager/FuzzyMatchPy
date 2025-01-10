from FST import FST
from FSTRecognizer import FSTRecognizer
from Resource import LanguageResourceType
from NumberFSTEx import NumberFSTEx
from NumberPatternComputer import NumberPatternComputer
from NumberToken import NumberToken, NumericSeparator, Sign
from Recognizer import *
from LanguageResources import LanguageResources
from CultureInfoExtensions import CultureInfoExtensions
from typing import List, Optional

from ResourceStorage import ResourceStatus
from SeparatorCombination import SeparatorCombination
from TokenBundle import PrioritizedToken, TokenBundle


class NumberFSTRecognizer(Recognizer):
    def __init__(self, settings: 'RecognizerSettings', culture: str, priority: int,
                 fst_recognizer: FSTRecognizer, number_fst_ex: NumberFSTEx) -> None:
        super().__init__(settings, TokenType.Number, priority, "Number", "NumberFSTRecognizer", False, culture)

        self._fst_recognizer = fst_recognizer
        self._culture_specific_text_constraints = self.get_culture_specific_text_constraints(culture)
        self._number_fst_ex = number_fst_ex
        NumberFSTRecognizer.set_additional_options(self, culture)

    @staticmethod
    def create(settings:RecognizerSettings, access:LanguageResources, culture_name:str, priority:int) -> Recognizer:
        result = NumberFSTRecognizer(settings, culture_name, priority, access)
        result = NumberFSTRecognizer.set_additional_options(result, culture_name)
        return result

    @staticmethod
    def set_additional_options(result, culture_name:str):
        result.only_if_followed_by_nonword_character = CultureInfoExtensions.use_blank_as_word_separator(culture_name)

        if result.additional_terminators is None:
            result.additional_terminators = CharacterSet()

        result.additional_terminators.add('-')
        result.override_fallback_recognizer = True
        return result

    @staticmethod
    def get_separators_signature_string(number_fst_ex: Optional['NumberFSTEx']) -> str:
        if number_fst_ex is None or number_fst_ex.separator_combinations is None:
            return ""

        result: List[str] = []
        num = 1
        for separator_combination in number_fst_ex.separator_combinations:
            string_builder = f"{num} {separator_combination.group_separators}\t{separator_combination.decimal_separators}\t"
            result.append(string_builder)
            num += 1

        result.sort()
        return ''.join(result)

    def get_signature(self, culture: str) -> str:
        customisations_string = NumberFSTRecognizer.get_separators_signature_string(self._number_fst_ex)

        if CultureInfoExtensions.use_full_width(culture):
            text = super().get_signature(culture)  # Assuming base_get_signature is a method in the base class
            text2 = text + "Number1" + customisations_string
        else:
            text3 = super().get_signature(culture) + "Number0" + customisations_string
            text2 = text3

        return text2

    @property
    def separator_combinations_computed(self) -> 'List[SeparatorCombination]':
        if self._number_fst_ex is None:
            return None
        return self._number_fst_ex.separator_combinations

    @staticmethod
    def append_word_terminator(culture: str) -> bool:
        return CultureInfoExtensions.use_blank_as_word_separator(culture) and StringUtils.get_iso_language_code(culture) != "ko"

    def get_culture_specific_text_constraints(self,
                                              culture: str) -> 'Optional[Callable[[str, int, Token], bool]]':
        if NumberFSTRecognizer.append_word_terminator(culture):
            return None
        two_letter_iso_language_name = StringUtils.get_iso_language_code(culture)
        if two_letter_iso_language_name == "ko":
            return self.korean_text_constraints
        return None

    def korean_text_constraints(self, s: str, p: int, t: 'Token') -> bool:
        return self.default_text_constraints(s, p, True) or (p < len(s) and StringUtils.is_korean_char(s[p]))

    @staticmethod
    def load(settings, culture, priority, accessor):
        if culture is None:
            raise ValueError("culture cannot be None")

        resource_status = accessor.get_resource_status(culture, LanguageResourceType.NumberFST, True)
        number_fst_recognizer = None

        if resource_status == ResourceStatus.NotAvailable:
            number_fst_recognizer = None
        else:
            array = accessor.get_resource_data(culture, LanguageResourceType.NumberFST, True)
            if array is None:
                raise Exception("EMSG_ResourceNotAvailable")

            fst = FST.create(array)
            number_fst_ex = None

            if accessor.get_resource_status(culture, LanguageResourceType.NumberFSTEx,
                                            True) != ResourceStatus.NotAvailable:
                array = accessor.get_resource_data(culture, LanguageResourceType.NumberFSTEx, True)
                if array is None:
                    raise Exception("EMSG_ResourceNotAvailable")

                number_fst_ex = NumberFSTEx.from_binary(array)

            number_fst_recognizer = NumberFSTRecognizer(settings, culture, priority, FSTRecognizer(fst, culture),
                                                        number_fst_ex)

        return number_fst_recognizer

    def recognize(self, s: str, from_index: int, allow_token_bundles: bool, num:int):
        num = 0
        matches = self._fst_recognizer.compute_matches(s, from_index, False, 0, True)

        if matches is None or len(matches) == 0:
            return None, 0

        prioritized_tokens = None
        for match in matches:
            if self.verify_context_constraints(s, match.index + match.length, None):
                if match.output is None or len(match.output) != match.length or match.length == 0:
                    raise Exception("Internal error: invalid number FST")

                if num == 0:
                    num = match.length

                text = s[match.index: match.index + match.length]
                output = match.output
                number_fst_ex = self._number_fst_ex
                separator_combinations = number_fst_ex.separator_combinations if number_fst_ex else None
                number_token = NumberFSTRecognizer.parse_number(text, output, separator_combinations, self.culture_name)

                if number_token:
                    if prioritized_tokens is None:
                        prioritized_tokens = []
                    prioritized_tokens.append(PrioritizedToken(number_token, 0))

        if prioritized_tokens is None or len(prioritized_tokens) == 0:
            return None, 0

        self.evaluate_and_sort_candidates(prioritized_tokens)

        if allow_token_bundles and len(prioritized_tokens) > 1:
            return TokenBundle.create_from_prioritized_token_list(prioritized_tokens), num

        return prioritized_tokens[0].token, num

    @staticmethod
    def create_fst(culture, append_word_terminator, nfd, treat_first_separators_as_primary_separators):
        text = NumberPatternComputer.compute_fst_pattern(nfd, treat_first_separators_as_primary_separators,
                                                         append_word_terminator)
        fst = FST.create(text)
        fst.make_deterministic()
        return fst

    def evaluate_and_sort_candidates(self, candidates):
        if not candidates:
            return

        for prioritized_token in candidates:
            number_token = prioritized_token.token if isinstance(prioritized_token.token, NumberToken) else None
            num = 0
            if number_token and (
                    number_token.decimal_separator == NumericSeparator.Alternate or number_token.group_separator == NumericSeparator.Alternate):
                num += 1
            prioritized_token.priority = self._priority - num

        candidates.sort(key=lambda x: x.priority, reverse=True)

    @staticmethod
    def parse_number(surface, output, separator_combinations_computed, culture):
        if surface is None:
            raise ValueError("surface cannot be None")
        if output is None:
            raise ValueError("output cannot be None")

        string_builder = []
        string_builder2 = []
        string_builder3 = []
        c = '\0'
        c2 = '\0'
        sign = Sign.Non
        numeric_separator = NumericSeparator.Non
        numeric_separator2 = NumericSeparator.Non
        num = 0
        num2 = len(surface)

        if NumberPatternComputer.AllowTrailingSign and num2 > 0:
            c3 = output[num2 - 1]
            c4 = surface[num2 - 1]
            if c3 == '-' or c3 == '+':
                sign = Sign.Minus if c3 == '-' else Sign.Plus
                string_builder.append(c4)
                num2 -= 1

        for i in range(num2):
            c5 = surface[i]
            c3 = output[i]
            if num == 0:
                if c3 == '-' or c3 == '+':
                    sign = Sign.Minus if c3 == '-' else Sign.Plus
                    string_builder.append(c5)
                    num = 1
                else:
                    if not ('0' <= c3 <= '9'):
                        raise ValueError(f"Unexpected input in {surface}/{output} at position {i}")
                    string_builder2.append(c3)
                    num = 1
            elif num == 1:
                if not ('0' <= c3 <= '9'):
                    if c3 <= 'G':
                        if c3 == 'D':
                            pass  # skip to next case
                        elif c3 == 'G':
                            pass
                    else:
                        if c3 == 'd':
                            pass
                        elif c3 == 'g':
                            pass
                    if numeric_separator != NumericSeparator.Non:
                        continue
                    if separator_combinations_computed and len(separator_combinations_computed) > 0:
                        c = c5
                    if c3 == 'g':
                        numeric_separator = NumericSeparator.Alternate
                        c = c5
                        continue
                    numeric_separator = NumericSeparator.Primary
                else:
                    string_builder2.append(c3)
                    num = 1
            elif num == 2:
                if not ('0' <= c3 <= '9'):
                    raise ValueError(f"Unexpected input in {surface}/{output} at position {i}")
                string_builder3.append(c3)
                num = 2
            else:
                raise ValueError("Internal error")

        return NumberToken(surface, numeric_separator, numeric_separator2, c, c2, sign,
                           ''.join(string_builder) if string_builder else None,
                           ''.join(string_builder2) if string_builder2 else None,
                           ''.join(string_builder3) if string_builder3 else None)

