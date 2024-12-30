
class CharSubstringScoreProvider:
    def get_align_score(self, a:str, b:str) -> int:
        if a == b:
            return 3
        return -100

    def get_source_skip_score(self, a:str) -> int:
        return -100

    def get_target_skip_score(self, a:str) -> int:
        return -100

    @property
    def maybe_skip(self):
        return True

