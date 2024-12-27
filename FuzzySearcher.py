from typing import *
from bisect import bisect_left

class ScoringMethod:
    QUERY = "Query"
    RESULT = "Result"
    DICE = "Dice"

class Hit:
    def __init__(self, k:int, s:int):
        self.key = k
        self.score = s

    def __str__(self):
        return f"key {self.Key}; score {self.Score}"

    def __lt__(self, other):
        return self.score < other.score

    def __eq__(self, other):
        return self.key == other.key and self.score == other.score

class IntFeatureVector(List[int]):
    pass

class PostingsList:
    def __init__(self, feature: int):
        self.feature = feature
        self.keys: List[int] = []

    def add_key(self, key: int):
        """Add a key in sorted order."""
        pos = bisect_left(self.keys, key)
        if pos == len(self.keys) or self.keys[pos] != key:
            self.keys.insert(pos, key)


class AbstractPostingsIterator:
    """Abstract iterator for traversing postings."""
    def __init__(self, postings_list: PostingsList, order_descending: bool):
        self.postings_list = postings_list
        self.order_descending = order_descending
        self.index = len(postings_list.keys) - 1 if order_descending else 0

    @property
    def at_end(self) -> bool:
        return self.index < 0 if self.order_descending else self.index >= len(self.postings_list.keys)

    @property
    def current(self) -> Optional[int]:
        if self.at_end:
            return None
        return self.postings_list.keys[self.index]

    def next(self):
        if not self.at_end:
            self.index -= 1 if self.order_descending else 1


class InMemoryPostingsIterator(AbstractPostingsIterator):
    def __init__(self, postings_list, descending_order):
        self._column = postings_list.keys
        self._descending_order = descending_order
        if self._descending_order:
            self._current = len(self._column) - 1
            self._at_end = (self._current < 0)
        else:
            self._current = 0
            self._at_end = (self._current >= len(self._column))

        if not self._at_end:
            self._current_value = self._column[self._current]

    @property
    def at_end(self):
        return self._at_end

    @property
    def current(self):
        return self._current_value

    def next(self):
        if self._descending_order:
            self._current -= 1
            self._at_end = (self._current < 0)
        else:
            self._current += 1
            self._at_end = (self._current >= len(self._column))

        if not self._at_end:
            self._current_value = self._column[self._current]

        return self._at_end

    @property
    def count(self):
        return len(self._column)

class Storage:
    def __init__(self):
        self._index: Dict[int, PostingsList] = {}
        self._featureVectors: Dict[int, IntFeatureVector] = {}

    def add(self, key: int, fv: IntFeatureVector):
        if not fv or len(fv) == 0:
            return

        if key in self._featureVectors:
            raise Exception("Duplicate key detected")  # Replace with custom exception if needed

        for feature in fv:
            if feature not in self._index:
                self._index[feature] = PostingsList(feature)
            postings_list = self._index[feature]
            postings_list.add_key(key)

        self._featureVectors[key] = fv

    def contains_feature(self, feature: int) -> bool:
        return feature in self._index

    def contains_key(self, key: int) -> bool:
        return key in self._featureVectors

    @property
    def count(self) -> int:
        return len(self._featureVectors)

    def get_postings_count(self, feature: int) -> int:
        postings_list = self._index.get(feature)
        return len(postings_list.keys) if postings_list else 0

    def get_feature_vector(self, key: int) -> Optional[IntFeatureVector]:
        return self._featureVectors.get(key)

    def delete(self, key: int):
        int_feature_vector = self._featureVectors.get(key)
        if not int_feature_vector:
            return

        for feature in int_feature_vector:
            postings_list = self._index.get(feature)
            if postings_list:
                pos = bisect_left(postings_list.keys, key)
                if pos < len(postings_list.keys) and postings_list.keys[pos] == key:
                    postings_list.keys.pop(pos)

        self._featureVectors.pop(key, None)

    def remove(self, key: int) -> Optional[IntFeatureVector]:
        fv = self._featureVectors.get(key)
        if fv:
            self.delete(key)
        return fv

    def get_iterator(self, feature: int, order_descending: bool) -> Optional[AbstractPostingsIterator]:
        postings_list = self._index.get(feature)
        if postings_list is None:
            return None
        return InMemoryPostingsIterator(postings_list, order_descending)

    def __iter__(self) -> Iterator:
        return iter(self._featureVectors.items())

