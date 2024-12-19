from LanguagePair import LanguagePair

class TranslationMemory:
    def __init__(self,
                 _id,
                 _guid,
                 _name,
                 _srcLang,
                 _trgLang,
                 _recognizers,
                 _creationUser,
                 _creationDate,
                 _copyright,
                 _description,
                 _expirationDate,
                 _tokenizerFlags,
                 _wordCountFlags):
        self.id = _id
        self.guid = _guid
        self.name = _name
        self.creationUser = _creationUser
        self.creationDate = _creationDate

        self.languageDirection = LanguagePair(_srcLang, _trgLang)
        self.copyright = _copyright
        self.description = _description

        self.expirationDate = _expirationDate
        self.recognizers = _recognizers
        self.tokenizerFlags = _tokenizerFlags
        self.wordCountFlags = _wordCountFlags
        self.fuzzyIndexes = 0