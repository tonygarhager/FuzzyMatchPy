class TokenIndexLcsScoreProvider:
    def __init__(self, sim_matrix, threshold, may_skip):
        """
        Initializes the TokenIndexLcsScoreProvider instance.

        :param sim_matrix: An instance of SimilarityMatrix.
        :param threshold: A double value representing the threshold for alignment scoring.
        :param may_skip: A boolean indicating whether skipping is allowed.
        """
        self._sim_matrix = sim_matrix
        self._threshold = threshold
        self.may_skip = may_skip

    def get_align_score(self, a, b):
        """
        Computes the alignment score between two indices.

        :param a: The source index.
        :param b: The target index.
        :return: An integer alignment score.
        """
        num = self._sim_matrix.get_element_at(a, b)
        return 1 if num >= self._threshold else -100000

    def get_source_skip_score(self, a):
        """
        Computes the skip score for a source index.

        :param a: The source index.
        :return: An integer skip score.
        """
        return -1 if self.may_skip else -100000

    def get_target_skip_score(self, a):
        """
        Computes the skip score for a target index.

        :param a: The target index.
        :return: An integer skip score.
        """
        return -1 if self.may_skip else -100000
