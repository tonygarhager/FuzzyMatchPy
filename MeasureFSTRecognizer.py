from CultureInfoExtensions import CultureInfoExtensions
from CustomUnitDefinition import Unit
from FST import FST
from FSTRecognizer import FSTRecognizer
from MeasureFSTEx import MeasureFSTEx
from NumberFSTEx import NumberFSTEx
from NumberFSTRecognizer import NumberFSTRecognizer
from NumberPatternComputer import NumberPatternComputer
from NumberToken import MeasureToken, NumericSeparator
from Recognizer import *
from Resource import LanguageResourceType
from ResourceStorage import ResourceStatus
from TokenBundle import PrioritizedToken, TokenBundle


class MeasureFSTRecognizer(Recognizer):
    def __init__(self, settings, culture, priority, fst_recognizer, number_fst_ex, measure_fst_ex):
        super().__init__(settings, TokenType.Measurement, priority, "Measurement", "MeasureFSTRecognizer", False,
                         culture)
        self._culture_specific_text_constraints = self.get_culture_specific_text_constraints(culture)
        self._check_width_variants = CultureInfoExtensions.use_full_width(culture)
        self._number_fst_ex = number_fst_ex
        self._measure_fst_ex = measure_fst_ex
        self._fst_recognizer = fst_recognizer

    @property
    def unit_definitions(self):
        measure_fst_ex = self._measure_fst_ex
        if measure_fst_ex is None:
            return None
        return measure_fst_ex.unit_definitions

    def get_signature(self, culture):
        sb = []
        sb.append(NumberFSTRecognizer.get_separators_signature_string(self._number_fst_ex))
        unit_definitions_list = []
        measure_fst_ex = self._measure_fst_ex
        if measure_fst_ex and measure_fst_ex.unit_definitions:
            for key, value in measure_fst_ex.unit_definitions.items():
                string_builder = []
                text = ''
                text2 = ''
                if value:
                    text = str(value.unit)
                    text2 = value.category_name if value.category_name else ''
                string_builder.append(key)
                string_builder.append(" ")
                string_builder.append(text)
                string_builder.append(" ")
                string_builder.append(text2)
                unit_definitions_list.append("".join(string_builder))

        unit_definitions_list.sort()

        for text3 in unit_definitions_list:
            sb.append(text3 + "|")

        if CultureInfoExtensions.use_full_width(culture):
            text4 = super().get_signature(culture)
            text7 = text4 + "Measure1" + "".join(sb)
        else:
            text8 = super().get_signature(culture)
            text7 = text8 + "Measure0" + "".join(sb)

        return text7

    @staticmethod
    def append_word_terminator(culture):
        return NumberFSTRecognizer.append_word_terminator(culture)

    @staticmethod
    def set_additional_options(result):
        result.only_if_followed_by_nonword_character = True
        result.override_fallback_recognizer = True

    def get_culture_specific_text_constraints(self, culture):
        if MeasureFSTRecognizer.append_word_terminator(culture):
            return None

        region_neutral_name = StringUtils.get_iso_language_code(culture)
        if region_neutral_name == "ko":
            return lambda s, p, t: MeasureFSTRecognizer.korean_text_constraints(self, s, p, t)

        return None

    @staticmethod
    def korean_text_constraints(r, s, p, t):
        if r.default_text_constraints(s, p, True):
            return True

        measure_token = t if isinstance(t, MeasureToken) else None
        if not measure_token or not measure_token.unit_string or not measure_token.text:
            return False

        if p >= len(s) or not StringUtils.is_korean_char(s[p]):
            return False

        if measure_token.unit == Unit.Currency and measure_token.text[0] == measure_token.unit_string[0]:
            return True

        return not any(StringUtils.is_korean_char(x) for x in measure_token.unit_string)

    @staticmethod
    def create(settings, culture, priority, culture_metadata_manager):
        if culture is None:
            raise ValueError("culture cannot be None")

        fst = MeasureFSTRecognizer.create_fst(culture, MeasureFSTRecognizer.append_word_terminator(culture),
                                              culture_metadata_manager)
        fst2 = fst
        measure_fst_recognizer = MeasureFSTRecognizer(settings, culture, priority, FSTRecognizer(fst2, culture), None,
                                                      None)
        MeasureFSTRecognizer.set_additional_options(measure_fst_recognizer)

        return measure_fst_recognizer

    @staticmethod
    def load(settings, culture:str, priority:int, accessor):
        if culture is None:
            raise ValueError("culture cannot be None")

        resource_status = accessor.get_resource_status(culture, LanguageResourceType.MeasurementFST, True)
        if resource_status == ResourceStatus.NotAvailable:
            recognizer = None
        else:
            array = accessor.get_resource_data(culture, LanguageResourceType.MeasurementFST, True)
            if array is None:
                raise Exception("ErrorMessages.EMSG_RESOURCE_NOT_AVAILABLE")

            fst = FST.create(array)
            number_fst_ex = None
            measure_fst_ex = None

            if accessor.get_resource_status(culture, LanguageResourceType.NumberFSTEx,
                                            True) != ResourceStatus.NotAvailable:
                array = accessor.get_resource_data(culture, LanguageResourceType.NumberFSTEx, True)
                if array is None:
                    raise Exception("ErrorMessages.EMSG_RESOURCE_NOT_AVAILABLE")
                number_fst_ex = NumberFSTEx.from_binary(array)

            if accessor.get_resource_status(culture, LanguageResourceType.MeasurementFSTEx,
                                            True) != ResourceStatus.NotAvailable:
                array = accessor.get_resource_data(culture, LanguageResourceType.MeasurementFSTEx, True)
                if array is None:
                    raise Exception("ErrorMessages.EMSG_RESOURCE_NOT_AVAILABLE")
                measure_fst_ex = MeasureFSTEx.from_binary(array)

            measure_fst_recognizer = MeasureFSTRecognizer(
                settings, culture, priority, FSTRecognizer(fst, culture), number_fst_ex, measure_fst_ex)
            MeasureFSTRecognizer.set_additional_options(measure_fst_recognizer)

            recognizer = measure_fst_recognizer

        return recognizer

    def recognize(self, s, from_idx, allow_token_bundles, consumed_length):
        consumed_length = 0
        matches = self._fst_recognizer.compute_matches(s, from_idx, False, 0, True)
        if matches is None or len(matches) == 0:
            return None, 0

        candidates = None
        for match in matches:
            if self._culture_specific_text_constraints is not None or self.verify_context_constraints(s,
                                                                                                      match.index + match.length,
                                                                                                      None):
                if match.output is None or len(match.output) != match.length or match.length == 0:
                    raise Exception("Internal error: invalid measurement FST")

                if consumed_length == 0:
                    consumed_length = match.length

                measure_token = self.parse(s[match.index:match.index + match.length], match.output)
                if measure_token is not None:
                    if self._culture_specific_text_constraints is not None and not self.verify_context_constraints(s,
                                                                                                                   match.index + match.length,
                                                                                                                   measure_token):
                        continue
                    if candidates is None:
                        candidates = []
                    candidates.append(PrioritizedToken(measure_token, 0))
                match = None

        if candidates is None or len(candidates) == 0:
            return None, 0
        else:
            MeasureFSTRecognizer.evaluate_and_sort_candidates(candidates, self._priority)
            if allow_token_bundles and len(candidates) > 1:
                return TokenBundle.create_from_prioritized_token_list(candidates), consumed_length
            else:
                return candidates[0].token, consumed_length
    @staticmethod
    def check_no_full_width(s):
        return s is None or s == StringUtils.full_width_to_half_width(s)

    @staticmethod
    def check_no_half_width(s):
        return s is None or s == StringUtils.half_width_to_full_width2(s)

    @staticmethod
    def check_not_mixed_width(s):
        return MeasureFSTRecognizer.check_no_full_width(s) or MeasureFSTRecognizer.check_no_half_width(s)

    @staticmethod
    def create_fst(culture, append_word_terminator, culture_metadata_manager):
        language_base = culture_metadata_manager.get_language(culture)
        culture_info = language_base.get_culture_info()
        culture_info2 = culture_info
        number_format_data = NumberPatternComputer.get_number_format_data(culture_info2, True, True)
        return MeasureFSTRecognizer.create_fst(culture_info2, append_word_terminator, number_format_data, None, False,
                                               True, culture_metadata_manager)

    @staticmethod
    def create_fst(culture, append_word_terminator, nfd, custom_units, custom_units_only,
                   treat_first_separators_as_primary_separators, culture_metadata_manager):
        text = NumberPatternComputer.compute_fst_pattern(nfd, treat_first_separators_as_primary_separators, False)
        sb = text
        sb.append("(")
        flag = True
        NumberPatternComputer.append_disjunction(sb, StringUtils.blanks, 'U', flag)
        sb.append(")?(")

        if custom_units_only and (custom_units is None or len(custom_units) == 0):
            raise Exception("customUnitsOnly specified but none were provided")

        include_width_variants = CultureInfoExtensions.use_full_width(culture)
        units = set()

        if custom_units:
            for unit in custom_units:
                units.add(unit)
                if include_width_variants:
                    if not MeasureFSTRecognizer.check_not_mixed_width(unit):
                        raise Exception(f"Custom unit string has mixed character widths: {unit}")
                    units.add(StringUtils.full_width_to_half_width(unit))
                    units.add(StringUtils.half_width_to_full_width2(unit))

        if not custom_units_only:
            list_ = culture_metadata_manager.get_all_unit_metadata(culture.name)
            for unit_metadata in list_:
                for label_value_set in unit_metadata.label_value_sets:
                    for text3 in label_value_set.label_value_conditions:
                        hash_set = set([text3.label])
                        if include_width_variants:
                            if not MeasureFSTRecognizer.check_not_mixed_width(text3.label):
                                raise Exception(
                                    f"Unit string has mixed character widths: {text3.label}")
                            hash_set.add(StringUtils.full_width_to_half_width(text3.label))
                            hash_set.add(StringUtils.half_width_to_full_width2(text3.label))
                        for text4 in hash_set:
                            units.add(text4)
                            if custom_units is not None:
                                custom_units.add(text4)

        flag = True
        for text5 in units:
            if flag:
                flag = False
            else:
                sb.append("|")
            sb.append(f"(<{FST.escape_special(text5[0])}:U>")
            text6 = text5[1:]
            if text6:
                sb.append(FST.escape_special(text6))
            sb.append(")")

        sb.append(")")

        if append_word_terminator:
            sb.append("#>")

        fst = FST.create(sb.to_string())
        fst.make_deterministic()
        return fst

    @staticmethod
    def evaluate_and_sort_candidates(candidates, priority):
        if not candidates:
            return

        for prioritized_token in candidates:
            measure_token = prioritized_token.token  # Assuming `PrioritizedToken.token` is a MeasureToken
            num = 0
            if measure_token.decimal_separator == NumericSeparator.Alternate or measure_token.group_separator == NumericSeparator.Alternate:
                num += 1
            prioritized_token.priority = priority - num

        candidates.sort(key=lambda x: x.priority, reverse=True)

    def parse(self, surface, output):
        num = output.find('U')
        if num <= 0:
            raise Exception("Invalid measurement format")

        text = surface[:num]
        text2 = output[:num]
        unit_separator = '\0'

        while num < len(surface) and surface[num].isspace():
            if unit_separator == '\0':
                unit_separator = surface[num]
            num += 1

        unit_part = surface[num:]
        text3 = text
        text4 = text2
        number_fst_ex = self._number_fst_ex
        nt = NumberFSTRecognizer.parse_number(text3, text4,
                                              number_fst_ex.separator_combinations if number_fst_ex else None,
                                              self.culture_name)
        unit_string_for_lookup = unit_part

        text5 = None
        unit = Unit.NoUnit

        measure_fst_ex = self._measure_fst_ex
        custom_unit_definition = None
        if measure_fst_ex and measure_fst_ex.unit_definitions:
            custom_unit_definition = measure_fst_ex.unit_definitions.get(unit_string_for_lookup)

            if custom_unit_definition:
                unit = custom_unit_definition.unit
                text5 = custom_unit_definition.category_name

        return MeasureToken(surface, nt, unit, unit_part, unit_separator, text5)


class CurrencyFSTRecognizer(Recognizer):
    def __init__(self, settings, priority, fst_recog, fst_ex, number_fst_ex, culture_name):
        super().__init__(settings, TokenType.Measurement, priority, 'Currency', 'CurrencyFSTRecognizer', False, culture_name)
        self._fst_recog = fst_recog
        self._currency_fst_ex = fst_ex
        self._number_fst_ex = number_fst_ex
        #mod

    @staticmethod
    def create(settings, culture_name, priority, accessor, fst_ex):
        #mod
        currency_fst_recognizer = CurrencyFSTRecognizer(settings, priority, None, None, None, culture_name)
        currency_fst_recognizer = CurrencyFSTRecognizer.set_additional_options(currency_fst_recognizer)
        return currency_fst_recognizer
    @staticmethod
    def set_additional_options(result:Recognizer):
        result.only_if_followed_by_nonword_character = True
        result.override_fallback_recognizer = True
        return result

    def recognize(self, s: str, from_idx: int, allow_token_bundles: bool, consumed_length: int) -> Tuple[Token, int]:
        return None, consumed_length#mod