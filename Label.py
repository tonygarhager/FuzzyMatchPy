
class Label:
    SPECIAL_SYMBOL_EPSILON = -1
    SPECIAL_SYMBOL_BEGINNING_OF_WORD = -3
    SPECIAL_SYMBOL_END_OF_WORD = -4
    SPECIAL_SYMBOL_BEGINNING_OF_LINE = -5
    SPECIAL_SYMBOL_END_OF_LINE = -6
    SPECIAL_SYMBOL_WHITESPACE = -7
    SPECIAL_SYMBOL_DIGIT = -8
    FIRST_USER_DEFINED_SYMBOL = -1000

    def __init__(self, symbol):
        self.symbol = symbol

    @property
    def is_char_label(self):
        return self.symbol >= 0

    @property
    def is_consuming(self):
        return self.symbol >= 0 or self.symbol in {
            Label.SPECIAL_SYMBOL_WHITESPACE,
            Label.SPECIAL_SYMBOL_DIGIT,
        } or self.symbol <= Label.FIRST_USER_DEFINED_SYMBOL

    @property
    def is_epsilon(self):
        return self.symbol == Label.SPECIAL_SYMBOL_EPSILON

    def matches(self, s, position, ignore_case):
        if self.symbol >= 0 or self.symbol <= Label.FIRST_USER_DEFINED_SYMBOL:
            if position >= len(s):
                return False
            c = s[position]
            match = ord(c) == self.symbol
            if not match and ignore_case:
                match = c.lower() == chr(self.symbol).lower()
            return match
        elif self.symbol == Label.SPECIAL_SYMBOL_EPSILON:
            return True
        elif position == 0 and self.symbol in {
            Label.SPECIAL_SYMBOL_BEGINNING_OF_LINE,
            Label.SPECIAL_SYMBOL_BEGINNING_OF_WORD,
        }:
            return True
        elif position >= len(s):
            return self.symbol in {
                Label.SPECIAL_SYMBOL_END_OF_LINE,
                Label.SPECIAL_SYMBOL_END_OF_WORD,
            }
        c = s[position]
        if self.symbol == Label.SPECIAL_SYMBOL_DIGIT:
            return c.isdigit()
        elif self.symbol == Label.SPECIAL_SYMBOL_WHITESPACE:
            return c.isspace()
        elif self.symbol == Label.SPECIAL_SYMBOL_BEGINNING_OF_WORD:
            return (
                c.isalnum()
                and (position == 0 or not s[position - 1].isalnum())
            )
        return not c.isalnum()

    @staticmethod
    def matches_char(c, symbols, ignore_case):
        if not symbols:
            return False

        sorted_symbols = sorted(symbols)
        match = ord(c) in sorted_symbols
        if not match and ignore_case:
            if c.isupper():
                match = ord(c.lower()) in sorted_symbols
            elif c.islower():
                match = ord(c.upper()) in sorted_symbols
        if not match and Label.SPECIAL_SYMBOL_WHITESPACE in sorted_symbols:
            match = c.isspace()
        if not match and Label.SPECIAL_SYMBOL_DIGIT in sorted_symbols:
            match = c.isdigit()
        return match

    def __eq__(self, other):
        if not isinstance(other, Label):
            return False
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        if self.symbol >= 0:
            return chr(self.symbol)
        return {
            Label.SPECIAL_SYMBOL_DIGIT: "\\d",
            Label.SPECIAL_SYMBOL_WHITESPACE: "\\s",
            Label.SPECIAL_SYMBOL_END_OF_LINE: "$",
            Label.SPECIAL_SYMBOL_BEGINNING_OF_LINE: "^",
            Label.SPECIAL_SYMBOL_END_OF_WORD: "#>",
            Label.SPECIAL_SYMBOL_BEGINNING_OF_WORD: "#<",
            Label.SPECIAL_SYMBOL_EPSILON: "",
        }.get(self.symbol, f"[Invalid symbol code ={self.symbol}]")
