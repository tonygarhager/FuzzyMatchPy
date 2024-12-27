
from AbstractAnnotatedSegment import AbstractAnnotatedSegment
from AnnotatedTranslationMemory import AnnotatedTranslationMemory
from LanguageTools import LanguageTools
from Segment import Segment


class AnnotatedSegment(AbstractAnnotatedSegment):
    def __init__(self, tm:AnnotatedTranslationMemory, s:Segment, is_target_segment:bool, keep_tokens:bool, keep_peripheral_whitespace:bool):
        super().__init__(s, keep_tokens, keep_peripheral_whitespace)
        self._tools = tm.target_tools if is_target_segment else tm.source_tools

    @property
    def lingua_language_tool(self) -> LanguageTools:
        return self._tools


