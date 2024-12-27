from typing import List, Optional


class StoSegment:
    def __init__(
        self,
        hash: int,
        relaxed_hash: int,
        text: str,
        plain_text: Optional[str] = None,
        serialized_tags: Optional[bytes] = None,
    ):
        self.hash = hash
        self.relaxed_hash = relaxed_hash
        self.text = text
        self.plain_text = plain_text
        self.serialized_tags = serialized_tags
        self._features: List[int] = []
        self._concordance_features: List[int] = []

    @property
    def features(self) -> List[int]:
        if not self._features:
            self._features = []
        return self._features

    @features.setter
    def features(self, value: List[int]):
        self._features = value

    @property
    def concordance_features(self) -> List[int]:
        if not self._concordance_features:
            self._concordance_features = []
        return self._concordance_features

    @concordance_features.setter
    def concordance_features(self, value: List[int]):
        self._concordance_features = value
