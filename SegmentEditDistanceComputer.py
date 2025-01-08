

class SegmentEditDistanceComputer:
    def __init__(self, compute_moves:bool = True):
        self._compute_moves = compute_moves

    @staticmethod
    def can_compute_edit_distance(source_token_count:int, target_token_count:int) -> bool:
        return source_token_count * target_token_count <= 4194304