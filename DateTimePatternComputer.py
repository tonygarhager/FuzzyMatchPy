
class DateTimePatternComputer:
    def __init__(self, culture_name:str, accessor):
        self._culture = culture_name
        self._accessor = accessor