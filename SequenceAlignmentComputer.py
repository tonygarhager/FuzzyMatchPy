from typing import List, Callable
from dataclasses import dataclass

@dataclass
class Substring:
    start: int
    length: int

class AlignedSubstring:
    def __init__(self, source=None, target=None, score=0, length=0):
        if isinstance(source, Substring) and isinstance(target, Substring):
            self.source = source
            self.target = target
            self.score = score
            self.length = length
        elif isinstance(source, int) and isinstance(target, int):
            self.source = Substring(source, score)
            self.target = Substring(target, length)
            self.score = score
            self.length = length
        else:
            self.source = Substring(source[0], source[1])
            self.target = Substring(target[0], target[1])
            self.score = score
            self.length = length

    def __str__(self):
        return f"({self.source.start},{self.source.start + self.source.length - 1}-{self.target.start},{self.target.start + self.target.length - 1},{self.score})"


class SequenceAlignmentComputer:
    class Operation:
        ALIGN = 0
        NOISE = 1
        SKIP = 2

    class Cell:
        def __init__(self):
            self.score = 0
            self.back_i = -1
            self.back_j = -1
            self.op = None
            self.ul_max_score = 0

        def __str__(self):
            return f"{self.score}->{self.back_i}/{self.back_j}"

    def __init__(self, source, target, scorer, picker, min_length, max_items):
        if source is None:
            raise ValueError("source cannot be None")
        if target is None:
            raise ValueError("target cannot be None")
        if scorer is None:
            raise ValueError("scorer cannot be None")
        if min_length <= 0:
            min_length = 1
        if max_items < 0:
            max_items = 0

        self._source = source
        self._target = target
        self._scorer = scorer
        self._picker = picker
        self._min_length = min_length
        self._max_items = max_items
        self._alignment_scores = None
        self._table = None
        self._source_skip_scores = None
        self._target_skip_scores = None

    @staticmethod
    def compute_scores(source, target, scorer):
        alignment_scores = [[0] * len(target) for _ in range(len(source))]
        for i in range(len(source)):
            for j in range(len(target)):
                a = source[i]
                b = target[j]
                alignment_scores[i][j] = scorer.get_align_score(a, b)
        return alignment_scores

    @staticmethod
    def compute_coverage(source, target, scorer, picker, min_length=1, max_items=0):
        return SequenceAlignmentComputer(source, target, scorer, picker, min_length, max_items).compute()

    @staticmethod
    def compute_longest_common_subsequence(source, target, min_length, scorer, picker):
        return SequenceAlignmentComputer(source, target, scorer, picker, min_length, 1).compute()

    def compute_skip_score_caches(self):
        self._source_skip_scores = [self._scorer.get_source_skip_score(x) for x in self._source]
        self._target_skip_scores = [self._scorer.get_target_skip_score(x) for x in self._target]

    def compute_full_table(self, may_skip):
        for i in range(1, len(self._source) + 1):
            for j in range(1, len(self._target) + 1):
                self._table[i][j].score = 0
                num = self._alignment_scores[i - 1][j - 1]
                num2 = self._table[i - 1][j - 1].score + num
                if num2 > self._table[i][j].score:
                    self._table[i][j].score = num2
                    self._table[i][j].back_i = i - 1
                    self._table[i][j].back_j = j - 1
                    self._table[i][j].op = SequenceAlignmentComputer.Operation.ALIGN if num > 0 else SequenceAlignmentComputer.Operation.NOISE

                if may_skip:
                    num3 = self._table[i - 1][j].score + self._source_skip_scores[i - 1]
                    if num3 > self._table[i][j].score:
                        self._table[i][j].score = num3
                        self._table[i][j].back_i = i - 1
                        self._table[i][j].back_j = j
                        self._table[i][j].op = SequenceAlignmentComputer.Operation.SKIP

                    num4 = self._table[i][j - 1].score + self._target_skip_scores[j - 1]
                    if num4 > self._table[i][j].score:
                        self._table[i][j].score = num4
                        self._table[i][j].back_i = i
                        self._table[i][j].back_j = j - 1
                        self._table[i][j].op = SequenceAlignmentComputer.Operation.SKIP

                max_score = max(self._table[i - 1][j - 1].ul_max_score, self._table[i - 1][j].ul_max_score, self._table[i][j - 1].ul_max_score)
                self._table[i][j].ul_max_score = max_score

    def compute_maxima_for_coverage(self, maxima, upto_source, upto_target, may_skip, blocked):
        maxima.clear()
        global_max = 0
        for i in range(1, upto_source + 1):
            for j in range(1, upto_target + 1):
                self._table[i][j].score = 0
                if blocked is None or not blocked[i][j]:
                    num = self._alignment_scores[i - 1][j - 1]
                    num2 = self._table[i - 1][j - 1].score + num
                    if num2 > self._table[i][j].score:
                        self._table[i][j].score = num2
                        self._table[i][j].back_i = i - 1
                        self._table[i][j].back_j = j - 1
                        self._table[i][j].op = SequenceAlignmentComputer.Operation.ALIGN if num > 0 else SequenceAlignmentComputer.Operation.NOISE

                    if may_skip:
                        num3 = self._table[i - 1][j].score + self._source_skip_scores[i - 1]
                        if num3 > self._table[i][j].score:
                            self._table[i][j].score = num3
                            self._table[i][j].back_i = i - 1
                            self._table[i][j].back_j = j
                            self._table[i][j].op = SequenceAlignmentComputer.Operation.SKIP

                        num4 = self._table[i][j - 1].score + self._target_skip_scores[j - 1]
                        if num4 > self._table[i][j].score:
                            self._table[i][j].score = num4
                            self._table[i][j].back_i = i
                            self._table[i][j].back_j = j - 1
                            self._table[i][j].op = SequenceAlignmentComputer.Operation.SKIP

                    if self._table[i][j].score > global_max:
                        maxima.clear()
                        global_max = self._table[i][j].score
                        maxima.append((i, j))
                    elif self._table[i][j].score > 0 and self._table[i][j].score == global_max:
                        maxima.append((i, j))

    def compute_maxima_for_lcs(self, maxima, upto_source, upto_target):
        maxima.clear()
        global_max = self._table[upto_source][upto_target].ul_max_score
        for i in range(upto_source, 0, -1):
            if self._table[i][upto_target].ul_max_score >= global_max:
                for j in range(upto_target, 0, -1):
                    if self._table[i][j].score == global_max:
                        maxima.append((i, j))
                        return

    def compute(self, upto_source=None, upto_target=None):
        if upto_source is None:
            upto_source = len(self._source)
        if upto_target is None:
            upto_target = len(self._target)

        list_ = []
        list2 = []

        if self._alignment_scores is None:
            self._alignment_scores = self.compute_scores(self._source, self._target, self._scorer)

        may_skip = self._scorer.may_skip
        if may_skip and (self._source_skip_scores is None or self._target_skip_scores is None):
            self.compute_skip_score_caches()

        if self._table is None:
            self._table = [[SequenceAlignmentComputer.Cell() for _ in range(len(self._target) + 1)] for _ in range(len(self._source) + 1)]
            self.compute_full_table(may_skip)

        array = None
        if self._max_items != 1:
            array = [[False] * (len(self._target) + 1) for _ in range(len(self._source) + 1)]

        while list2:
            score = None
            if self._max_items != 1:
                self.compute_maxima_for_coverage(list2, upto_source, upto_target, may_skip, array)
            else:
                self.compute_maxima_for_lcs(list2, upto_source, upto_target)

            if list2:
                list3 = []
                for pair in list2:
                    num, num2 = pair
                    num3 = 0
                    while self._table[num][num2].score > 0:
                        cell = self._table[num][num2]
                        if cell.op == SequenceAlignmentComputer.Operation.ALIGN:
                            num3 += 1
                        num = cell.back_i
                        num2 = cell.back_j

                    item = (num, pair[0] - num, num2, pair[1] - num2, score, num3)
                    if num3 >= self._min_length:
                        list3.append(item)

                if not list3:
                    list2.clear()
                else:
                    aligned_substring = self._picker.pick_extension(list_, list3) if self._picker else list3[0]
                    if aligned_substring is None:
                        break
                    if array:
                        for i in range(1, upto_source + 1):
                            for j in range(1, upto_target + 1):
                                if (i > aligned_substring[0] and i <= aligned_substring[0] + aligned_substring[1]) or (j > aligned_substring[2] and j <= aligned_substring[2] + aligned_substring[3]):
                                    array[i][j] = True
                    list_.append(aligned_substring)

        return list_
