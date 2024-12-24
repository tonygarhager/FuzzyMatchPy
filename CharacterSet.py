import unicodedata


class CharacterSet:
    class Range:
        def __init__(self, lower, upper):
            self.lower = lower
            self.upper = upper

    def __init__(self):
        self.negated = False
        self._individual_members = set()
        self._categories = set()
        self._ranges = []

    def contains(self, c):
        if c in self._individual_members:
            return not self.negated
        for r in self._ranges:
            if r.lower <= c <= r.upper:
                return not self.negated
        cat = unicodedata.category(c)
        if any(cat.startswith(unicode_category) for unicode_category in self._categories):
            return not self.negated
        return self.negated

    def add(self, c_or_lower, upper=None):
        if upper is None:
            if c_or_lower not in self._individual_members:
                self._individual_members.add(c_or_lower)
        else:
            if c_or_lower > upper:
                c_or_lower, upper = upper, c_or_lower
            self._ranges.append(self.Range(c_or_lower, upper))

    def add_category(self, category):
        if category not in self._categories:
            self._categories.add(category)

    def add_character_set(self, other):
        if other is None:
            raise ValueError("The 'other' CharacterSet cannot be None.")
        self._individual_members.update(other._individual_members)
        self._ranges.extend(other._ranges)
        self._categories.update(other._categories)

    def signature(self):
        parts = []
        if self.negated:
            parts.append("^")
        if self._individual_members:
            parts.append("".join(sorted(self._individual_members)))
        for r in self._ranges:
            parts.append(f"{r.lower}-{r.upper}")
        for cat in sorted(self._categories):
            parts.append(f"\\p{{{cat}}}")
        return f"[{''.join(parts)}]"

    def __str__(self):
        return self.signature()
