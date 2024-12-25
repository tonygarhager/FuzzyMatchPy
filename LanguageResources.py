from ResourceStorage import ResourceStorage
from LanguageResource import *
from Wordlist import Wordlist


class LanguageResources:
    def __init__(self, _culture_name):
        self.culture_name = _culture_name
        self.accessor = ResourceStorage()
        self.abbreviations_status = self.accessor.get_resource_status(self.culture_name, LanguageResourceType.Abbreviations, True)
        self.stopwords_status = self.accessor.get_resource_status(self.culture_name, LanguageResourceType.Stopwords, True)
        self.stemming_rules_status = self.accessor.get_resource_status(self.culture_name, LanguageResourceType.StemmingRules, True)

    def load_wordlist(self, t:LanguageResourceType)->Wordlist:
        return ResourceStorage.load_wordlist(self.accessor, self.culture_name, t, True)

if __name__ == "__main__":
    lr = LanguageResources('en-US')