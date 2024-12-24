from LanguageResources import *
from typing import List
from LanguageTools import LanguageTools

class AnnotatedTranslationMemory:
    def __init__(self, tm_resources: List[LanguageResources], resources_write_count: int, tm):
        self.tm = tm
        self.resources_write_count = resources_write_count
        self.tm_resources = tm_resources
        self._source_tools: LanguageTools = None
        self._target_tools: LanguageTools = None

    def source_tools(self) -> LanguageTools:
        if (self._source_tools is not None):
            return self._source_tools
        resources = LanguageResources(self.tm.languageDirection['srcLang'])
        self._source_tools = LanguageTools(resources, self.tm.recognizers, self.tm.tokenizerFlags, True, True)
        return self._source_tools

    def target_tools(self) -> LanguageTools:
        if (self._target_tools is not None):
            return self._target_tools
        resources = LanguageResources(self.tm.languageDirection['trgLang'])
        self._target_tools = LanguageTools(resources, self.tm.recognizers, self.tm.tokenizerFlags, True, True)
        return self._target_tools