from typing import Callable, List, Optional
from MatchState import MatchState
from dataclasses import dataclass

@dataclass
class Match:
    index: int
    length: int

@dataclass
class FSTMatch(Match):
    output: str

class Matcher:
    class MatchMode:
        ANALYSE = "Analyse"
        GENERATE = "Generate"

    def __init__(self, fst:'FST'):
        self._fst = fst

    def match(
        self,
        input_str: str,
        match_whole_input: bool,
        mode: str,
        start_offset: int = 0,
        ignore_case: bool = False,
        match_found_callback: Optional[Callable[[MatchState], bool]] = None,
        continue_iteration_callback: Optional[Callable[[int], bool]] = None,
    ) -> Optional[List[MatchState]]:
        if start_offset < 0:
            raise ValueError("start_offset must be non-negative.")
        if not match_found_callback:
            raise ValueError("match_found_callback is required.")

        input_length = len(input_str) if input_str else 0
        if start_offset > input_length:
            return None

        start_state = self._fst.get_start_state()
        if start_state < 0:
            return None

        states = [MatchState(start_state)]
        states[0].input_position = start_offset

        results = []

        if self._fst.is_final(states[0].state) and (not match_whole_input or states[0].input_position >= input_length):
            if not match_found_callback(states[0]):
                return None

        iteration_count = 0
        while states:
            next_states = []
            for match_state in reversed(states):
                state = self._fst.get_state(match_state.state)
                for transition in state.transitions:
                    iteration_count += 1
                    new_match_state = match_state.traverse(input_str, transition, mode, ignore_case)
                    if new_match_state:
                        next_states.append(new_match_state)
                        if self._fst.is_final(new_match_state.state) and (
                            not match_whole_input or new_match_state.input_position >= input_length
                        ):
                            if not match_found_callback(new_match_state):
                                return None

            states = next_states

            if iteration_count % 1000 == 0 and continue_iteration_callback:
                if not continue_iteration_callback(iteration_count):
                    return None

        return results
