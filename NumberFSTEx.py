from SeparatorCombination import SeparatorCombination


class NumberFSTEx:
    CurrentVersion = 1

    def __init__(self):
        self.separator_combinations = []
        self.version = NumberFSTEx.CurrentVersion

    @classmethod
    def from_binary(cls, data):
        string_data = data.decode('utf-8')
        separator_combinations = []
        lines = string_data.split('\r')

        if not lines:
            return cls()

        version = int(lines[0])
        if version > 1:
            raise Exception(f"Unexpected NumberFSTEx version: {version}")

        lines = lines[1:]  # Remove version line
        for line in lines:
            parts = line.split('\t')
            if len(parts) == 2:
                separator_combinations.append(SeparatorCombination(parts[0], parts[1]))

        instance = cls()
        instance.separator_combinations = separator_combinations
        instance.version = version
        return instance

    def to_binary(self):
        result = []
        if not self.separator_combinations:
            return b""

        result.append(str(self.version))
        for combo in self.separator_combinations:
            result.append(f"\r{combo.group_separators}\t{combo.decimal_separators}")

        return ''.join(result).encode('utf-8')

    @property
    def separator_combinations(self):
        return self._separator_combinations

    @separator_combinations.setter
    def separator_combinations(self, value):
        self._separator_combinations = value