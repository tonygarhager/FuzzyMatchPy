from typing import List, Set

from CultureInfoExtensions import CultureInfoExtensions
from CurrencyFSTEx import CurrencyFSTEx
from CurrencyFormat import CurrencyFormat
from FST import FST
from MeasureFSTRecognizer import MeasureFSTRecognizer, CurrencyFSTRecognizer
from NumberFSTRecognizer import NumberFSTRecognizer
from NumberFormatData import NumberFormatData


class FSTGenerator:

    @staticmethod
    def generate_number_fst(ci: str, culture_metadata_manager) -> FST:
        return NumberFSTRecognizer.create_fst(ci, NumberFSTRecognizer.append_word_terminator(ci), culture_metadata_manager)

    @staticmethod
    def generate_number_fst_sync(ci: str, nfd: NumberFormatData, treat_first_separators_as_primary_separators: bool) -> FST:
        return NumberFSTRecognizer.create_fst(ci, NumberFSTRecognizer.append_word_terminator(ci), nfd, treat_first_separators_as_primary_separators)

    @staticmethod
    def generate_measurement_fst(ci: str, culture_metadata_manager) -> FST:
        return MeasureFSTRecognizer.create_fst(ci, CultureInfoExtensions.use_blank_as_word_separator(ci), culture_metadata_manager)

    @staticmethod
    def generate_measurement_fst_sync(ci: str, nfd: NumberFormatData, custom_units: Set[str], custom_units_only: bool, treat_first_separators_as_primary_separators: bool, culture_metadata_manager) -> FST:
        return MeasureFSTRecognizer.create_fst(ci, MeasureFSTRecognizer.append_word_terminator(ci), nfd, custom_units, custom_units_only, treat_first_separators_as_primary_separators, culture_metadata_manager)

    @staticmethod
    def generate_currency_fst(ci: str, nfd: NumberFormatData, currency_formats: List[CurrencyFormat], treat_first_separators_as_primary_separators: bool) -> FST:
        currency_fst_ex = CurrencyFSTEx(currency_formats)
        return CurrencyFSTRecognizer.create_fst(ci, CurrencyFSTRecognizer.append_word_terminator(ci), nfd, currency_fst_ex, treat_first_separators_as_primary_separators)
