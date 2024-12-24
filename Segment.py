from Text import Text
from typing import Tuple
from StringUtils import StringUtils

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
        if not t:
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
