from SeparatorCombination import SeparatorCombination


class NumberFormatData:
    def __init__(self):
        self.digits = []  # List of digits
        self.separator_combinations = []  # List of SeparatorCombination objects
        self.positive_signs = ""
        self.negative_signs = ""
        self.number_group_sizes = []
        self.number_negative_pattern = 0

    def add_separator_combination(self, group_separator, decimal_separator, augment_group_separators):
        separator_combination = SeparatorCombination(group_separator, decimal_separator, augment_group_separators)
        if separator_combination in self.separator_combinations:
            return False
        self.separator_combinations.append(separator_combination)
        return True

    def get_combined_decimal_separators(self):
        hash_set = set()
        string_builder = []
        for separator_combination in self.separator_combinations:
            if separator_combination.decimal_separators:
                for c in separator_combination.decimal_separators:
                    if c not in hash_set:
                        string_builder.append(c)
                        hash_set.add(c)
        return ''.join(string_builder)