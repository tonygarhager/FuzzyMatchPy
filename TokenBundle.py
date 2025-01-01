from rapidfuzz.distance.DamerauLevenshtein import similarity

from Token import *

class PrioritizedToken:
    def __init__(self, token, priority):
        self.token = token
        self.priority = priority

class TokenBundle(Token):
    def __init__(self, t:Token, priority:int):
        self.text = t.text
        self.alternatives = [PrioritizedToken(t, priority)]
        self.culture_name = t.culture_name

    def __len__(self):
        return len(self.alternatives)

    def add(self, t:Token, priority:int):
        self._add(t, priority, True)

    def _add(self, t:Token, priority:int, keep_duplicates:bool):
        if keep_duplicates or len(self.alternatives) == 0:
            self.alternatives.append(PrioritizedToken(t, priority))
            return

        num = -1
        for i in range(len(self.alternatives)):
            flag = t.get_similarity(self.alternatives[i].token) == SegmentElement.Similarity.IdenticalValueAndType
            if flag and (num < 0 or self.alternatives[i].priority >= self.alternatives[num].priority):
                num = i
        if num < 0:
            self.alternatives.append(PrioritizedToken(t, priority))
            return
        if self.alternatives[num].priority >= priority:
            return
        del self.alternatives[num]
        self.alternatives.append(PrioritizedToken(t, priority))

    def __getitem__(self, item):
        return self.alternatives[item]

    def get_best(self):
        index = 0
        priority = self.alternatives[index].priority

        for i in range(len(self.alternatives)):
            if priority < self.alternatives[i].priority:
                index = i
                priority = self.alternatives[i].priority
        return self.alternatives[index].token

    def sort_by_decreasing_priority(self):
        if self.alternatives is None or len(self.alternatives) < 2:
            return
        self.alternatives.sort(key=lambda token: token.priority, reverse=True)

    def contains(self, t:Token):
        return (
                self.alternatives is not None and
                len(self.alternatives) != 0 and
                any(t == x.token for x in self.alternatives)
        )

    def get_tokens(self):
        return self.alternatives[0].token.type

    def is_placeable(self):
        return any(x.token.is_placeable for x in self.alternatives)

    def is_substitutable(self):
        return any(x.token.is_substitutable for x in self.alternatives)

    def get_similarity(self, other):
        if not isinstance(other, Token):
            return SegmentElement.Similarity.Non
        sim1 = SegmentElement.Similarity.Non
        for prioritized_token in self.alternatives:
            sim2 = other.get_similarity(prioritized_token.token)

            if sim1 < sim2:
                sim1 = sim2
        return sim1






