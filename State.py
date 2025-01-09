from FSTTransition import FSTTransition


class State:
    def __init__(self):
        self.transitions = []
        self.transitions_sorted = True
        self.is_initial = False
        self.is_final = False
        self.id = -1

    @property
    def transition_count(self):
        return len(self.transitions)

    def add_transition(self, target, input, output):
        if self.has_transition(target, input, output):
            return
        fst_transition = FSTTransition(self.id, target, input, output)
        self.transitions.append(fst_transition)
        if not self.transitions_sorted or len(self.transitions) <= 1:
            return
        count = len(self.transitions)
        if self.transitions[count - 1].compare_to(self.transitions[count - 2]) <= 0:
            self.transitions_sorted = False

    def remove_transition(self, target, input, output):
        index = self._find_transition_internal(target, input, output)
        if index >= 0:
            self.transitions.pop(index)

    def remove_transition_at(self, index):
        self.transitions.pop(index)

    def has_transition(self, target, input, output):
        return self.find_transition(target, input, output) is not None

    def find_transition(self, target, input, output):
        index = self._find_transition_internal(target, input, output)
        if index >= 0:
            return self.transitions[index]
        return None

    def _find_transition_internal(self, target, input, output):
        for i, transition in enumerate(self.transitions):
            if (transition is not None and
                transition.target == target and
                transition.input == input and
                transition.output == output):
                return i
        return -1

    def sort_transitions(self):
        if len(self.transitions) > 1:
            self.transitions.sort()
        self.transitions_sorted = True

    def ensure_source_state(self):
        for fst_transition in self.transitions:
            if fst_transition and fst_transition.source != self.id:
                return False
        return True

    def is_deterministic(self):
        if not self.transitions or len(self.transitions) == 0:
            return True
        self.sort_transitions()
        if self.transitions[0].is_epsilon():
            return False
        for i in range(1, len(self.transitions)):
            if (self.transitions[i].input.symbol == self.transitions[i - 1].input.symbol and
                self.transitions[i].output.symbol == self.transitions[i - 1].output.symbol) or \
               self.transitions[i].is_epsilon():
                return False
        return True

    def has_epsilon_transitions(self):
        return any(fst_transition.is_epsilon() for fst_transition in self.transitions)
