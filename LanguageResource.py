
class LanguageResourceType:
    Undefined = 0
    Variables = 1
    Abbreviations = 2
    OrdinalFollowers = 3
    SegmentationRules = 4
    TokenizerSettings = 5
    StemmingRules = 6
    Stopwords = 7
    DatePatterns = 8
    TimePatterns = 9
    NumberPatterns = 10
    MeasurementPatterns = 11
    CharTrigramVector = 12
    ShortDateFST = 13
    LongDateFST = 14
    ShortTimeFST = 15
    LongTimeFST = 16
    CurrencySymbols = 17
    PhysicalUnits = 18
    NumberFST = 19
    MeasurementFST = 20
    GenericRecognizers = 21
    ShortDateFSTEx = 22
    LongDateFSTEx = 23
    ShortTimeFSTEx = 24
    LongTimeFSTEx = 25
    NumberFSTEx = 26
    MeasurementFSTEx = 27
    CurrencyFST = 28
    CurrencyFSTEx = 29

class LanguageResource:
    def __init__(self):
        self.type = LanguageResourceType.Undefined
        self.data = None
        self.culture_name = None