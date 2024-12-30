from StringUtils import *

class CaseAwareCharSubsequenceScoreProvider:
    def __init__(self, use_to_base=True, normalize_widths=False):
        """
        Initializes the CaseAwareCharSubsequenceScoreProvider.

        Args:
            use_to_base (bool): Whether to use base character comparison.
            normalize_widths (bool): Whether to normalize character widths.
        """
        self._use_to_base = use_to_base
        self._normalize_widths = normalize_widths

    def get_align_score(self, a, b):
        """
        Gets the alignment score for two characters.

        Args:
            a (char): First character.
            b (char): Second character.

        Returns:
            int: Alignment score.
        """
        if a == b:
            return 2

        a = a.lower()
        b = b.lower()

        if a == b:
            return 1

        if self._use_to_base:
            a = StringUtils.to_base(a)
            b = StringUtils.to_base(b)
            if a == b:
                return 1

        if not self._normalize_widths:
            return -1

        text_a = StringUtils.half_width_to_full_width(a)
        text_b = StringUtils.half_width_to_full_width(b)

        if text_a == text_b:
            return 1

        return -1

    def get_source_skip_score(self, a):
        """
        Gets the score for skipping a source character.

        Args:
            a (char): Character to skip.

        Returns:
            int: Skip score.
        """
        return -1

    def get_target_skip_score(self, a):
        """
        Gets the score for skipping a target character.

        Args:
            a (char): Character to skip.

        Returns:
            int: Skip score.
        """
        return -1

    @property
    def may_skip(self):
        """
        Indicates whether skipping is allowed.

        Returns:
            bool: True if skipping is allowed, otherwise False.
        """
        return True


