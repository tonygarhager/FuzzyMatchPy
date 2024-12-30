from abc import ABC, abstractmethod

from pip._internal.resolution.resolvelib import candidates

from SequenceAlignmentComputer import AlignedSubstring


class IExtensionDisambiguator(ABC):
    @abstractmethod
    def pick_extension(self, path:[], candidates:[]):
        pass

class SubstringAlignmentDisambiguator(IExtensionDisambiguator):
    def pick_extension(self, path:[], candidates:[]) -> AlignedSubstring:
        if path is None:
            raise ValueError("path cannot be None")
        if candidates is None:
            raise ValueError("candidates cannot be None")
        if not candidates:
            return None

        if len(candidates) == 1 or not path:
            return candidates[0]

        best_candidate = None

        min_cost = 0
        for candidate in candidates:
            cost = self.compute_costs(path, candidate)
            if best_candidate is None or cost < min_cost:
                min_cost = cost
                best_candidate = candidate

        return best_candidate

    def compute_costs(self, path:[], candidate:[]) -> int:
        if candidates is None:
            raise ValueError("candidates cannot be None")
        num = -1
        for aligned_substring in path:
            if aligned_substring.source.start < candidate.source.start:
                val = candidate.source.start - aligned_substring.source.start - aligned_substring.source.length
            else:
                val = aligned_substring.source.start - candidate.source.start - candidate.source.length

            if aligned_substring.target.start < candidate.target.start:
                val2 = candidate.target.start - aligned_substring.target.start - aligned_substring.target.length
            else:
                val2 = aligned_substring.target.start - candidate.target.start - candidate.target.length

            num2 = max(val, val2)
            if num < 0 or num2 < num:
                num = num2
        return num
