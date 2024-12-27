from SegmentElement import SegmentElement
from Tag import Tag
from Token import Token, TokenType


class TagToken(Token):
    def __init__(self, tag:Tag):
        super().__init__(tag.to_string())
        self.tag = tag

    def update_value(self, blue_print, update_values_only:bool = False):
        if blue_print.tag is None:
            self.tag = None
            self.text = None
            return
        if update_values_only:
            self.tag.tagid = blue_print.tag.tagid
            self.tag.text_equivalent = blue_print.tag.text_equivalent
            self.text = blue_print.to_string()
            return
        self.tag = blue_print.tag
        self.text = blue_print.to_string()

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

    def to_string(self):
        if self.tag is not None:
            return self.tag.to_string()
        return '(null)'




