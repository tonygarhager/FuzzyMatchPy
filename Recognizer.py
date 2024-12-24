
class RecognizerSettings:
    def __init__(self):
        self.break_on_hyphens: bool = False
        self.break_on_dash: bool = False
        self.break_on_apostrophe: bool = False

class Recognizer:
    def __init__(self, settings, t, priority, token_class_name, recognizer_name, auto_substitutable, culture_name):
        self.override_fallback_recognizer = False
        self.is_fallback_recognizer = False
        self.settings = settings
        self.type = t
        self.priority = priority
        self.token_class_name = token_class_name
        self.recognizer_name = recognizer_name
        self.auto_substitutable = auto_substitutable
        self.culture_name = culture_name