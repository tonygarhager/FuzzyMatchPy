from ResourceStorage import *
from LanguageResource import *
from Wordlist import Wordlist
from StemmingRuleSet import *

class LanguageResources:
    def __init__(self, _culture_name, accessor):
        self.culture_name = _culture_name
        self.accessor = accessor
        self._abbreviations_status:ResourceStatus = self.accessor.get_resource_status(self.culture_name, LanguageResourceType.Abbreviations, True)
        self._stopwords_status:ResourceStatus = self.accessor.get_resource_status(self.culture_name, LanguageResourceType.Stopwords, True)
        self._stemming_rules_status:ResourceStatus = self.accessor.get_resource_status(self.culture_name, LanguageResourceType.StemmingRules, True)
        ###
        self._abbreviations:Wordlist = None
        self._stopwords:Wordlist = None
        self._stemming_rules:StemmingRuleSet = None

    def load_wordlist(self, t:LanguageResourceType)->Wordlist:
        return ResourceStorage.load_wordlist(self.accessor, self.culture_name, t, True)

    def is_abbreviation(self, s:str)->bool:
        self.ensure_abbreviations_loaded()
        return self._abbreviations is not None and self._abbreviations.contains(s)

    def ensure_abbreviations_loaded(self) -> None:
        if self._abbreviations is not None or self._abbreviations_status == ResourceStatus.NotAvailable:
            return
        self._abbreviations = self.load_wordlist(LanguageResourceType.Abbreviations)
        if self._abbreviations is not None:
            self._abbreviations_status = ResourceStatus.Loaded

    @property
    def stoplist_signature(self) -> str:
        if self._stopwords_status == ResourceStatus.NotAvailable or not self._stopwords:
            return 'Stopwords0'
        return 'Stopwords0' + str(self._stopwords.version)

    @property
    def abbreviations_signature(self) -> str:
        self.ensure_abbreviations_loaded()
        if self._abbreviations_status == ResourceStatus.NotAvailable or not self._abbreviations:
            return 'Abbr0'
        list = []
        for text in self._abbreviations.items:
            list.append(text.replace('|', '\\|'))

        list.sort()
        sb = ''
        for str in list:
            sb += str + '|'
        return 'Abbr' + sb

    def is_stopword(self, s:str)->bool:
        if self._stopwords is not None:
            return self._stopwords.contains(s)
        if self._stopwords_status == ResourceStatus.NotAvailable:
            return False
        self._stopwords = self.load_wordlist(LanguageResourceType.Stopwords)
        if self._stopwords is not None:
            self._stopwords_status = ResourceStatus.Loaded
        return self._stopwords is not None and self._stopwords.contains(s)

    @property
    def stemming_rules(self):
        return self._stemming_rules#mod

