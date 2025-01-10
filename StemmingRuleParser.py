from StemmingRuleSet import StemmingRule, VersionStemmingRule
from StringUtils import StringUtils


class StemmingRuleParser:
    def __init__(self, ruleset):
        self._rule_set = ruleset

    class RuleSetReader:
        def __init__(self, rule_set):
            self._rule_set = rule_set
            self._rule = ""
            self._rule_p = 0

    def add(self, rule: str):
        self._rule = rule
        self._rule_p = 0
        stemming_rule = StemmingRule()
        num = 0
        length = len(self._rule)

        while num != 99:
            while self._rule_p < length and self._rule[self._rule_p].isspace():
                self._rule_p += 1

            if num == 0:
                text = self.get_identifier().lower()
                num2 = StringUtils.compute_string_hash(text)
                if num2 <= 1527429133:
                    if num2 <= 1181855383:
                        if num2 != 1042520049:
                            if num2 == 1181855383:
                                if text == "version":
                                    num = 15
                                    continue
                        elif text == "tolower":
                            stemming_rule.action = StemmingRule.StemAction.MapToLower
                            num = 1
                            continue
                    elif num2 != 1268415125:
                        if num2 == 1527429133:
                            if text == "testonbaseword":
                                stemming_rule.action = StemmingRule.StemAction.TestOnBaseWord
                                num = 1
                                continue
                        elif text == "deletelastdoublevowels":
                            stemming_rule.action = StemmingRule.StemAction.DeleteLastDoubleVowels
                            num = 1
                            continue
                elif num2 <= 2699807289:
                    if num2 != 2347441966:
                        if num2 == 2699807289:
                            if text == "deletelastdoubleconsonants":
                                stemming_rule.action = StemmingRule.StemAction.DeleteLastDoubleConsonants
                                num = 1
                                continue
                    elif text == "stripdiacritics":
                        num = 1
                        stemming_rule.action = StemmingRule.StemAction.StripDiacritics
                        continue
                elif num2 != 2704835779:
                    if num2 == 3324446467:
                        if text == "set":
                            num = 12
                            continue
                elif text == "replace":
                    num = 6
                    continue
                raise Exception("ErrorMessages.EMSG_SegmentationIllegalKeywordInRule")

            elif num == 1:
                self.expect("priority")
                num = 2

            elif num == 2:
                stemming_rule.priority = self.get_number()
                num = 3

            elif num == 3:
                self.expect("and")
                num = 4

            elif num == 4:
                num = 10
                text2 = self.get_identifier().lower()
                if text2 == "continue":
                    stemming_rule.continuation_on_success = StemmingRule.StemContinuation.Continue
                elif text2 == "restart":
                    stemming_rule.continuation_on_success = StemmingRule.StemContinuation.Restart
                elif text2 == "stop":
                    stemming_rule.continuation_on_success = StemmingRule.StemContinuation.Stop
                else:
                    raise Exception("ErrorMessages.EMSG_SegmentationIllegalContinuation")

                stemming_rule.continuation_on_fail = StemmingRule.StemContinuation.Continue
                stemming_rule.continuation_priority = 0

            elif num == 5:
                if self._rule[self._rule_p] != ';':
                    raise Exception("ErrorMessages.EMSG_SegmentationTrailingJunk")
                num = 99

            elif num == 6:
                text3 = self.get_identifier().lower()
                num2 = StringUtils.compute_string_hash(text3)
                if num2 <= 2121723151:
                    if num2 != 827898097:
                        if num2 != 1079560007:
                            if num2 != 2121723151:
                                continue
                            if text3 == "circumfix":
                                stemming_rule.action = StemmingRule.StemAction.Circumfix
                        elif text3 == "form":
                            stemming_rule.action = StemmingRule.StemAction.Form
                    elif text3 == "infix":
                        stemming_rule.action = StemmingRule.StemAction.Infix
                elif num2 <= 3617714895:
                    if num2 != 2953616746:
                        if num2 != 3617714895:
                            continue
                        if text3 == "properinfix":
                            stemming_rule.action = StemmingRule.StemAction.ProperInfix
                    elif text3 == "prefixedinfix":
                        stemming_rule.action = StemmingRule.StemAction.PrefixedInfix
                elif num2 != 3901637708:
                    if num2 != 4232466889:
                        continue
                    if text3 == "prefix":
                        stemming_rule.action = StemmingRule.StemAction.Prefix
                elif text3 == "suffix":
                    stemming_rule.action = StemmingRule.StemAction.Suffix

                num = 7

            elif num == 7:
                stemming_rule.affix = self.get_quoted_string()
                num = 8

            elif num == 8:
                self.expect("with")
                num = 9

            elif num == 9:
                stemming_rule.replacement = self.get_quoted_string()
                num = 1

            elif num == 10:
                if self._rule[self._rule_p] == ';':
                    num = 5
                else:
                    self.expect("at")
                    num = 11

            elif num == 11:
                stemming_rule.continuation_priority = self.get_number()
                num = 5

            elif num == 12:
                text4 = self.get_identifier().lower()
                if text4 == "minwordlength":
                    self._rule_set.minimum_word_length = self.get_number()
                elif text4 == "minstemlength":
                    self._rule_set.minimum_stem_length = self.get_number()
                elif text4 == "minstempercentage":
                    self._rule_set.minimum_stem_percentage = self.get_number()
                elif text4 == "maxruleapplications":
                    self._rule_set.maximum_rule_applications = self.get_number()
                else:
                    raise Exception("ErrorMessages.EMSG_SegmentationInvalidVariableName")
                num = 5

            elif num == 15:
                stemming_rule = VersionStemmingRule(self.get_number())
                num = 5

        if stemming_rule.action != StemmingRule.StemAction.Non:
            self._rule_set.add(stemming_rule)

    def expect(self, expectation):
        if expectation is None:
            raise ValueError("expectation cannot be None")
        identifier = self.get_identifier()
        if identifier.lower() != expectation.lower():
            raise Exception("ErrorMessages.EMSG_SegmentationInvalidRule")

    def get_identifier(self):
        result = []
        while self._rule_p < len(self._rule) and self._rule[self._rule_p].isalpha():
            result.append(self._rule[self._rule_p])
            self._rule_p += 1
        return ''.join(result)

    def get_number(self):
        while self._rule_p < len(self._rule) and self._rule[self._rule_p].isspace():
            self._rule_p += 1
        result = []
        while self._rule_p < len(self._rule) and self._rule[self._rule_p].isdigit():
            result.append(self._rule[self._rule_p])
            self._rule_p += 1
        if not result:
            raise Exception("ErrorMessages.EMSG_SegmentationInvalidRule")
        return int(''.join(result))

    def get_quoted_string(self):
        result = []
        if self._rule[self._rule_p] != '"':
            raise Exception("ErrorMessages.EMSG_SegmentationInvalidRule")
        self._rule_p += 1
        while self._rule_p < len(self._rule) and self._rule[self._rule_p] != '"':
            result.append(self._rule[self._rule_p])
            self._rule_p += 1
        if self._rule_p >= len(self._rule) or self._rule[self._rule_p] != '"':
            raise Exception("ErrorMessages.EMSG_SegmentationInvalidRule")
        self._rule_p += 1
        return ''.join(result)
