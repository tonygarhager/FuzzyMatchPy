from Token import *
from enum import Enum

class Sign:
    Non = 0
    Plus = 1
    Minus = 2

class NumericSeparator(Enum):
    Non = 0
    Primary = 1
    Alternate = 2

class Unit(Enum):
    Mmm = 1
    Mcm = 2
    Mdm = 3
    Mm = 4
    Mkm = 5
    Mmm2 = 6
    Mcm2 = 7
    Mm2 = 8
    Ma = 9
    Mha = 10
    Mkm2 = 11
    Mmg = 12
    Mg = 13
    Mkg = 14
    Mt = 15
    Mml = 16
    Mcm3 = 17
    Mcl = 18
    Mdl = 19
    Ml = 20
    Mm3 = 21
    Mcentigrade = 22
    Mfahrenheit = 23
    Mkelvin = 24
    Mpercent = 25
    Mdegree = 26
    BISin = 27
    BISft = 28
    BISyd = 29
    BISfurlong = 30
    BISmi = 31
    BISin2 = 32
    BISft2 = 33
    BISyd2 = 34
    BISacre = 35
    BISmi2 = 36
    BISoz = 37
    BISlb = 38
    BISstone = 39
    BISshortHW = 40
    BISlongHW = 41
    BISshortTon = 42
    BISlongTon = 43
    BISflozUK = 44
    BISptUK = 45
    BISqtUK = 46
    BISgalUK = 47
    BISbuUK = 48
    BISflozUS = 49
    BISptUS = 50
    BISgalUS = 51
    BISptUSDry = 52
    BISbuUSDry = 53
    Other = 54
    Currency = 55
    NoUnit = 56

class NumberToken(Token):
    standard_digits = [str(i) for i in range(10)]
    def __init__(self, text:str, group_separator:NumericSeparator,
                 decimal_separator:NumericSeparator,
                 alternate_group_separator:str,
                 alternate_decimal_separator:str,
                 sign:Sign,
                 raw_sign:str,
                 raw_decimal_digits:str,
                 raw_fractional_digits:str):
        super().__init__(text)
        self._group_separator = group_separator
        self._alternate_group_separator = alternate_group_separator if group_separator == NumericSeparator.Alternate else '\0'
        self._decimal_separator = decimal_separator
        self._alternate_decimal_separator = alternate_decimal_separator if decimal_separator == NumericSeparator.Alternate else '\0'
        self._sign = sign
        self._raw_sign = raw_sign
        self._raw_decimal_digits = raw_decimal_digits
        self._raw_fractional_digits = raw_fractional_digits
        self.update_canonical_form_and_value()

    def update_canonical_form_and_value(self):
        sb = ''
        if self._sign == Sign.Minus:
            sb += '-'
        sb += self._raw_decimal_digits
        if self._raw_fractional_digits != None:
            sb += '.'
            sb += self._raw_fractional_digits
        self._canonical_number = sb
        try:
            self.value:float = float(self._canonical_number)
        except ValueError:
            self.value:float = 0.0
            self._value_valid = False

    def get_token_type(self) -> TokenType:
        return TokenType.Number

    @property
    def group_separator(self) -> NumericSeparator:
        return self._group_separator
    @group_separator.setter
    def group_separator(self, group_separator:NumericSeparator):
        self._group_separator = group_separator
    @property
    def value_valid(self) -> bool:
        return self._value_valid
    @value_valid.setter
    def value_valid(self):
        self._value_valid = False
    @property
    def sign(self) -> Sign:
        return self._sign
    @sign.setter
    def sign(self, sign:Sign):
        self._sign = sign
    @property
    def raw_sign(self) -> str:
        return self._raw_sign
    @raw_sign.setter
    def raw_sign(self, raw_sign:str):
        self._raw_sign = raw_sign
    @property
    def decimal_separator(self) -> NumericSeparator:
        return self._decimal_separator
    @decimal_separator.setter
    def decimal_separator(self, decimal_separator:NumericSeparator):
        self._decimal_separator = decimal_separator
    @property
    def alternate_group_separator(self) -> str:
        return self._alternate_group_separator
    @alternate_group_separator.setter
    def alternate_group_separator(self, alternate_group_separator:str):
        self._alternate_group_separator = alternate_group_separator
    @property
    def alternate_decimal_separator(self) -> str:
        return self._alternate_decimal_separator
    @alternate_decimal_separator.setter
    def alternate_decimal_separator(self, alternate_decimal_separator:str):
        self._alternate_decimal_separator = alternate_decimal_separator
    @property
    def raw_fractional_digits(self) -> str:
        return self._raw_fractional_digits
    @raw_fractional_digits.setter
    def raw_fractional_digits(self, raw_fractional_digits:str):
        self._raw_fractional_digits = raw_fractional_digits
    @property
    def raw_decimal_digits(self) -> str:
        return self._raw_decimal_digits
    @raw_decimal_digits.setter
    def raw_decimal_digits(self, raw_decimal_digits:str):
        self._raw_decimal_digits = raw_decimal_digits

class MeasureToken(NumberToken):
    def __init__(self, text:str, numeric_part:NumberToken, unit:Unit, unit_string:str, unit_separator:str, custom_category:str = None):
        super().__init__(text, numeric_part.group_separator, numeric_part.decimal_separator, numeric_part.alternate_group_separator,
                         numeric_part.alternate_decimal_separator, numeric_part.sign, numeric_part.raw_sign,
                         numeric_part.raw_decimal_digits, numeric_part.raw_fractional_digits)
        self.unit = unit
        self.unit_string = unit_string
        self.unit_separator = unit_separator
        self.custom_category = custom_category

    def get_token_type(self) -> TokenType:
        return TokenType.Measurement