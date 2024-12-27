from SegmentRange import SegmentRange
from SegmentElement import SegmentElement
from abc import ABC, abstractmethod

class TokenType:
    Unknown = -1
    Word = 0
    Abbreviation = 1
    CharSequence = 2
    GeneralPunctuation = 3
    OpeningPunctuation = 4
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

class Token(SegmentElement, ABC):
    def __init__(self, text:str = None, culture_name:str = None):
        self.culture_name = culture_name
        self._text = text
        self._span = SegmentRange(None, None)
        self.type = TokenType.Unknown

    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, text:str):
        self._text = text
    @property
    def span(self):
        return self._span
    @span.setter
    def span(self, span:SegmentRange):
        self._span = span

    @property
    def type(self):
        return self.get_token_type()
    @type.setter
    def type(self, type:TokenType):
        self.set_token_type(type)

    @abstractmethod
    def get_token_type(self)->TokenType:
        pass

    @abstractmethod
    def set_token_type(self, type:TokenType):
        pass

    def is_punctuation(self):
        type == TokenType.GeneralPunctuation or type == TokenType.OpeningPunctuation or type == TokenType.ClosingPunctuation

    @property
    def is_word(self):
        return (type == TokenType.Word or
                type == TokenType.Abbreviation or
                type == TokenType.Acronym or
                type == TokenType.Uri or
                type == TokenType.OtherTextPlaceable)

    @property
    def is_whitespace(self):
        type == TokenType.Whitespace

    @property
    def is_placeable(self):
        return False

    @property
    def is_substitutable(self):
        return False

    def get_bundle_similarity(self, other):
        from TokenBundle import TokenBundle
        if isinstance(other, TokenBundle) == False:
            return SegmentElement.Similarity.Non
        return other.get_similarity(self)



