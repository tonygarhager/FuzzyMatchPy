from Token import *
from SegmentElement import SegmentElement

class SimpleToken(Token):
    def __init__(self, text, t):
        self.text = text
        self.type = t
        self.is_stopword = False
        self.stem = ''

    def is_placeable(self):
        return (self.type == TokenType.Acronym or
                self.type == TokenType.Variable or
                self.type == TokenType.Uri or
                self.type == TokenType.AlphaNumeric or
                self.type == TokenType.OtherTextPlaceable)

    def is_substitutable(self):
        return (self.type == TokenType.Acronym or
                self.type == TokenType.Variable or
                self.type == TokenType.AlphaNumeric)

    def get_similarity(self, other):
        bundle_similarity = Token.get_bundle_similarity(other)

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

class GenericPlaceableToken(SimpleToken):
    def __init__(self, text:str, token_class:str, is_subtitutable:bool):
        super().__init__(text, TokenType.OtherTextPlaceable)
        self.token_class = token_class
        self.is_subtitutable = is_subtitutable

