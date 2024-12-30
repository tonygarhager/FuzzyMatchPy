from SortSpecification import *
from Penalty import *

class SearchMode:
    ExactSearch = 0
    NormalSearch = 1
    FullSearch = 2
    ConcordanceSearch = 3
    TargetConcordanceSearch = 4
    DuplicateSearch = 5

class SearchSettings:
    min_score_lower_bound = 30
    def __init__(self,
                 _mode:int,
                 _max_results:int,
                 _min_score:int):
        self.is_document_search = False
        self.mode = _mode
        self.max_results = _max_results
        self.min_score = _min_score
        self.sort_spec: SortSpecification = None
        self.check_matching_sub_languages = False
        self.advanced_tokenization_legacy_scoring = False
        self.penalties = None
        self.filters = None

    @property
    def is_concordance_search(self) -> bool:
        return self.mode == SearchMode.ConcordanceSearch or self.mode == SearchMode.TargetConcordanceSearch

    def find_penalty(self, pt:PenaltyType) -> Penalty:
        # List of Penalties (replace with actual list in your implementation)
        penalties = self.penalties
        if penalties is None:
            return None
        return next((p for p in penalties if p.penalty_type == pt), None)

    def add_penalty(self, pt:Penalty, malus:int):
        penalty = self.find_penalty(pt)
        if penalty is not None:
            return
        penalty = Penalty(pt, malus)
        if self.penalties == None:
            self.penalties = []
        self.penalties.append(penalty)
