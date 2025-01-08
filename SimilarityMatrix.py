import asyncio

from SimilarityComputers import SimilarityComputers


class SimilarityMatrix:
    UNCOMPUTED = -1000.0

    def __init__(self, source_tokens, target_tokens, use_string_edit_distance, disabled_auto_substitutions, characters_normalize_safely, apply_small_change_adjustment):
        self.source_tokens = source_tokens
        self.target_tokens = target_tokens
        self._use_string_edit_distance = use_string_edit_distance
        self._disabled_auto_substitutions = disabled_auto_substitutions
        self._characters_normalize_safely = characters_normalize_safely
        self._apply_small_change_adjustment = apply_small_change_adjustment
        self._sim = [[self.UNCOMPUTED for _ in target_tokens] for _ in source_tokens]

    def is_assigned(self, s, t):
        return self._sim[s][t] != self.UNCOMPUTED

    def set_element_at(self, s, t, value):
        self._sim[s][t] = value

    def get_element_at(self, s, t):
        value = self._sim[s][t]
        if value != self.UNCOMPUTED:
            return value
        similarity = SimilarityComputers.get_token_similarity(
            self.source_tokens[s],
            self.target_tokens[t],
            self._use_string_edit_distance,
            self._disabled_auto_substitutions,
            self._characters_normalize_safely,
            self._apply_small_change_adjustment
        )
        self._sim[s][t] = similarity
        return similarity

    def count_uncomputed_values(self):
        return sum(1 for i in range(len(self.source_tokens))
                      for j in range(len(self.target_tokens))
                      if self._sim[i][j] == self.UNCOMPUTED)

    def compute_async(self, compute_diagonal_only):
        for i in range(len(self.source_tokens)):
            for j in range(len(self.target_tokens)):
                if self._sim[i][j] == self.UNCOMPUTED:
                    if compute_diagonal_only and i != j:
                        self._sim[i][j] = -1.0
                    else:
                        self._sim[i][j] = SimilarityComputers.get_token_similarity(
                            self.source_tokens[i],
                            self.target_tokens[j],
                            self._use_string_edit_distance,
                            self._disabled_auto_substitutions,
                            self._characters_normalize_safely,
                            self._apply_small_change_adjustment
                        )