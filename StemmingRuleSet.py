from enum import Enum
from typing import List, Optional
from functools import cmp_to_key
from abc import ABC, abstractmethod

from StringUtils import StringUtils


class IStemmer(ABC):
    @abstractmethod
    def stem_string(self, word:str) -> str:
        pass
    @abstractmethod
    def get_signature(self) -> str:
        pass

class StemmingRule:
    class StemAction(Enum):
        Non = 0
        Prefix = 1
        Suffix = 2
        Infix = 3
        ProperInfix = 4
        Circumfix = 5
        Form = 6
        MapToLower = 7
        StripDiacritics = 8
        DeleteLastDoubleConsonants = 9
        DeleteLastDoubleVowels = 10
        TestOnBaseWord = 11
        PrefixedInfix = 12
        Version = 13

    class StemContinuation(Enum):
        Continue = 0
        Restart = 1
        Stop = 2

    def __init__(self):
        self.continuation_on_success = None
        self.continuation_on_fail = None
        self.action = StemmingRule.StemAction.Non
        self.length = 0
        self.affix = ""
        self.replacement = ""
        self.priority = 0
        self.continuation_priority = 0

    @staticmethod
    def compare(a: "StemmingRule", b: "StemmingRule") -> int:
        """
        Compares two StemmingRule objects based on priority and length.
        """
        diff = b.priority - a.priority
        if diff == 0:
            diff = b.length - a.length
        return diff

    def __str__(self) -> str:
        """
        Returns a string representation of the StemmingRule.
        """
        return (
            f"stemAction={self.action};"
            f"Affix={self.affix};"
            f"replacement={self.replacement};"
            f"priority={self.priority}"
        )

class VersionStemmingRule(StemmingRule):
    """
    A specialized stemming rule that represents a version-specific rule.
    """

    def __init__(self, version: int):
        """
        Initializes a VersionStemmingRule instance.

        Args:
            version (int): The version associated with this rule.
        """
        super().__init__()
        self.action = StemmingRule.StemAction.Version
        self._version = version

    @property
    def version(self) -> int:
        """
        Gets the version associated with this rule.
        """
        return self._version

class StemmingRuleSet:
    DEFAULT_MINIMUM_WORD_LENGTH = 3
    DEFAULT_MINIMUM_STEM_LENGTH = 2
    DEFAULT_MINIMUM_STEM_PERCENTAGE = 30
    DEFAULT_MAXIMUM_RULE_APPLICATIONS = 100

    def __init__(self, culture: str):
        """
        Initializes a StemmingRuleSet instance.

        Args:
            culture (str): The culture code for the stemming rule set.
        """
        self._rules: List[StemmingRule] = []
        self.culture: str = culture
        self.version: int = 0
        self.minimum_stem_length: int = self.DEFAULT_MINIMUM_STEM_LENGTH
        self.maximum_rule_applications: int = self.DEFAULT_MAXIMUM_RULE_APPLICATIONS
        self.minimum_stem_percentage: int = self.DEFAULT_MINIMUM_STEM_PERCENTAGE
        self.minimum_word_length: int = self.DEFAULT_MINIMUM_WORD_LENGTH

    def __getitem__(self, index: int) -> StemmingRule:
        """
        Gets a stemming rule by index.
        """
        return self._rules[index]

    def __len__(self) -> int:
        """
        Returns the number of stemming rules in the set.
        """
        return len(self._rules)

    def add(self, rule: StemmingRule):
        """
        Adds a new stemming rule to the set and sorts the rules.

        Args:
            rule (StemmingRule): The rule to add.
        """
        if isinstance(rule, VersionStemmingRule):
            self.version = rule.version
        else:
            self._rules.append(rule)
            self._sort()

    def _sort(self):
        """
        Sorts the rules based on their priority and length.
        """
        self._rules.sort(key=cmp_to_key(StemmingRule.compare))

class StemmingRuleSetIterator:
    def __init__(self, set):
        if set is None:
            raise ValueError("set cannot be None")
        self._set = set
        self._position = -1

    @property
    def current(self):
        if self._position < 0 or self._position >= len(self._set):
            return None
        return self._set[self._position]

    def first(self, priority):
        self._position = -1
        self.next(priority)

    def next(self, priority):
        if self._position >= len(self._set):
            self._position = -1
            return
        self._position += 1
        if priority <= 0:
            return
        while self._position < len(self._set) and self._set[self._position].priority < priority:
            self._position += 1


