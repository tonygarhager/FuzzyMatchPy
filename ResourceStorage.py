import io
import base64
from ResourceReader import ResourceReader
from CultureInfoExtensions import CultureInfoExtensions
from LanguageResource import *
from Wordlist import Wordlist

class ResourceStatus:
    Loaded = 0
    Loadable = 1
    NotAvailable = 2

class ResourceStorage:
    def __init__(self):
        self.resource_names = None
        reader = ResourceReader('Sdl.LanguagePlatform.NLP.json')
        try:
            reader.open()
            self.resources = reader.resources
        finally:
            reader.close()

    @staticmethod
    def get_resource_type_name(t:LanguageResourceType)->str:
        if t == LanguageResourceType.Variables:
            return "Variables.txt"
        elif t == LanguageResourceType.Abbreviations:
            return "Abbreviations.txt"
        elif t == LanguageResourceType.OrdinalFollowers:
            return "OrdinalFollowers.txt"
        elif t == LanguageResourceType.SegmentationRules:
            return "SegmentationRules.xml"
        elif t == LanguageResourceType.TokenizerSettings:
            return "TokenizerSettings.xml"
        elif t == LanguageResourceType.StemmingRules:
            return "StemmingRules.txt"
        elif t == LanguageResourceType.Stopwords:
            return "Stopwords.txt"
        elif t == LanguageResourceType.DatePatterns:
            return "DatePatterns.xml"
        elif t == LanguageResourceType.TimePatterns:
            return "TimePatterns.xml"
        elif t == LanguageResourceType.NumberPatterns:
            return "NumberPatterns.xml"
        elif t == LanguageResourceType.MeasurementPatterns:
            return "MeasurementPatterns.xml"
        elif t == LanguageResourceType.CharTrigramVector:
            return "CharTrigrams.dat"
        elif t == LanguageResourceType.ShortDateFST:
            return "ShortDate.fst"
        elif t == LanguageResourceType.LongDateFST:
            return "LongDate.fst"
        elif t == LanguageResourceType.ShortTimeFST:
            return "ShortTime.fst"
        elif t == LanguageResourceType.LongTimeFST:
            return "LongTime.fst"
        elif t == LanguageResourceType.CurrencySymbols:
            return "CurrencySymbols.txt"
        elif t == LanguageResourceType.PhysicalUnits:
            return "PhysicalUnits.txt"
        elif t == LanguageResourceType.NumberFST:
            return "Number.fst"
        elif t == LanguageResourceType.MeasurementFST:
            return "Measurement.fst"
        elif t == LanguageResourceType.GenericRecognizers:
            return "GenericRecognizers.xml"
        elif t == LanguageResourceType.ShortDateFSTEx:
            return "ShortDate.fstex"
        elif t == LanguageResourceType.LongDateFSTEx:
            return "LongDate.fstex"
        elif t == LanguageResourceType.ShortTimeFSTEx:
            return "ShortTime.fstex"
        elif t == LanguageResourceType.LongTimeFSTEx:
            return "LongTime.fstex"
        elif t == LanguageResourceType.NumberFSTEx:
            return "Number.fstex"
        elif t == LanguageResourceType.MeasurementFSTEx:
            return "Measurement.fstex"
        elif t == LanguageResourceType.CurrencyFST:
            return "Currency.fst"
        elif t == LanguageResourceType.CurrencyFSTEx:
            "Currency.fstex"
        raise Exception("Illegal enum")

    def get_name(self, culture_prefix:str, t:LanguageResourceType)->str:
        sb = ''
        if culture_prefix is not None and culture_prefix != '':
            sb += culture_prefix + '_'
        sb += ResourceStorage.get_resource_type_name(t)
        return sb

    def find(self, full_name):
        return next((s for s in self.resources.keys() if s.lower() == full_name.lower()), None)

    def get_resource_name(self, culture_name:str, t:LanguageResourceType, fall_back:bool)->str:
        name = self.get_name(culture_name, t)
        text = self.find(name)

        if not fall_back:
            return text

        flag = False

        while text is None and culture_name != 'InvariantCulture':
            if CultureInfoExtensions.get_lcid_from_culture_name(CultureInfoExtensions.get_parent_culture(culture_name)) == 127 and not flag:
                language_group_name = CultureInfoExtensions.get_language_group_name(culture_name)

                if language_group_name is not None:
                    name = self.get_name(language_group_name, t)
                    text = self.find(name)
                flag = True
            else:
                culture_name = CultureInfoExtensions.get_parent_culture(culture_name)
                name = self.get_name(culture_name, t)
                text = self.find(name)

        return text

    def get_resource_status(self, culture_name:str, t:LanguageResourceType, fall_back:bool) -> ResourceStatus:
        resource_name = self.get_resource_name(culture_name, t, fall_back)

        if resource_name is not None:
            return ResourceStatus.Loadable
        return ResourceStatus.NotAvailable

    def get_resource_data(self, culture_name, t, fall_back):
        resource_name = self.get_resource_name(culture_name, t, fall_back)

        if resource_name is not None and self.resources.get(resource_name) is not None:
            str = self.resources.get(resource_name)
            byte_array = base64.b64decode(str)
            return byte_array
        return None

    def read_resource_data(self, culture_name, t, fall_back):
        resource_data = self.get_resource_data(culture_name, t, fall_back)
        if not resource_data:
            return None

        memory_stream = io.BytesIO()
        memory_stream.write(resource_data)
        memory_stream.seek(0)

        return memory_stream

    @staticmethod
    def load_wordlist(accessor, culture_name:str, t:LanguageResourceType, fall_back:bool) -> Wordlist:
        stream = accessor.read_resource_data(culture_name, t, fall_back)
        if not stream:
            return None
        wordlist = Wordlist()
        wordlist.load_stream(stream, True)
        return wordlist

if __name__ == "__main__":
    storage = ResourceStorage()
    memory_stream = storage.read_resource_data('en-US', 'CurrencySymbols', True)
    from Wordlist import Wordlist
    wordlist = Wordlist()
    wordlist.load_internal(memory_stream, True)

