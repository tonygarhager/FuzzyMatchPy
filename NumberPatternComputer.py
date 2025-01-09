from typing import Any, Tuple, List, Dict

from CultureInfoExtensions import CultureInfoExtensions
from CurrencyFSTEx import CurrencyFSTEx
from CurrencyFormat import CurrencyFormat
from CustomUnitDefinition import CustomUnitDefinition
from FST import FST
from MeasureFSTEx import MeasureFSTEx
from NumberFSTEx import NumberFSTEx
from NumberFormatData import NumberFormatData
from SeparatorCombination import SeparatorCombination
from StringUtils import StringUtils


class NumberPatternComputer:
    # Constants
    DefaultDigits = "0123456789"
    FullWidthDigits = "０１２３４５６７８９"

    AllowTrailingSign = True
    SUPPORT_NONSTANDARD_GROUPING = False

    NumericPositiveSymbols = ['+', '＋']
    NumericNegativeSymbols = ['-', '–', '−', '－']

    @staticmethod
    def do_add_enus_separators(culture:str) -> bool:
        two_letter_iso_language_name = StringUtils.get_iso_language_code(culture)
        return two_letter_iso_language_name.lower() == "fr"

    @staticmethod
    def get_number_format_data(culture: Any, add_separator_variants: bool,
                               augment_whitespace_group_separators: bool) -> NumberFormatData:
        if culture is None:
            raise ValueError("Argument cannot be null")

        if culture.IsNeutralCulture:
            raise ValueError("Cannot compute number format information for neutral cultures")

        text = "".join(culture.NumberFormat.NativeDigits)
        if len(text) != 10:
            return None

        number_format_data = NumberFormatData()
        number_format_data.digits.append(text)

        if text != NumberPatternComputer.DefaultDigits:
            number_format_data.digits.append(NumberPatternComputer.DefaultDigits)

        if CultureInfoExtensions.use_full_width(
                culture) and NumberPatternComputer.FullWidthDigits not in number_format_data.digits:
            number_format_data.digits.append(NumberPatternComputer.FullWidthDigits)

        number_format_data.negative_signs = culture.NumberFormat.NegativeSign
        number_format_data.positive_signs = culture.NumberFormat.PositiveSign
        number_format_data.number_group_sizes = culture.NumberFormat.NumberGroupSizes
        number_format_data.number_negative_pattern = culture.NumberFormat.NumberNegativePattern
        number_format_data.add_separator_combination(culture.NumberFormat.NumberGroupSeparator,
                                                     culture.NumberFormat.NumberDecimalSeparator,
                                                     augment_whitespace_group_separators)
        number_format_data.add_separator_combination(culture.NumberFormat.CurrencyGroupSeparator,
                                                     culture.NumberFormat.CurrencyDecimalSeparator,
                                                     augment_whitespace_group_separators)

        if not add_separator_variants:
            return number_format_data

        text2 = culture.TwoLetterISOLanguageName.lower()
        if text2 == "fr":
            number_format_data.add_separator_combination(",", ".", False)
        elif text2 == "pl":
            number_format_data.add_separator_combination(".", ",", False)

        if CultureInfoExtensions.use_full_width(culture):
            number_format_data.add_separator_combination(
                StringUtils.half_width_to_full_width(culture.NumberFormat.NumberGroupSeparator),
                StringUtils.half_width_to_full_width(culture.NumberFormat.NumberDecimalSeparator),
                augment_whitespace_group_separators
            )
            number_format_data.add_separator_combination(
                StringUtils.half_width_to_full_width(culture.NumberFormat.CurrencyGroupSeparator),
                StringUtils.half_width_to_full_width(culture.NumberFormat.CurrencyDecimalSeparator),
                augment_whitespace_group_separators
            )

        for i in range(len(number_format_data.separator_combinations) - 1, -1, -1):
            separator_combination = number_format_data.separator_combinations[i]
            if separator_combination.is_swappable():
                number_format_data.add_separator_combination(separator_combination[1], separator_combination[0], False)

        return number_format_data

    @staticmethod
    def get_measure_number_and_currency_language_resources(ci: str,
                                                           custom_separator_combinations: List[SeparatorCombination],
                                                           custom_units: Dict[str, CustomUnitDefinition],
                                                           currency_formats: List[CurrencyFormat],
                                                           custom_separators_only: bool, custom_units_only: bool,
                                                           culture_metadata_manager: Any) -> Tuple[FST, NumberFSTEx, FST, MeasureFSTEx, FST, CurrencyFSTEx]:
        number_format_data = NumberPatternComputer.get_number_format_data(ci, True, False)
        nfd_augmented = NumberPatternComputer.get_number_format_data(ci, True, True)

        if custom_separators_only and (not custom_separator_combinations or len(custom_separator_combinations) == 0):
            raise ValueError("customSeparatorsOnly specified but no separator combinations were provided")

        if custom_separators_only:
            number_format_data.separator_combinations.clear()
            nfd_augmented.separator_combinations.clear()

        if custom_separator_combinations:
            for separator_combination in custom_separator_combinations:
                if separator_combination.group_separators is None or len(
                        separator_combination.group_separators) > 1 or separator_combination.decimal_separators is None or len(
                        separator_combination.decimal_separators) > 1:
                    raise ValueError("SeparatorException")
                number_format_data.add_separator_combination(separator_combination.group_separators,
                                                             separator_combination.decimal_separators, False)
                nfd_augmented.add_separator_combination(separator_combination.group_separators,
                                                        separator_combination.decimal_separators, True)

        number_fst = FSTGenerator.generate_number_fst(ci, nfd_augmented, True)
        number_fst_ex = NumberFSTEx()
        number_fst_ex.separator_combinations = custom_separator_combinations if custom_separators_only else number_format_data.separator_combinations

        string_units = set()
        if custom_units is None:
            custom_units = {}
        for text in custom_units.keys():
            if text in string_units:
                raise ValueError(f"Duplicate unit string found: {text}")
            string_units.add(text)

        fst = FSTGenerator.generate_measurement_fst(ci, nfd_augmented, string_units, custom_units_only, True,
                                                    culture_metadata_manager)
        measure_fst = fst
        fst_ex = MeasureFSTEx()
        fst_ex.unit_definitions = custom_units.copy()

        if not custom_units_only:
            for text in string_units:
                if text not in custom_units:
                    fst_ex.unit_definitions[text] = None

        if not currency_formats:
            currency_formats = CurrencyFSTEx.get_defaults(ci, None, culture_metadata_manager).currency_formats

        currency_fst_ex = CurrencyFSTEx()
        currency_fst_ex.currency_formats = currency_formats
        fst2 = FSTGenerator.generate_currency_fst(ci, nfd_augmented, currency_formats, True)

        return number_fst, number_fst_ex, measure_fst, fst_ex, fst2, currency_fst_ex

    @staticmethod
    def append_disjunction(sb: str, symbol: str, output: str, first: bool) -> Tuple[str, bool]:
        if not first:
            sb += "|"
        sb += f"<{FST.escape_special(symbol)}:{output}>"
        return sb, False

    @staticmethod
    def append_disjunction_(sb: str, symbols: str, output: str, first: bool) -> Tuple[str, bool]:
        if not symbols:
            return sb, first

        for c in symbols:
            sb, first = NumberPatternComputer.append_disjunction(sb, c, output, first)

        return sb, first

    @staticmethod
    def is_balanced(s: str) -> bool:
        if not s:
            return True

        num = 0
        flag = False

        for c in s:
            if flag:
                flag = False
            elif c != '(':
                if c != ')':
                    if c == '\\':
                        flag = True
                else:
                    num -= 1
                    if num < 0:
                        return False
            else:
                num += 1

        return num == 0

    @staticmethod
    def compute_sign(positive_signs: str, negative_signs: str, optional: bool) -> str:
        string_builder = ""
        string_builder += "("
        first = True

        # Append positive signs
        string_builder, first = NumberPatternComputer.append_disjunction(string_builder, positive_signs, '+', first)
        first = False

        # Append negative signs
        string_builder, first = NumberPatternComputer.append_disjunction(string_builder, negative_signs, '-', first)

        string_builder += ")" if not optional else ")?"
        return string_builder

    @staticmethod
    def compute_single_digit(digit_set: list[str]) -> str:
        string_builder = ""
        first = True
        string_builder += "("

        for text in digit_set:
            for i in range(10):
                string_builder, first = NumberPatternComputer.append_disjunction(string_builder, text[i], NumberPatternComputer.DefaultDigits[i],
                                                    first)
                first = False

        string_builder += ")"
        return string_builder

    @staticmethod
    def compute_fst_pattern(data, treat_first_separators_as_primary_separators, append_word_terminator):
        text = NumberPatternComputer.compute_single_digit(data.digits)
        string_builder = ""
        string_builder += "".join(NumberPatternComputer.NumericPositiveSymbols)
        string_builder2 = ""
        string_builder2 += "".join(NumberPatternComputer.NumericNegativeSymbols)
        text2 = string_builder
        text3 = string_builder2
        text4 = NumberPatternComputer.compute_sign(text2, text3, True)
        text5 = NumberPatternComputer.compute_sign(text2, text3, False)

        string_builder3 = ""
        combined_decimal_separators = data.get_combined_decimal_separators()
        string_builder3 += f"({text}+((("

        flag = True
        for i in range(len(combined_decimal_separators)):
            if i == 0 and treat_first_separators_as_primary_separators:
                NumberPatternComputer.append_disjunction(string_builder3, combined_decimal_separators[i], 'D', flag)
            else:
                NumberPatternComputer.append_disjunction(string_builder3, combined_decimal_separators[i], 'd', flag)

        string_builder3 += f"){text}+)?)"

        string_builder4 = ""
        string_builder4 += f"{text}({text}{text}?)?("

        flag = True
        for separator_combination in data.separator_combinations:
            string_builder5 = ""
            string_builder5 += "("

            for j in range(len(separator_combination.group_separators)):
                c = 'g'
                if flag and treat_first_separators_as_primary_separators:
                    c = 'G'
                if j > 0:
                    string_builder5 += "|"
                string_builder5 += f"((<{FST.escape_special(separator_combination.group_separators[j])}:{c}>{text}{text}{text})+)"

            string_builder5 += ")"
            string_builder5 += "(("

            for k in range(len(separator_combination.decimal_separators)):
                c2 = 'd'
                if flag and treat_first_separators_as_primary_separators:
                    c2 = 'D'
                if k > 0:
                    string_builder5 += "|"
                string_builder5 += f"<{FST.escape_special(separator_combination.decimal_separators[k])}:{c2}>"

            string_builder5 += f"){text}+)?"

            if not flag:
                string_builder4 += "|"

            string_builder4 += f"({string_builder5})"

            if flag:
                flag = False

        string_builder4 += ")"

        string_builder6 = ""
        if not NumberPatternComputer.AllowTrailingSign or data.number_negative_pattern < 3:
            string_builder6 += f"({text4}({string_builder4}|{string_builder3}))"
        else:
            string_builder6 += f"(({text5}({string_builder4}|{string_builder3}))|(({string_builder4}|{string_builder3}){text4}))"

        if append_word_terminator:
            string_builder6 += "#>"

        return string_builder6