class RuleBasedStemmer(IStemmer):
    def __init__(self, rules, resources, skip_surrogates=False, signatures:str=None):
        self._resources = resources
        self._rules = rules
        if signatures is None:
            self.signature = "RuleBased" + ("0" if self._rules is None else str(self._rules.version))
        else:
            self.signature = signatures
        self._skip_surrogates = skip_surrogates

    @staticmethod
    def create(resources, skip_surrogates=False):
        stemming_rule_set = resources.stemming_rules
        return RuleBasedStemmer(stemming_rule_set, resources, skip_surrogates, "RuleBased" + ("0" if stemming_rule_set is None else str(stemming_rule_set.version)))

    def get_signature(self) -> str:
        return self.signature

    def stem_string(self, word):
        return self.stem_internal(word)

    def stem_internal(self, word):
        if self._rules is None or len(self._rules) == 0:
            return self.brute_force_stem(word)
        else:
            apply_rules = True
            special_rules_only = len(word) < self._rules.minimum_word_length
            applied_rules = 0
            rule_sink = iter(self._rules)
            shortest_stem_length = max(self._rules.minimum_stem_length,
                                       len(word) * self._rules.minimum_stem_percentage // 100)
            while apply_rules:
                rule = next(rule_sink, None)
                if applied_rules > self._rules.maximum_rule_applications or rule is None:
                    apply_rules = False
                else:
                    applied, word = self.apply_rule(word, shortest_stem_length, special_rules_only, rule)
                    if applied:
                        applied_rules += 1
                        stem_continuation = rule.continuation_on_success
                    else:
                        stem_continuation = rule.continuation_on_fail

                    if stem_continuation == "continue":
                        continue
                    elif stem_continuation == "restart":
                        rule_sink = iter(self._rules)
                    else:
                        apply_rules = False
            return word

    def apply_rule(self, form, shortest_stem_length, special_rules_only, rule):
        num = 0 if not rule.affix else len(rule.affix)
        length = len(form)
        num2 = 0 if not rule.replacement else len(rule.replacement)
        action = rule.action
        flag = False

        if action != StemmingRule.StemAction.MapToLower:
            if action != StemmingRule.StemAction.StripDiacritics:
                if special_rules_only:
                    flag = False
                else:
                    if action == StemmingRule.StemAction.DeleteLastDoubleConsonants:
                        if length > 2:
                            for i in range(length - 1, 0, -1):
                                if form[i] == form[i - 1] and not StringUtils.is_vowel(form[i]):
                                    form = form[:i] + form[i + 1:]
                                    break
                        flag = True
                    elif action == StemmingRule.StemAction.DeleteLastDoubleVowels:
                        if length > 2:
                            for j in range(length - 1, 0, -1):
                                if form[j] == form[j - 1] and StringUtils.is_vowel(form[j]):
                                    form = form[:j] + form[j + 1:]
                                    break
                        flag = True
                    elif action == StemmingRule.StemAction.TestOnBaseWord:
                        flag2 = self._resources.is_stopword(form)
                        flag = flag2
                    else:
                        flag = length >= num and length - num + num2 >= shortest_stem_length and RuleBasedStemmer.replace_affix(
                            form, rule.action, rule.affix, rule.replacement)
            else:
                form = StringUtils.to_base(form)
                form = RuleBasedStemmer.strip_peripheral_punctuation(form)
                flag = True
        else:
            form = form.lower()
            flag = True

        return flag, form

    def brute_force_stem(self, word):
        word = word.lower()
        word = self.strip_peripheral_punctuation(word)
        if self._rules:
            if self._resources.is_stopword(word):
                return word
        for i in range(len(word) - 1, 2, -1):
            if word[i] == word[i - 1] and not self.is_vowel(word[i]):
                word = word[:i] + word[i + 1:]
                break
        num = min(len(word) // 3, 3)
        if len(word) >= 3 and (len(word) - num) % 2 != 0:
            num += 1
        if len(word) >= 3 and len(word) - num < 3:
            num = len(word) - 3
        word = word[:-num]
        return word

    def strip_peripheral_punctuation(self, form):
        if not form:
            return form
        num = 0
        length = len(form)
        while num < length and form[num] in ",.?!":
            num += 1
        if num == length:
            return form
        num2 = length - 1
        while num2 > num and form[num2] in ",.?!":
            num2 -= 1
        return form[num:num2 + 1]

    def is_vowel(self, char):
        return char in "aeiou"

    @property
    def strips_diacritics(self):
        if self._rules is None:
            return False
        for rule in self._rules:
            if rule.action == "strip_diacritics":
                return True
        return False



class CachingStemmer:
    def __init__(self, wrapped):
        if wrapped is None:
            raise ValueError("wrapped cannot be None")
        self._wrapped_stemmer = wrapped
        self._cache = {}

    def stem(self, word):
        # Check if word is in the cache
        if word in self._cache:
            return self._cache[word]

        # If not cached, call the wrapped stemmer's stem method
        result = self._wrapped_stemmer.stem(word)

        # Store the result in the cache
        self._cache[word] = result
        return result

    @property
    def signature(self):
        return self._wrapped_stemmer.signature

