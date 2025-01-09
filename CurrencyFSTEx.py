import enum
from typing import List, Set, Optional
import asyncio

from AutoLocalizationSettings import CurrencySymbolPosition
from CurrencyFormat import CurrencyFormat
from Wordlist import Wordlist


class CurrencyFSTEx:
    CURRENT_VERSION = 1

    def __init__(self):
        self.version = 1
        self.currency_formats: List[CurrencyFormat] = []

    @staticmethod
    def get_defaults(culture, accessor, culture_metadata_manager):
        if accessor is None:
            accessor = ResourceFileResourceAccessor(culture_metadata_manager)

        wl = Wordlist()
        stream = accessor.read_resource_data(culture, "CurrencySymbols", True)
        with stream:
            if stream:
                wl.load(stream, True)

        currency_fst_ex = None
        if not wl.count:
            currency_fst_ex = CurrencyFSTEx()
        else:
            fst_ex = CurrencyFSTEx()
            culture_info = culture_metadata_manager.get_language(culture).get_culture_info()

            for text in wl.items:
                currency_format = CurrencyFormat()
                currency_format.symbol = text
                currency_format.currency_symbol_positions = [CurrencySymbolPosition.beforeAmount, CurrencySymbolPosition.afterAmount]

                if not culture_info.currency_precedes_number():
                    currency_format.currency_symbol_positions.reverse()

                fst_ex.currency_formats.append(currency_format)

            currency_fst_ex = fst_ex

        return currency_fst_ex

    @staticmethod
    def from_binary(data: bytes) -> 'CurrencyFSTEx':
        data_str = data.decode('utf-8')
        lines = [line for line in data_str.split('\r') if line.strip()]

        if len(lines) == 0:
            return CurrencyFSTEx()

        try:
            version = int(lines[0])
        except ValueError:
            raise Exception("Unexpected data during CurrencyFSTEx deserialization")

        if version > 1:
            raise Exception(f"Unexpected CurrencyFSTEx version: {version}")

        lines = lines[1:]
        currency_formats = []
        invalid_text = None

        for line in lines:
            currency_format = CurrencyFormat()
            builder = []
            i = 0
            while i < len(line) and not line[i].isspace():
                builder.append(line[i])
                i += 1

            if not builder:
                invalid_text = line
                break

            i += 1
            currency_format.symbol = ''.join(builder)
            currency_format.separators = set()

            while i < len(line) and (line[i] == 'Z' or line[i].isspace()):
                char = line[i] if line[i] != 'Z' else '\0'
                currency_format.separators.add(char)
                i += 1

            if i >= len(line):
                invalid_text = line
                break

            rest = line[i:]
            separator_index = rest.find('|')
            if separator_index == -1:
                invalid_text = line
                break

            category = rest[separator_index + 1:]
            rest = rest[:separator_index]
            positions = [int(pos) for pos in rest.split(',') if pos.isdigit()]

            for position in positions:
                if not CurrencySymbolPosition(position):
                    invalid_text = line
                    break
                currency_format.currency_symbol_positions.append(CurrencySymbolPosition(position))

            if invalid_text is not None:
                break

            currency_format.category = category
            currency_formats.append(currency_format)

        if invalid_text:
            raise Exception(f"Invalid currency format line: {invalid_text}")

        return CurrencyFSTEx(currency_formats=currency_formats, version=version)

    def to_binary(self) -> bytes:
        builder = []

        if self.currency_formats:
            builder.append(str(self.CURRENT_VERSION))

            for currency_format in self.currency_formats:
                builder.append(f'\r{currency_format.symbol} ')

                for separator in currency_format.separators:
                    builder.append(separator if separator != '\0' else 'Z')

                if currency_format.currency_symbol_positions:
                    positions = ','.join([str(int(pos)) for pos in currency_format.currency_symbol_positions])
                    builder.append(positions)

                builder.append(f'|{currency_format.category}')

        return ''.join(builder).encode('utf-8')