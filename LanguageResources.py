from ResourceStorage import ResourceStorage

class LanguageResources:
    def __init__(self, _culture_name):
        self.culture_name = _culture_name
        self.accessor = ResourceStorage()
        self.abbreviations_status = self.accessor.get_resource_status(self.culture_name, 'Abbreviations', True)
        self.stopwords_status = self.accessor.get_resource_status(self.culture_name, 'Stopwords', True)
        self.stemming_rules_status = self.accessor.get_resource_status(self.culture_name, 'StemmingRules', True)

if __name__ == "__main__":
    lr = LanguageResources('en-US')