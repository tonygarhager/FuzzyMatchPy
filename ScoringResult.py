from EditDistance import *
from Penalty import *
from SegmentRange import SegmentRange
from typing import *

class TextContextMatch:
    NoMatch = 0
    SourceMatch = 1
    SourceTargetMatch = 2
    PrecedingAndFollowingSourceMatch = 3

class ScoringResult:
    def __init__(self):
        self.base_score:int = 0
        self.edit_distance:EditDistance = None
        self.memory_tags_deleted:bool = False
        self.tag_mismatch:bool = False

        self.text_context_match:TextContextMatch = None
        self.is_structure_context_match:bool = False
        self.id_context_match:bool = False
        self.resolved_placeables:int = 0
        self.text_placements:int = 0
        self.placeable_format_changes:int = 0
        self.matching_concordance_ranges:List[SegmentRange] = None
        self.applied_penalties:List[AppliedPenalty] = None
        self.target_segment_differs:bool = False

    @property
    def match(self):
        num = self.base_score

        if not self.applied_penalties:
            if num >= 0:
                return num
            return 0
        else:
            for applied_penalty in self.applied_penalties:
                num -= applied_penalty.malus
            if num >= 0:
                return num
            return 0

    def find_penalty(self, pt:PenaltyType) -> AppliedPenalty:
        if not self.applied_penalties:
            return None
        for applied_penalty in self.applied_penalties:
            if applied_penalty.type == pt:
                return applied_penalty
        return None

    def find_applied_filter(self, filter_name:str) -> AppliedPenalty:
        if not self.applied_penalties:
            return None
        return next(
            (penalty for penalty in self.applied_penalties
             if penalty.type == PenaltyType.FilterPenalty and penalty.filter_name.lower() == filter_name.lower()),
            None
        )

    def apply_penalty(self, pt:Penalty):
        if pt is None:
            return

        applied_penalty = self.find_penalty(pt.penalty_type)
        if applied_penalty:
            if Penalty.can_apply_multiple_times(pt.penalty_type):
                applied_penalty.malus += pt.malus
            return

        if self.applied_penalties is None:
            self.applied_penalties = []

        self.applied_penalties.append(AppliedPenalty(pt.penalty_type, pt.malus))

    def remove_penalty(self, pt):
        if self.applied_penalties is not None:
            ScoringResult.remove_all(self.applied_penalties, lambda x: x.type == pt)

    @staticmethod
    def remove_all(elements:List[AppliedPenalty], d:Callable[[AppliedPenalty], bool]):
        i = 0
        while i < len(elements):
            if d(elements[i]):
                elements.pop(i)
            else:
                i += 1

    def apply_filter(self, filter_name:str, malus:int):
        if self.find_applied_filter(filter_name) is not None:
            return
        if not self.applied_penalties:
            self.applied_penalties = List[AppliedPenalty]
        applied_penalty = AppliedPenalty(PenaltyType.FilterPenalty, malus)
        applied_penalty.filter_name = filter_name
        self.applied_penalties.append(applied_penalty)

    def is_exact_match(self):
        return self.base_score >= 100
