from Field import FieldDefinitions


class TUStreamContext:
    def __init__(self, source_culture:str, target_culture:str, fields:FieldDefinitions):
        if source_culture is None or target_culture is None:
            raise ValueError("source_culture and target_culture are required")
        self._source_culture = source_culture
        self._target_culture = target_culture
        if fields is None:
            self._fields = FieldDefinitions()
        else:
            self._fields = fields

        self._may_add_new_fields = True
        self._check_matching_sublanguages = False

    @property
    def field_definitions(self) -> FieldDefinitions:
        return self._fields

    @property
    def source_culture(self) -> str:
        return self._source_culture

    @property
    def target_culture(self) -> str:
        return self._target_culture

    @property
    def check_matching_sublanguages(self):
        return self._check_matching_sublanguages
    @check_matching_sublanguages.setter
    def check_matching_sublanguages(self, value):
        self._check_matching_sublanguages = value

    @property
    def may_add_new_fields(self):
        return self._may_add_new_fields
    @may_add_new_fields.setter
    def may_add_new_fields(self, value):
        self._may_add_new_fields = value