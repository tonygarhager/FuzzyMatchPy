from SegmentElement import SegmentElement
from Tag import Tag
from Token import Token, TokenType


class TagToken(Token):
    def __init__(self, tag:Tag = None):
        if tag is not None:
            super().__init__(str(tag))
        self.tag = tag

    def update_value(self, blue_print, update_values_only:bool = False):
        if blue_print.tag is None:
            self.tag = None
            self.text = None
            return
        if update_values_only:
            self.tag.tagid = blue_print.tag.tagid
            self.tag.text_equivalent = blue_print.tag.text_equivalent
            self.text = str(blue_print)
            return
        self.tag = blue_print.tag
        self.text = str(blue_print)

    def get_token_type(self) -> TokenType:
        return TokenType.Tag

    @property
    def is_placeable(self):
        return True

    @property
    def is_substitutable(self):
        return True

    def get_similarity(self, other):
        if (isinstance(other, TagToken) == False or
                self.tag is None or
                other.tag is None):
            return SegmentElement.Similarity.Non
        return self.tag.get_similarity(other.tag)

    def __str__(self):
        if self.tag is not None:
            return str(self.tag)
        return '(null)'





