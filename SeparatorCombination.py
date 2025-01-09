
class SeparatorCombination:
    def __init__(self, group_separators=None, decimal_separators=None, augment_group_separators=False):
        self.group_separators = group_separators
        self.decimal_separators = decimal_separators
        if group_separators and augment_group_separators:
            self.init(group_separators, decimal_separators, augment_group_separators)

    def init(self, group_separators, decimal_separators, augment_group_separators):
        self.group_separators = group_separators
        self.decimal_separators = decimal_separators
        if not group_separators or not augment_group_separators:
            return
        # Augment the group separator with non-breaking space if necessary
        if ' ' in group_separators and '\u00a0' not in group_separators:
            self.group_separators += '\u00a0'
        if '\u00a0' in group_separators and ' ' not in group_separators:
            self.group_separators += ' '

    def is_swappable(self):
        if not self.group_separators or not self.decimal_separators:
            return False
        if len(self.group_separators) != 1 or len(self.decimal_separators) != 1:
            return False
        group_sep = self.group_separators[0]
        decimal_sep = self.decimal_separators[0]
        return (group_sep in {'.', ','}) and (decimal_sep in {'.', ','}) and group_sep != decimal_sep

    def __eq__(self, other):
        if not isinstance(other, SeparatorCombination):
            return False
        return self.group_separators == other.group_separators and self.decimal_separators == other.decimal_separators

    def __hash__(self):
        group_hash = hash(self.group_separators) & 0xFFFF
        decimal_hash = hash(self.decimal_separators) & 0xFFFF
        return group_hash + (decimal_hash << 16)

    def clone(self):
        return SeparatorCombination(self.group_separators, self.decimal_separators, augment_group_separators=False)

    def __repr__(self):
        return f"SeparatorCombination(group_separators='{self.group_separators}', decimal_separators='{self.decimal_separators}')"

