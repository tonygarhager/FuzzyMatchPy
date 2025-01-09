from typing import List, Optional
from Label import Label

class MatchState:
    def __init__(self, state: int):
        self.state = state
        self.output: List[Label] = []
        self.input_position = 0
        self.consumed_symbols = 0

    def __copy__(self):
        # Creating a copy of the current match state
        new_state = MatchState(self.state)
        new_state.output = self.output.copy()
        new_state.input_position = self.input_position
        new_state.consumed_symbols = self.consumed_symbols
        return new_state

    def get_output_as_string(self) -> Optional[str]:
        if not self.output:
            return None
        result = []
        for label in self.output:
            if label.is_char_label:
                result.append(chr(label.symbol))
            elif label.symbol == -7:
                result.append(' ')
        return ''.join(result)

    def append_output(self, label: Label):
        if label.is_consuming:
            self.output.append(label)

    def traverse(self, input_str: str, transition: "FSTTransition", mode: str, ignore_case: bool) -> Optional["MatchState"]:
        if mode == "Analyse":
            label = transition.input
            label2 = transition.output
        elif mode == "Generate":
            label = transition.output
            label2 = transition.input
        else:
            raise Exception("Illegal case constant")

        if not label.matches(input_str, self.input_position, ignore_case):
            return None

        match_state = self.__copy__()
        match_state.state = transition.target
        if label2.is_consuming:
            match_state.append_output(label2)

        if not label.is_consuming:
            return match_state

        match_state.consumed_symbols += 1
        match_state.input_position += 1
        return match_state
