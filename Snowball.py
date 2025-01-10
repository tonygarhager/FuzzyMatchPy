import logging
from typing import List, Callable, Optional, Dict


class Env:
    def __init__(self, other=None):
        """
        Initializes an Env instance. If another Env instance is provided, copies its attributes.

        :param other: Another Env instance to copy attributes from (optional).
        """
        self.current = None
        self.cursor = 0
        self.limit = 0
        self.limit_backward = 0
        self.bra = 0
        self.ket = 0

        if other is not None:
            self.copy_from(other)

    def copy_from(self, other):
        """
        Copies attributes from another Env instance.

        :param other: Another Env instance.
        """
        self.current = other.current
        self.cursor = other.cursor
        self.limit = other.limit
        self.limit_backward = other.limit_backward
        self.bra = other.bra
        self.ket = other.ket

class Stemmer(Env):
    def __init__(self):
        super().__init__()
        self.current = ""
        self.set_buffer_contents("")

    def stem(self) -> bool:
        raise NotImplementedError("The stem method must be implemented in a subclass.")

    def stem_word(self) -> bool:
        return self.stem()

    def stem_string(self, word: str) -> str:
        self.set_buffer_contents(word)
        self.stem()
        return self.current

    @property
    def buffer(self) -> str:
        return self.current

    @buffer.setter
    def buffer(self, value: str):
        self.set_buffer_contents(value)

    def set_buffer_contents(self, value: str):
        self.current = value
        self.cursor = 0
        self.limit = len(self.current)
        self.limit_backward = 0
        self.bra = self.cursor
        self.ket = self.limit

    def in_grouping(self, s: str, min_char: int, max_char: int, repeat: bool) -> int:
        while self.cursor < self.limit:
            c = self.current[self.cursor]
            if ord(c) < min_char or ord(c) > max_char or c not in s:
                return 1
            self.cursor += 1
            if not repeat:
                return 0
        return -1

    def in_grouping_b(self, s: str, min_char: int, max_char: int, repeat: bool) -> int:
        while self.cursor > self.limit_backward:
            c = self.current[self.cursor - 1]
            if ord(c) < min_char or ord(c) > max_char or c not in s:
                return 1
            self.cursor -= 1
            if not repeat:
                return 0
        return -1

    def out_grouping(self, s: str, min_char: int, max_char: int, repeat: bool) -> int:
        while self.cursor < self.limit:
            c = self.current[self.cursor]
            if ord(c) < min_char or ord(c) > max_char or c in s:
                self.cursor += 1
                continue
            self.cursor += 1
            if not repeat:
                return 0
        return -1

    def out_grouping_b(self, s: str, min_char: int, max_char: int, repeat: bool) -> int:
        while self.cursor > self.limit_backward:
            c = self.current[self.cursor - 1]
            if ord(c) < min_char or ord(c) > max_char or c in s:
                self.cursor -= 1
                continue
            self.cursor -= 1
            if not repeat:
                return 0
        return -1

    def eq_s(self, s: str) -> bool:
        if self.limit - self.cursor < len(s):
            return False
        if self.current[self.cursor:self.cursor + len(s)] != s:
            return False
        self.cursor += len(s)
        return True

    def eq_s_b(self, s: str) -> bool:
        if self.cursor - self.limit_backward < len(s):
            return False
        if self.current[self.cursor - len(s):self.cursor] != s:
            return False
        self.cursor -= len(s)
        return True

    def find_among(self, v: List["Among"]) -> int:
        num = 0
        num2 = len(v)
        cursor = self.cursor
        limit = self.limit
        while True:
            num5 = num + (num2 - num) // 2
            among = v[num5]
            num6 = (self.current[cursor:cursor + len(among.search_string)] != among.search_string)

            if num6 < 0:
                num2 = num5
            else:
                num = num5
            if num2 - num <= 1:
                if num > 0 or num2 == num:
                    break

        among2 = v[num]
        if self.current[cursor:cursor + len(among2.search_string)] == among2.search_string:
            self.cursor = cursor + len(among2.search_string)
            return among2.result
        return 0

    def find_among_b(self, v):
        num = 0
        num2 = len(v)
        cursor = self.cursor
        limit_backward = self.limit_backward
        num3 = 0
        num4 = 0
        flag = False

        while True:
            num5 = num + ((num2 - num) >> 1)
            num6 = 0
            num7 = min(num3, num4)
            among = v[num5]

            for i in range(len(among.search_string) - 1 - num7, -1, -1):
                if cursor - num7 == limit_backward:
                    num6 = -1
                    break
                num6 = ord(self.current[cursor - 1 - num7]) - ord(among.search_string[i])
                if num6 != 0:
                    break
                num7 += 1

            if num6 < 0:
                num2 = num5
                num4 = num7
            else:
                num = num5
                num3 = num7

            if num2 - num <= 1:
                if num > 0 or num2 == num or flag:
                    break
                flag = True

        while True:
            among2 = v[num]
            if num3 >= len(among2.search_string):
                self.cursor = cursor - len(among2.search_string)
                if among2.action is None:
                    break
                flag2 = among2.action()
                self.cursor = cursor - len(among2.search_string)
                if flag2:
                    return among2.result
            num = among2.match_index
            if num < 0:
                return 0

        return among2.result

    def replace_s(self, c_bra: int, c_ket: int, s: str) -> int:
        num = len(s) - (c_ket - c_bra)
        self.current = self.current[:c_bra] + s + self.current[c_ket:]
        self.limit += num
        if self.cursor >= c_ket:
            self.cursor += num
        elif self.cursor > c_bra:
            self.cursor = c_bra
        return num

    def slice_check(self):
        if not (0 <= self.bra <= self.ket <= self.limit <= len(self.current)):
            logging.error("Faulty slice operation")

    def slice_from(self, s: str):
        self.slice_check()
        self.replace_s(self.bra, self.ket, s)

    def slice_del(self):
        self.slice_from("")

    def insert(self, c_bra: int, c_ket: int, s: str):
        num = self.replace_s(c_bra, c_ket, s)
        if c_bra <= self.bra:
            self.bra += num
        if c_bra <= self.ket:
            self.ket += num

    def slice_to(self, s: str) -> str:
        self.slice_check()
        return self.current[self.bra:self.ket]

    def assign_to(self, s: str) -> str:
        return self.current[:self.limit]

    @staticmethod
    def replace(sb: str, index: int, length: int, text: str) -> str:
        return sb[:index] + text + sb[length:]

