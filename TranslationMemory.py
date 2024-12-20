import datetime
from LanguagePair import LanguagePair

class TranslationMemory:
    def __init__(self,
                 _id:int,
                 _guid,
                 _name:str,
                 _srcLang:str,
                 _trgLang:str,
                 _recognizers:int,
                 _creationUser:str,
                 _creationDate:datetime,
                 _copyright:str,
                 _description:str,
                 _expirationDate:datetime,
                 _tokenizerFlags:int,
                 _wordCountFlags:int):
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
        self.fuzzy_indexes = 0