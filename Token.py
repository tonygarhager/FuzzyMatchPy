from SegmentRange import SegmentRange
from SegmentElement import SegmentElement

class TokenType:
    Unknown = -1
    Word = 0
    Abbreviation = 1
    CharSequence = 2
    GeneralPunctuation = 3,
    OpeningPunctuation = 4,
    ClosingPunctuation = 5
    Date = 6
    Time = 7
    Variable = 8
    Number = 9
    Measurement = 10
    Whitespace = 11
    Acronym = 12
    Uri = 13
    OtherTextPlaceable = 14
    UserDefined = 15
    Tag = 16
    AlphaNumeric = 17

class Token(SegmentElement):
    def __init__(self, culture_name, text = None):
        self.culture_name = culture_name
        self.text = text
        self.span = SegmentRange(None, None)
        self.type = TokenType.Unknown

    def get_token_type(self):
        return self.type

    def is_punctuation(self):
        type == TokenType.GeneralPunctuation or type == TokenType.OpeningPunctuation or type == TokenType.ClosingPunctuation

    def is_word(self):
        type == TokenType.Word or type == TokenType.Abbreviation or type == TokenType.Acronym or type == TokenType.Uri or type == TokenType.OtherTextPlaceable

    def is_whitespace(self):
        type == TokenType.Whitespace

    def is_placeable(self):
        return False

    def is_substitutable(self):
        return False



