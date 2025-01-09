from Label import Label
from State import State
from bisect import bisect_left
import gzip
import io

class FST:
    reserved_characters = "<>()[]{}<>*+?\\^$|#:"
    _special_chars_array = list(reserved_characters)  # Convert string to list of characters

    Magic = 2007110601

    def __init__(self, alpha = None):
        self._states = {}
        self._start_state = -1
        self._max_state = -1

        # Define the delegate (which is not directly needed in Python)
        self._transition_property = None

        if alpha is None:
            return
        # Initial state
        state = State()
        state.id = 1
        state.is_initial = True
        state.is_final = False
        self._states[state.id] = state
        self._start_state = state.id

        # Other states
        for i in range(2, 7):
            state = State()
            state.id = i
            state.is_initial = False
            state.is_final = False
            self._states[state.id] = state

        self._max_state = 5

        # Final state
        final_state = self._states[6]
        final_state.is_final = True

        # Adding transitions
        FST.add_transitions(self._states[1], self._states[2], "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        FST.add_transitions(self._states[1], self._states[3], "0123456789")
        FST.add_transitions(self._states[2], self._states[2], "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        FST.add_transitions(self._states[2], self._states[2], "-_")
        FST.add_transitions(self._states[3], self._states[3], "0123456789")
        FST.add_transitions(self._states[3], self._states[3], "-_")
        FST.add_transitions(self._states[2], self._states[4], "0123456789")
        FST.add_transitions(self._states[3], self._states[4], "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        FST.add_transitions(self._states[2], self._states[5], "0123456789")
        FST.add_transitions(self._states[3], self._states[5], "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        FST.add_transitions(self._states[4], self._states[4], "0123456789")
        FST.add_transitions(self._states[4], self._states[4], "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        FST.add_transitions(self._states[4], self._states[4], "-_")
        FST.add_transitions(self._states[4], self._states[5], "0123456789")
        FST.add_transitions(self._states[4], self._states[5], "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

        self._states[5].add_transition(6, Label(-4), Label(-4))

    @staticmethod
    def add_transitions(start, end, transitions):
        for c in transitions:
            start.add_transition(end.id, Label(ord(c)), Label(ord(c)))

    @staticmethod
    def is_special(c):
        return c in FST.reserved_characters

    @staticmethod
    def escape_special(c):
        if c in FST._special_chars_array:
            return "\\" + str(c)
        return str(c)

    @staticmethod
    def escape_special_string(s):
        if not s:
            return s
        if not any(c in FST._special_chars_array for c in s):
            return s
        result = []
        for c in s:
            if c in FST._special_chars_array:
                result.append("\\")
            result.append(c)
        return ''.join(result)

    @staticmethod
    def create(expression):
        parser = Parser()
        return parser.parse(expression)

    @staticmethod
    def create(data):
        fst = FST()
        fst.from_binary(data)
        return fst

    def get_state(self, s):
        state = self._states.get(s)
        if state is None:
            return None
        return state

    def get_states(self):
        return list(self._states.keys())

    def get_state_count(self):
        return len(self._states)

    def get_transitions(self, state):
        if not self.state_exists(state):
            raise Exception("State doesn't exist")
        return self._states[state].transitions

    def add_state(self):
        state = State()
        state.id = self._max_state
        self._max_state += 1
        self._states[state.id] = state
        return state.id

    def state_exists(self, s):
        return s in self._states

    def get_first_set(self, for_output):
        result = []

        def callback(t):
            label = t.output if for_output else t.input
            if not label.is_consuming:
                return True

            num = bisect_left(result, label.symbol)
            if num < 0:
                result.insert(~num, label.symbol)

            return False

        self.compute_state_closure(self._start_state, True, callback)
        return result

    def remove_state(self, s):
        if not self.state_exists(s):
            raise Exception("State doesn't exist")

        if s == self._start_state:
            self._start_state = -1

        self.remove_transitions_into(s)
        return self._states.pop(s, None) is not None

    def concatenate(self, rhs):
        final_states = self.get_final_states()
        if not final_states:
            raise Exception("Automaton does not have any final states")

        if not self.state_exists(self._start_state):
            raise Exception("Automaton does not have a start state")

        if not rhs.state_exists(rhs._start_state):
            raise Exception("RHS Automaton does not have a start state")

        flag = self.is_final(self._start_state)
        flag2 = rhs.is_final(rhs._start_state)
        state_mapping = {}

        if not flag2:
            for state_id in final_states:
                self.set_final(state_id, False)

        for state_id, state in rhs._states.items():
            new_state_id = self.add_state()
            state_mapping[state_id] = new_state_id
            if state.is_final:
                self.set_final(new_state_id, True)

        for state_id, state in rhs._states.items():
            for transition in state.transitions:
                self.add_transition(
                    state_mapping[transition.source],
                    state_mapping[transition.target],
                    Label(transition.input),
                    Label(transition.output)
                )

        rhs_start_state = state_mapping[rhs._start_state]
        for state_id, state in self._states.items():
            for transition in state.transitions:
                if transition.target in final_states:
                    state.add_transition(rhs_start_state, Label(transition.input), Label(transition.output))

        if flag:
            self.add_transition(self._start_state, rhs_start_state, Label(-1), Label(-1))

        self.clean()

    def disjunct(self, alternatives):
        if not alternatives:
            return

        start_state = self._start_state
        new_start_state = self.add_state()
        self.set_initial(new_start_state)
        self.add_transition(new_start_state, start_state, Label(-1), Label(-1))

        for fst in alternatives:
            state_mapping = {}
            start_state2 = fst._start_state

            for state_id, state in fst._states.items():
                new_state_id = self.add_state()
                state_mapping[state_id] = new_state_id
                if state.is_final:
                    self.set_final(new_state_id, True)

                if state_id == start_state2:
                    self.add_transition(new_start_state, new_state_id, Label(-1), Label(-1))

            for state_id, state in fst._states.items():
                for transition in state.transitions:
                    self.add_transition(
                        state_mapping[transition.source],
                        state_mapping[transition.target],
                        Label(transition.input),
                        Label(transition.output)
                    )

        self.merge_simple_final_states()
        self.eliminate_epsilon_transitions()
        self.clean()

    def compute_reachable_states(self):
        if not self.state_exists(self._start_state):
            return []

        return self.compute_state_closure(self._start_state, True, lambda p0: True)

    def is_cyclic(self):
        visited = []
        to_visit = [self._start_state]

        while to_visit:
            current_state = to_visit.pop(0)
            if current_state in visited:
                return True
            visited.append(current_state)

            for transition in self._states[current_state].transitions:
                target = transition.target
                if target in visited:
                    return True
                if target not in to_visit:
                    to_visit.append(target)

        return False

    def merge_simple_final_states(self):
        final_states = self.get_final_states()

        if not final_states or len(final_states) < 2:
            return

        states_to_remove = []
        initial_state_set = False
        merged_state = -1

        for state_id in final_states:
            state = self._states[state_id]
            if not state.transitions:
                if state_id == self._start_state:
                    initial_state_set = True
                if merged_state < 0:
                    merged_state = state_id
                else:
                    states_to_remove.append(state_id)

        if not states_to_remove:
            return

        states_to_remove.sort()

        if initial_state_set:
            self.set_initial(merged_state)

        for state_id, state in self._states.items():
            for transition in state.transitions:
                if transition.target in states_to_remove:
                    transition.target = merged_state

        for state_id in states_to_remove:
            del self._states[state_id]

    def eliminate_epsilon_transitions(self):
        num = 0
        epsilon_state_map = {}

        for state_id, state in self._states.items():
            if self.has_epsilon_transitions(state_id):
                state_closure = self.compute_state_closure(state_id, False, lambda t: t.is_epsilon)
                epsilon_state_map[state_id] = state_closure
                if not state.is_final:
                    state.is_final = any(self.is_final(s) for s in state_closure)

        if epsilon_state_map:
            if self._start_state in epsilon_state_map:
                start_state = self._states[self._start_state]
                for closure_state in epsilon_state_map[self._start_state]:
                    for transition in self._states[closure_state].transitions:
                        if not transition.is_epsilon:
                            start_state.add_transition(transition.target, Label(transition.input),
                                                       Label(transition.output))

            for state_id, state in self._states.items():
                transitions = state.transitions
                for transition in transitions[::-1]:  # Reverse iteration
                    if not transition.is_epsilon and transition.target in epsilon_state_map:
                        for closure_state in epsilon_state_map[transition.target]:
                            state.add_transition(closure_state, Label(transition.input), Label(transition.output))

                # Remove epsilon transitions
                for i in range(len(transitions) - 1, -1, -1):
                    if transitions[i].is_epsilon:
                        transitions.pop(i)
                        num += 1

            self.delete_nonreachable_states()

        return num

    def sort_transitions(self):
        for state_id, state in self._states.items():
            state.sort_transitions()

    def make_deterministic(self):
        if not self.state_exists(self._start_state):
            raise Exception("No start state")
        if self.is_deterministic():
            return

        self.eliminate_epsilon_transitions()
        self.sort_transitions()

        state_list = [self._start_state]
        state_list.extend(kvp[0] for kvp in self._states.items() if kvp[0] != self._start_state)

        i = 0
        trie = Trie()

        while i < len(state_list):
            state_id = state_list[i]
            i += 1
            state = self._states[state_id]

            if len(state.transitions) >= 2:
                flag = False
                j = 0
                transition_count = state.transition_count

                while j < transition_count:
                    num2 = j + 1
                    while num2 < transition_count and state.transitions[num2].input == state.transitions[j].input and \
                            state.transitions[num2].output == state.transitions[j].output:
                        num2 += 1
                    if num2 > j + 1:
                        state_group = [state.transitions[k].target for k in range(j, num2)]
                        state_group.sort()
                        if not trie.contains(state_group, out_value=None):
                            new_state_id = self.add_state()
                            new_state = self._states[new_state_id]
                            state_list.append(new_state_id)
                            trie.add(state_group, new_state_id)
                            new_state.is_final = any(self.is_final(state_id) for state_id in state_group)

                            for state_id in state_group:
                                for transition in self._states[state_id].transitions:
                                    new_state.add_transition(transition.target, Label(transition.input),
                                                             Label(transition.output))

                            new_state.sort_transitions()
                        else:
                            new_state_id = trie.get(state_group)

                        state.add_transition(new_state_id, Label(state.transitions[j].input),
                                             Label(state.transitions[j].output))

                        for k in range(j, num2):
                            state.transitions[k] = None

                        flag = True

                    j = num2

                if flag:
                    state.transitions = [t for t in state.transitions if t is not None]

        self.clean()

    def is_deterministic(self):
        return all(state.is_deterministic() for state in self._states.values())

    def has_epsilon_transitions(self):
        return any(state.has_epsilon_transitions() for state in self._states.values())

    def has_epsilon_transitions(self, state):
        if state not in self._states:
            raise Exception("State doesn't exist")
        state_obj = self._states[state]
        return state_obj.has_epsilon_transitions()

    def compute_productive_states(self):
        final_states = self.get_final_states()
        flag = False
        while True:
            flag = False
            for key, state in self._states.items():
                if key not in final_states:
                    for fst_transition in state.transitions:
                        if fst_transition.target in final_states:
                            final_states.append(key)
                            final_states.sort()  # To maintain order
                            flag = True
                            break
            if not flag:
                break
        return final_states

    def clean(self):
        self.delete_unproductive_states()
        self.delete_nonreachable_states()

    def delete_unproductive_states(self):
        productive_states = self.compute_productive_states()
        if len(productive_states) == len(self._states):
            return
        states_to_remove = []
        for state_id, state in self._states.items():
            if state_id not in productive_states:
                states_to_remove.append(state_id)
        for state_id in states_to_remove:
            self.remove_state(state_id)

    def delete_nonreachable_states(self):
        reachable_states = self.compute_reachable_states()
        if len(reachable_states) == len(self._states):
            return
        states_to_remove = []
        for state_id, state in self._states.items():
            if state_id not in reachable_states:
                states_to_remove.append(state_id)
        for state_id in states_to_remove:
            self.remove_state(state_id)

    def set_start_state(self, s):
        if s == self._start_state:
            return
        state = None
        if self._start_state >= 0:
            state = self.get_state(self._start_state)
            if state is None:
                raise Exception("State doesn't exist")
        state2 = self.get_state(s)
        if state2 is None:
            raise Exception("State doesn't exist")
        if state is not None:
            state.is_initial = False
        state2.is_initial = True
        self._start_state = s

    def get_start_state(self):
        if self.get_state(self._start_state) is None:
            return -1
        return self._start_state

    def is_initial(self, s):
        state = self._states.get(s)
        if state is None:
            raise Exception("State doesn't exist")
        return state.is_initial

    def is_final(self, s):
        state = self._states.get(s)
        if state is None:
            raise Exception("State doesn't exist")
        return state.is_final

    def set_initial(self, s):
        self.set_start_state(s)

    def set_final(self, s, flag):
        state = self._states.get(s)
        if state is None:
            raise Exception("State doesn't exist")
        state.is_final = flag

    def get_final_states(self):
        final_states = [state.id for state in self._states.values() if state.is_final]
        final_states.sort()
        return final_states

    def remove_transitions_into(self, s):
        if not self.state_exists(s):
            raise Exception("State doesn't exist")
        for state in self._states.values():
            for i in range(len(state.transitions) - 1, -1, -1):
                if state.transitions[i].target == s:
                    state.remove_transition_at(i)

    def add_transition(self, start, target, input, output):
        state = self._states.get(start)
        if state is None:
            raise Exception("State doesn't exist")

        state2 = self._states.get(target)
        if state2 is None:
            raise Exception("State doesn't exist")

        if state.has_transition(target, input, output):
            return False

        state.add_transition(target, input, output)
        return True

    def incoming_transition_count(self, s):
        if not self.state_exists(s):
            raise Exception("State doesn't exist")

        return len(self.get_incoming_transitions(s))

    def get_incoming_transitions(self, target_state):
        incoming_transitions = []
        for state in self._states.values():
            for fsttransition in state.transitions:
                if fsttransition.target == target_state:
                    incoming_transitions.append(fsttransition)
        return incoming_transitions

    def is_consistent(self):
        num = 0
        if len(self._states) == 0:
            num += 1
        num2 = 0
        num3 = 0
        for state in self._states.values():
            if state.is_initial:
                num2 += 1
            if state.is_final:
                num3 += 1
            for fsttransition in state.transitions:
                if not self.state_exists(fsttransition.target):
                    num += 1
        if num2 != 1:
            num += 1
        if num3 == 0:
            num += 1
        return num == 0

    def compute_state_closure(self, start_state, include_start_state, prop):
        result = []
        to_process = [start_state]

        while to_process:
            current_state = to_process.pop(0)
            if current_state != self._start_state or include_start_state:
                if current_state not in result:
                    result.append(current_state)

            for fsttransition in self._states[current_state].transitions:
                if prop(fsttransition):
                    target = fsttransition.target
                    if target not in result and target not in to_process:
                        to_process.append(target)

        return result

    @staticmethod
    def read_int32(binary_reader):
        n = int.from_bytes(binary_reader.read(4), 'little') & 0xffffffff
        if n >= 0x80000000:
            n -= 0x100000000
        return n

    def from_binary(self, data):
        self._states = {}
        self._start_state = -1
        self._max_state = -1

        with io.BytesIO(data) as memory_stream:
            with gzip.GzipFile(fileobj=memory_stream, mode='rb') as gzip_stream:
                with gzip_stream:
                    with io.BufferedReader(gzip_stream) as buffered_stream:
                        binary_reader = io.BufferedReader(buffered_stream)

                        num = FST.read_int32(binary_reader)
                        if num != FST.Magic:
                            raise Exception("Inconsistent FST data - version number mismatch")

                        num2 = FST.read_int32(binary_reader)
                        if num2 < 0:
                            raise Exception("Inconsistent FST data - invalid state count")

                        self._start_state = FST.read_int32(binary_reader)
                        self._max_state = FST.read_int32(binary_reader)

                        for _ in range(num2):
                            state_id = FST.read_int32(binary_reader)
                            state = State()
                            state.id = state_id
                            self._states[state.id] = state
                            if state.id == self._start_state:
                                state.is_initial = True

                        num3 = FST.read_int32(binary_reader)
                        if num3 < 0:
                            raise Exception("Inconsistent FST data - invalid number of final states")

                        for _ in range(num3):
                            final_state_id = FST.read_int32(binary_reader)
                            self.set_final(final_state_id, True)

                        num_transitions = FST.read_int32(binary_reader)
                        for _ in range(num_transitions):
                            state_from = FST.read_int32(binary_reader)
                            state_to = FST.read_int32(binary_reader)
                            input_label = FST.read_int32(binary_reader)
                            output_label = FST.read_int32(binary_reader)
                            self.add_transition(state_from, state_to, Label(input_label), Label(output_label))

    def get_binary(self):
        byte_array = bytearray()
        with io.BytesIO() as memory_stream:
            with gzip.GzipFile(fileobj=memory_stream, mode='wb') as gzip_stream:
                with gzip_stream:
                    binary_writer = io.BufferedWriter(gzip_stream)

                    # Writing data to the stream
                    binary_writer.write(FST.Magic.to_bytes(4, byteorder='little'))
                    binary_writer.write(len(self._states).to_bytes(4, byteorder='little'))
                    binary_writer.write(self._start_state.to_bytes(4, byteorder='little'))
                    binary_writer.write(self._max_state.to_bytes(4, byteorder='little'))

                    num = 0
                    for state_key, state in self._states.items():
                        binary_writer.write(state_key.to_bytes(4, byteorder='little'))
                        num += state.transition_count

                    final_states = self.get_final_states()
                    binary_writer.write(len(final_states).to_bytes(4, byteorder='little'))
                    for final_state in final_states:
                        binary_writer.write(final_state.to_bytes(4, byteorder='little'))

                    binary_writer.write(num.to_bytes(4, byteorder='little'))

                    for state_key, state in self._states.items():
                        for transition in state.transitions:
                            binary_writer.write(transition.source.to_bytes(4, byteorder='little'))
                            binary_writer.write(transition.target.to_bytes(4, byteorder='little'))
                            binary_writer.write(transition.input.symbol.to_bytes(4, byteorder='little'))
                            binary_writer.write(transition.output.symbol.to_bytes(4, byteorder='little'))

            byte_array = memory_stream.getvalue()

        return byte_array

    def is_identical(self, other):
        if other is None:
            raise ValueError("Argument cannot be None")

        if (self._max_state != other._max_state or
                self._start_state != other._start_state or
                len(self._states) != len(other._states)):
            return False

        self.sort_transitions()
        other.sort_transitions()

        for state_key, state in self._states.items():
            if state_key not in other._states:
                return False

            other_state = other._states[state_key]

            if (state.is_final != other_state.is_final or
                    state.is_initial != other_state.is_initial or
                    state.transition_count != other_state.transition_count):
                return False

            for i in range(state.transition_count):
                fsttransition = state.transitions[i]
                fsttransition2 = other_state.transitions[i]

                if (fsttransition.source != fsttransition2.source or
                        fsttransition.target != fsttransition2.target or
                        fsttransition.input.symbol != fsttransition2.input.symbol or
                        fsttransition.output.symbol != fsttransition2.output.symbol):
                    return False

        return True