class SnowballWrapper:
    _exceptions = {
        "fr": {
            "la": "le",
            "l'": "le",
            "du": "de",
            "des": "de",
            "d'": "de",
            "qu'": "que",
            "s'": "se",
            "n'": "ne",
            "aux": "à",
            "au": "à",
        }
    }

    def __init__(self, stemmer: Stemmer, exceptions: Optional[Dict[str, str]], ci: str, strip_diacritics: bool, signature: int):
        self._stemmer = stemmer
        self._exceptions = exceptions
        self._ci = ci
        self._strip_diacritics = strip_diacritics
        self._signature = signature

    def stem(self, word: str) -> str:
        """Synchronously stems the given word."""
        return self.stem_async(word)

    def stem_async(self, word: str) -> str:
        """Asynchronously stems the given word."""
        word = word.lower()
        if self._exceptions:
            word = word.replace("`", "'").replace("‘", "'").replace("’", "'")
            if word in self._exceptions:
                return self._exceptions[word]

        text = self._stemmer.stem_string(word)

        if not self._strip_diacritics:
            return text

        text = self._to_base(text)
        text = self.strip_peripheral_punctuation(text)
        return text

    @staticmethod
    def create(ci: str, t) -> Optional["SnowballWrapper"]:
        """Creates a SnowballWrapper instance for the given culture."""
        two_letter_iso_language_name = ci.lower()[:2]
        stemmer = t
        if not stemmer:
            return None

        exceptions = SnowballWrapper._exceptions.get(two_letter_iso_language_name, None)
        signature = hash(two_letter_iso_language_name)
        return SnowballWrapper(stemmer, exceptions, ci, t.strips_diacritics, signature)

    @property
    def signature(self) -> str:
        """Returns the signature of the stemmer."""
        return str(self._signature)

    @staticmethod
    def strip_peripheral_punctuation(form: str) -> str:
        """Strips punctuation from the beginning and end of the string."""
        if not form:
            return form

        start = 0
        length = len(form)
        while start < length and form[start].is_punctuation():
            start += 1

        end = length - 1
        while end > start and form[end].is_punctuation():
            end -= 1

        return form[start:end + 1]

    @staticmethod
    def _to_base(text: str, strip_diacritics: bool = True) -> str:
        """Normalizes the text to remove diacritics."""
        if strip_diacritics:
            return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        return text