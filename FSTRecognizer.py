from Label import Label
from Match import FSTMatch
from Matcher import Matcher

class FSTRecognizer:
    def __init__(self, fst, culture):
        if fst is None:
            raise ValueError("fst cannot be None")
        self.fst = fst
        self.culture = culture
        self.first = self.fst.get_first_set(False)

    @property
    def fst(self):
        return self._fst

    @fst.setter
    def fst(self, value):
        self._fst = value

    @property
    def first(self):
        return self._first

    @first.setter
    def first(self, value):
        self._first = value

    @property
    def culture(self):
        return self._culture

    @culture.setter
    def culture(self, value):
        self._culture = value

    def compute_matches(self, s, start_offset, ignore_case, cap, keep_longest_matches_only):
        if not self.fst:
            return None

        c = s[start_offset]
        if start_offset < len(s) and self.first and not Label.matches(c, self.first, ignore_case):
            return None

        matcher = Matcher(self.fst)
        matches = []

        def match_callback(ms):
            matches.append(ms)
            return True

        matcher.match(s, False, Matcher.MatchMode.ANALYSE, start_offset, ignore_case, match_callback, None)

        if not matches:
            return None

        matches.sort(key=lambda a: a.consumed_symbols, reverse=True)
        consumed_symbols = matches[0].consumed_symbols
        result = []

        for match_state in matches:
            if keep_longest_matches_only and match_state.consumed_symbols < consumed_symbols:
                break
            result.append(FSTMatch(start_offset, match_state.consumed_symbols, match_state.get_output_as_string()))
            if cap > 0 and len(result) >= cap:
                break

        return result
