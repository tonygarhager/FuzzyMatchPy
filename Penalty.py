
class PenaltyType:
    Unknown = 0
    TagMismatch = 1
    MemoryTagsDeleted = 2
    TargetSegmentMismatch = 3
    FilterPenalty = 4
    ProviderPenalty = 5
    MultipleTranslations = 6
    AutoLocalization = 7
    TextReplacement = 8
    Alignment = 9
    CharacterWidthDifference = 10
    NotTranslated = 11
    Draft = 12
    Translated = 13
    RejectedTranslation = 14
    ApprovedTranslation = 15
    RejectedSignOff = 16
    ApprovedSignOff = 17

class AppliedPenalty:
    def __init__(self, pt: PenaltyType, malus:int):
        self.type = pt
        self.malus = malus
        self.filter_name = None

class Penalty:
    def __init__(self, pt: PenaltyType = PenaltyType.Unknown, malus:int = 0):
        self.penalty_type = pt
        self.malus = malus

    @staticmethod
    def can_apply_multiple_times(pt: PenaltyType):
        return pt == PenaltyType.TagMismatch

