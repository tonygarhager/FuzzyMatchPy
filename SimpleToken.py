from Token import *
from SegmentElement import SegmentElement

class SimpleToken(Token):
    def __init__(self, text:str = '', t:TokenType = TokenType.Unknown):
        self.text = text
        self._type = t
        self.is_stopword = False
        self.stem = ''

    @property
    def is_placeable(self):
        return (self._type == TokenType.Acronym or
                self._type == TokenType.Variable or
                self._type == TokenType.Uri or
                self._type == TokenType.AlphaNumeric or
                self._type == TokenType.OtherTextPlaceable)

    @property
    def is_substitutable(self):
        return (self.type == TokenType.Acronym or
                self.type == TokenType.Variable or
                self.type == TokenType.AlphaNumeric)

    def get_similarity(self, other):
        bundle_similarity = super().get_bundle_similarity(other)

        if not other or self.type != other.type:
            return bundle_similarity

        if not isinstance(other, SimpleToken) or self.type != other.type:
            return SegmentElement.Similarity.Non

        flag = self.text == other.text#mod using CultureInfo.CompareInfo.Compare

        if (self.type == TokenType.Variable or
            self.type == TokenType.Acronym or
            self.type == TokenType.OtherTextPlaceable or
            self.type == TokenType.AlphaNumeric):
            if flag == False:
                return SegmentElement.Similarity.IdenticalType
            return SegmentElement.Similarity.IdenticalValueAndType
        else:
            if flag == False:
                return SegmentElement.Similarity.Non
            return SegmentElement.Similarity.IdenticalValueAndType

    def get_token_type(self)->TokenType:
        return self._type

    def set_token_type(self, type:TokenType):
        self._type = type

class GenericPlaceableToken(SimpleToken):
    def __init__(self, text:str, token_class:str, is_subtitutable:bool):
        super().__init__(text, TokenType.OtherTextPlaceable)
        self.token_class = token_class
        self.is_subtitutable = is_subtitutable

