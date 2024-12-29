from SegmentRange import SegmentRange
from SegmentElement import SegmentElement
from abc import ABC, abstractmethod

class TokenType:
    Unknown = 0
    Word = 1
    Abbreviation = 2
    CharSequence = 3
    GeneralPunctuation = 4
    OpeningPunctuation = 5
    ClosingPunctuation = 6
    Date = 7
    Time = 8
    Variable = 9
    Number = 10
    Measurement = 11
    Whitespace = 12
    Acronym = 13
    Uri = 14
    OtherTextPlaceable = 15
    UserDefined = 16
    Tag = 17
    AlphaNumeric = 18

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

    def set_token_type(self, type:TokenType):
        pass

    def is_punctuation(self):
        return (self.type == TokenType.GeneralPunctuation or
                self.type == TokenType.OpeningPunctuation or
                self.type == TokenType.ClosingPunctuation)

    @property
    def is_word(self):
        return (self.type == TokenType.Word or
                self.type == TokenType.Abbreviation or
                self.type == TokenType.Acronym or
                self.type == TokenType.Uri or
                self.type == TokenType.OtherTextPlaceable)

    @property
    def is_whitespace(self):
        return self.type == TokenType.Whitespace

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



