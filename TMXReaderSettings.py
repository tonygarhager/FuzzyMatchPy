from TUStreamContext import TUStreamContext
from ImportSettings import *

class TMXReaderSettings:
    def __init__(self, context=None, validate_against_schema=True, resolve_neutral_cultures=True, plain_text=False):
        self._context = context if context is not None else TUStreamContext()
        self._validate_against_schema = validate_against_schema
        self._resolve_neutral_cultures = resolve_neutral_cultures
        self._plain_text = plain_text
        self._skip_unknown_cultures = False
        self._cleanup_mode = ImportSettings.ImportTUProcessingMode.PROCESS_CLEANED_TU_ONLY
        self._field_identifier_mappings = None

    @property
    def validate_against_schema(self):
        return self._validate_against_schema

    @validate_against_schema.setter
    def validate_against_schema(self, value):
        self._validate_against_schema = value

    @property
    def context(self):
        return self._context

    @property
    def resolve_neutral_cultures(self):
        return self._resolve_neutral_cultures

    @resolve_neutral_cultures.setter
    def resolve_neutral_cultures(self, value):
        self._resolve_neutral_cultures = value

    @property
    def skip_unknown_cultures(self):
        return self._skip_unknown_cultures

    @skip_unknown_cultures.setter
    def skip_unknown_cultures(self, value):
        self._skip_unknown_cultures = value

    @property
    def plain_text(self):
        return self._plain_text

    @plain_text.setter
    def plain_text(self, value):
        self._plain_text = value

    @property
    def cleanup_mode(self):
        return self._cleanup_mode

    @cleanup_mode.setter
    def cleanup_mode(self, value):
        self._cleanup_mode = value

    @property
    def field_identifier_mappings(self):
        return self._field_identifier_mappings

    @field_identifier_mappings.setter
    def field_identifier_mappings(self, value):
        self._field_identifier_mappings = value
