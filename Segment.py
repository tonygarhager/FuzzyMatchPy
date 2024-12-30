from SegmentRange import SegmentPosition
from Text import Text
from typing import Tuple, List
from StringUtils import StringUtils
from TokenBundle import TokenBundle
from Tag import *
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils

class Segment:
    def __init__(self, culture_name:str = 'InvariantCulture'):
        self.elements = []
        self.culture_name = culture_name
        self.tokens = None

    def is_empty(self):
        return not self.elements or len(self.elements) == 0

    def last_element(self):
        if self.is_empty():
            return None
        return self.elements[len(self.elements) - 1]

    def add(self, element):
        if len(self.elements) > 0 and isinstance(element, Text) and isinstance(self.last_element(), Text):
            text = Text(self.last_element())
            text.value += element.value
            return
        self.elements.append(element)

    def add_text(self, txt:str):
        if len(self.elements) > 0 and isinstance(self.last_element(), Text):
            text = Text(self.last_element())
            text.value += txt
            return
        self.elements.append(Text(txt))

    @staticmethod
    def _trim_element(t:Text, trailing:bool) -> Tuple[bool, str]:
        trimmed:str = None
        if isinstance(t, Text) == False:
            return False, str
        if trailing:
            t.value, trimmed = StringUtils.trim_end(t.value, StringUtils.whitespace_characters)
        else:
            t.value, trimmed = StringUtils.trim_start(t.value, StringUtils.whitespace_characters)
        return len(t.value) == 0, trimmed

    def trim_start(self) -> str:
        text:str = None
        flag:bool = True
        while flag:
            flag = False
            if len(self.elements) > 0:
                flag, text2 = Segment._trim_element(self.elements[0], False)
                if text2 is not None:
                    if not text:
                        text = text2
                    else:
                        text += text2
                if flag:
                    del self.elements[0]
        return text

    def trim_end(self) -> str:
        text:str = None
        flag:bool = True
        while flag:
            flag = False
            if len(self.elements) > 0:
                flag, text2 = Segment._trim_element(self.elements[len(self.elements) - 1], True)
                if text2 is not None:
                    if not text:
                        text = text2
                    else:
                        text = text2 + text
                if flag:
                    del self.elements[len(self.elements) - 1]
        return text

    def has_token_bundles(self):
        if self.tokens is not None:
            return any(isinstance(x, TokenBundle) for x in self.tokens)
        return False

    def renumber_tag_anchors(self, next_tag_anchor, max_alignment_anchor):
        if next_tag_anchor <= 0:
            raise ValueError("nextTagAnchor must be greater than 0")

        dictionary = {}
        flag = False
        num = 0

        for segment_element in self.elements:
            if isinstance(segment_element, Tag):
                tag = segment_element
                if tag.type == TagType.Start or tag.type == TagType.End:
                    # Handle Start and End tag types
                    if tag.anchor in dictionary:
                        previous_anchor = dictionary[tag.anchor]
                        flag |= (tag.anchor != previous_anchor)
                        tag.anchor = previous_anchor
                    else:
                        dictionary[tag.anchor] = next_tag_anchor
                        flag |= (tag.anchor != next_tag_anchor)
                        tag.anchor = next_tag_anchor
                        next_tag_anchor += 1
                elif tag.type == TagType.Standalone or tag.type == TagType.TextPlaceholder or tag.type == TagType.LockedContent:
                    # Handle Standalone, TextPlaceholder, LockedContent
                    flag |= (tag.anchor != next_tag_anchor)
                    tag.anchor = next_tag_anchor
                    next_tag_anchor += 1
                else:
                    raise Exception("Unexpected TagType")

                # Update the maximum anchor values
                num = max(num, tag.anchor)
                max_alignment_anchor = max(max_alignment_anchor, tag.alignment_anchor)

        return flag, max_alignment_anchor

    @staticmethod
    def _parse_segment(root: ET.Element):
        """Parses XML element into a dictionary representation for the Segment."""
        # This is an assumed method to parse the XML element into a dict
        culture_name = root.find('CultureName').text
        segment = Segment(culture_name)
        elements = root.find('Elements')
        for element in elements:
            if element.tag == 'Tag':
                segment.elements.append(Tag.from_xml(element))
            elif element.tag == 'Text':
                segment.elements.append(Text.from_xml(element))
        return segment

    def is_valid(self):
        return True#mod

    def __str__(self):
        sb = ''
        if self.elements is None:
            return sb
        for element in self.elements:
            if element is not None:
                sb += str(element)
        return sb

    def to_plain(self, tolower:bool, tobase:bool) -> Tuple[str, List[SegmentPosition]]:
        sb = ''
        ranges = []
        if self.elements is None:
            return sb, ranges
        for i in range(len(self.elements)):
            if self.elements[i] is None or isinstance(self.elements[i], Text) == False:
                continue
            text = self.elements[i]
            value = text.value

            for j in range(len(value)):
                c = value[j]
                if tolower:
                    c = c.lower()
                if tobase:
                    c = StringUtils.to_base(c)
                sb += c
                ranges.append(SegmentPosition(i, j))

        return sb, ranges
