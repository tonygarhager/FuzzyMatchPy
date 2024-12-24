
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
        self.mode = _mode
        self.max_results = _max_results
        self.min_score = _min_score

    def is_concordance_search(self) -> bool:
        return self.mode == SearchMode.ConcordanceSearch or self.mode == SearchMode.TargetConcordanceSearch