class HitComparer:
    def __init__(self, descending: bool):
        self.descending = descending

    def compare(self, a: Hit, b: Hit) -> int:
        return (b.score - a.score) if self.descending else (a.score - b.score)

class FuzzySearcher:
    def __init__(self, storage):
        self._storage = storage

    def search(
            self, fv: IntFeatureVector, max_results: int, min_score: int, last_key: int,
            scoring_method: ScoringMethod, validate_item_callback: Callable[[int], bool],
            descending_order: bool
    ) -> Optional[List[Hit]]:
        if not fv or len(fv) == 0 or max_results <= 0:
            return None

        min_score = max(0, min(min_score, 100))
        comparer = HitComparer(descending_order)

        hits = []
        iterators = []
        max_count = 0

        for feature in fv:
            iterator = self._storage.get_iterator(feature, descending_order)
            if iterator and iterator.count > 0:
                iterators.append(iterator)
                max_count = max(max_count, iterator.count)

        iterators.sort(key=lambda it: it.count, reverse=descending_order)

        score_threshold = min_score / 100.0
        min_match = 1 if min_score == 0 else len(fv) * min_score // 100
        allowed_misses = len(fv) - min_match

        dice_min = 0
        dice_max = 0

        if scoring_method == ScoringMethod.DICE and min_score > 0:
            num = 2 * len(fv) * (1 - score_threshold)
            dice_min = len(fv) - int(num / (2 - score_threshold))
            dice_max = len(fv) + int(num / score_threshold)

        iterators = [it for it in iterators if not (it.count > 1000 and allowed_misses > 0)]
        i = 0
        while i < len(iterators):
            current_key = max(it.current for it in iterators if not it.at_end) if descending_order else \
                min(it.current for it in iterators if not it.at_end)

            if current_key is None:
                return None

            match_count = sum(1 for it in iterators if not it.at_end and it.current == current_key)
            for it in iterators:
                if not it.at_end and it.current == current_key:
                    it.next()
                    if it.at_end:
                        i += 1

            if descending_order and current_key > last_key or not descending_order and current_key < last_key:
                continue

            feature_vector = self._storage.get_feature_vector(current_key)
            if feature_vector:
                feature_count = len(feature_vector)
                if feature_count == 0 or (dice_min and dice_max and not (dice_min <= feature_count <= dice_max)):
                    continue

                if validate_item_callback and not validate_item_callback(current_key):
                    continue

                if allowed_misses:
                    match_count = len(set(feature_vector) & set(fv))

                if scoring_method == ScoringMethod.QUERY:
                    score = match_count / len(fv)
                elif scoring_method == ScoringMethod.RESULT:
                    score = match_count / feature_count
                elif scoring_method == ScoringMethod.DICE:
                    score = 2 * match_count / (len(fv) + feature_count)
                else:
                    raise ValueError("Invalid scoring method")

                final_score = int(100 * score)
                if final_score >= min_score:
                    hit = Hit(current_key, final_score)
                    hits.append(hit)
                    hits.sort(key=lambda h: h.score, reverse=descending_order)
                    if len(hits) > max_results:
                        hits.pop()

        return hits

class InMemoryFuzzyIndex:
    def __init__(self):
        self.init()

    def init(self):
        self._storage = Storage()
        self._searcher = FuzzySearcher(self._storage)

    def clear(self):
        self._storage = None
        self._searcher = None
        self.init()

    def add(self, key:int, fv:IntFeatureVector):
        self._storage.add(key, fv)

    def delete(self, key:int):
        self._storage.delete(key)

    def remove(self, key:int):
        self._storage.remove(key)

    def contains_key(self, key:int)->bool:
        return self._storage.contains_key(key)

    @property
    def count(self):
        return self._storage.count

    def search(self, fv: IntFeatureVector, max_results: int, min_score: int, last_key: int,
            scoring_method: ScoringMethod, validate_item_callback: Callable[[int], bool],
            descending_order: bool
    ) -> Optional[List[Hit]]:
        return self._searcher.search(fv, max_results, min_score, last_key, scoring_method, validate_item_callback, descending_order)


