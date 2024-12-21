from ResourceReader import ResourceReader
from CultureInfoExtensions import CultureInfoExtensions

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
    def get_resource_type_name(t):
        if t == "Variables":
            return "Variables.txt"
        elif t == "Abbreviations":
            return "Abbreviations.txt"
        elif t == "OrdinalFollowers":
            return "OrdinalFollowers.txt"
        elif t == "SegmentationRules":
            return "SegmentationRules.xml"
        elif t == "TokenizerSettings":
            return "TokenizerSettings.xml"
        elif t == "StemmingRules":
            return "StemmingRules.txt"
        elif t == "Stopwords":
            return "Stopwords.txt"
        elif t == "DatePatterns":
            return "DatePatterns.xml"
        elif t == "TimePatterns":
            return "TimePatterns.xml"
        elif t == "NumberPatterns":
            return "NumberPatterns.xml"
        elif t == "MeasurementPatterns":
            return "MeasurementPatterns.xml"
        elif t == "CharTrigramVector":
            return "CharTrigrams.dat"
        elif t == "ShortDateFST":
            return "ShortDate.fst"
        elif t == "LongDateFST":
            return "LongDate.fst"
        elif t == "ShortTimeFST":
            return "ShortTime.fst"
        elif t == "LongTimeFST":
            return "LongTime.fst"
        elif t == "CurrencySymbols":
            return "CurrencySymbols.txt"
        elif t == "PhysicalUnits":
            return "PhysicalUnits.txt"
        elif t == "NumberFST":
            return "Number.fst"
        elif t == "MeasurementFST":
            return "Measurement.fst"
        elif t == "GenericRecognizers":
            return "GenericRecognizers.xml"
        elif t == "ShortDateFSTEx":
            return "ShortDate.fstex"
        elif t == "LongDateFSTEx":
            return "LongDate.fstex"
        elif t == "ShortTimeFSTEx":
            return "ShortTime.fstex"
        elif t == "LongTimeFSTEx":
            return "LongTime.fstex"
        elif t == "NumberFSTEx":
            return "Number.fstex"
        elif t == "MeasurementFSTEx":
            return "Measurement.fstex"
        elif t == "CurrencyFST":
            return "Currency.fst"
        elif t == "CurrencyFSTEx":
            "Currency.fstex"
        raise Exception("Illegal enum")

    def get_name(self, culture_prefix, t):
        sb = ''
        if culture_prefix is not None:
            sb += culture_prefix + '_'
        sb += ResourceStorage.get_resource_type_name(t)
        return sb

    def find(self, full_name):
        return next((s for s in self.resources.keys() if s.lower() == full_name.lower()), None)

    def get_resource_name(self, culture_name, t, fall_back):
        name = self.get_name(culture_name, t)
        text = self.find(name)

        if not fall_back:
            return text

        flag = False

        while text is None and culture_name != 'InvariantCulture':
            if CultureInfoExtensions.get_parent_culture(culture_name) and not flag:
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


if __name__ == "__main__":
    storage = ResourceStorage()
    storage.get_resource_name('en-US', 'CurrencySymbols', True)
