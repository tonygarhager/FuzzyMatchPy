from typing import Tuple, Optional
from Label import Label
from Matcher import Matcher


class FSTTransition:
    def __init__(self, source: int, target: int, input_label: Label, output_label: Label):
        self.source = source
        self.target = target
        self.input = input_label
        self.output = output_label

    @property
    def is_epsilon(self) -> bool:
        return self.input.is_epsilon and self.output.is_epsilon

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FSTTransition):
            return False
        return self.compare_to(other) == 0

    def __hash__(self) -> int:
        return hash((self.source, self.input.symbol, self.output.symbol, self.target))

    def compare_to(self, other: "FSTTransition") -> int:
        diff = self.source - other.source
        if diff == 0:
            diff = self.input.symbol - other.input.symbol
        if diff == 0:
            diff = self.output.symbol - other.output.symbol
        if diff == 0:
            diff = self.target - other.target
        return diff

    def can_traverse(
        self,
        mode: str,
        input_str: str,
        position: int,
        ignore_case: bool,
    ) -> Tuple[Optional[Label], bool]:
        consumed_input = False
        output = None
        if mode == Matcher.MatchMode.ANALYSE:
            label, label2 = self.input, self.output
        elif mode == Matcher.MatchMode.GENERATE:
            label, label2 = self.output, self.input
        else:
            raise Exception("Illegal case constant")

        if not label.matches(input_str, position, ignore_case):
            return None, False

        consumed_input = label.is_consuming
        output = label2
        return output, consumed_input