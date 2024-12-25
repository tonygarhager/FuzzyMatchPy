
import re
from Recognizer import *
from typing import List
from Token import *
from SimpleToken import *
from email.utils import parseaddr

class RegexRecognizerPattern:
    def __init__(self, rx=None, first=None, priority=0):
        """
        Initializes a new instance of RegexRecognizerPattern.

        :param rx: The regular expression (compiled regex object).
        :param first: A CharacterSet object representing the first set.
        :param priority: The priority of the pattern.
        """
        self.regex = rx
        self.first = first
        self.priority = priority

    @property
    def pattern(self):
        """
        Gets the string representation of the regex pattern.
        :return: The regex pattern as a string, or None if regex is None.
        """
        if self.regex is None:
            return None
        return self.regex.pattern

class RegexRecognizer(Recognizer, IRecognizerTextFilter):
    TOKEN_MAX_SIZE = 2000

    def __init__(self, settings, t, priority, token_class_name, recognizer_name, auto_substitutable, culture):
        super().__init__(settings, t, priority, token_class_name, recognizer_name, auto_substitutable, culture)
        self.patterns: List[RegexRecognizerPattern] = []

    def add(self, rx_pattern: str, first=None, priority: int = 0, case_insensitive: bool = False):
        if not rx_pattern:
            raise ValueError("rx_pattern cannot be null or empty")
        options = re.ASCII if not case_insensitive else re.IGNORECASE
        rx = re.compile(rx_pattern, options)
        if any(p.pattern == rx.pattern for p in self.patterns):
            return
        self.patterns.append(RegexRecognizerPattern(rx, first, priority))

    def create_token(self, s: str):

        if self.type == TokenType.OtherTextPlaceable:
            token = GenericPlaceableToken(s, self.token_class_name, self.auto_substitutable)
        else:
            token = SimpleToken(s, self.type)
        token.culture_name = self.culture_name
        return token

    def recognize(self, s: str, from_idx: int, allow_token_bundles: bool, consumed_length: int):
        token = None
        max_length = 0
        max_priority = 0
        for pattern in self.patterns:
            regex = pattern.regex
            first = pattern.first
            if first is None or from_idx >= len(s) or first.contains(s[from_idx]):
                match = regex.match(s, from_idx)
                if match and self.verify_context_constraints(s, match.end(), None):
                    new_token = self.create_token(match.group(), match.groups())
                    if new_token and len(match.group()) > 0:
                        if len(match.group()) > max_length or token is None or \
                                (
                                        len(match.group()) == max_length and pattern.priority > max_priority and not allow_token_bundles):
                            max_length = len(match.group())
                            token = new_token
                            max_priority = pattern.priority
                        elif allow_token_bundles and len(match.group()) == max_length:
                            if not isinstance(token, list):
                                token = [token]
                            token.append(new_token)
                            max_priority = max(max_priority, pattern.priority)
        if token is None:
            return None, consumed_length
        consumed_length = max_length
        return token, consumed_length

    def exclude_text(self, s:str) ->bool:
        return s is not None and len(s) > 2000

class EmailRecognizer(RegexRecognizer):
    def __init__(self, settings, priority, culture):
        super().__init__(settings, TokenType.OtherTextPlaceable, priority, "EMAIL", "DEFAULT_URI_REGOCNIZER", True, culture)
        email_pattern = r"(mailto:)?(?!\\.)[^\\s@\\\\\\(\\);:<>\\[\\],\\\"]+@((?![\\\"<>\\[\\]])[\\p{L}\\p{N}\\p{Pc}\\p{Pd}\\p{S}])+\\.(((?![\\\"<>\\[\\]])[\\p{L}\\p{N}\\p{Pc}\\p{Pd}\\p{S}])+\\.)*((?![\\\"<>\\[\\]])[\\p{L}\\p{N}\\p{Pc}\\p{Pd}\\p{S}]){2,}"
        self.add(email_pattern, None, True)

    def exclude_text(self, s:str)->bool:
        if super().exclude_text(s):
            return True
        return s.find('@') == -1

    def recognize(self, s, from_index, allow_token_bundles, consumed_length):
        token = super().recognize(s, from_index, allow_token_bundles, consumed_length)
        if token:
            try:
                text = token.text.lower()
                if text.startswith("mailto:"):
                    text = text[7:]
                mail_address = parseaddr(text)[1]
                if mail_address:
                    token.text = mail_address
                    return token
            except ValueError:
                pass
        return None
