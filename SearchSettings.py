
class SearchSettings:
    def __init__(self,
                 _mode:bool,
                 _max_results:int,
                 _min_score:int):
        self.mode = _mode
        self.max_results = _max_results
        self.min_score = _min_score