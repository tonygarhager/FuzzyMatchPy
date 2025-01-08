from enum import Enum
from typing import Optional
from dataclasses import dataclass
from BuiltinRecognizers import BuiltinRecognizers
from EditDistance import EditDistance, EditOperation, EditDistanceItem
from SegmentElement import SegmentElement
from SimpleToken import SimpleToken
from StringUtils import StringUtils
from Tag import TagType
from TagToken import TagToken
from Token import Token, TokenType

@dataclass
class MatrixItem:
    score: float
    operation: EditOperation
    similarity: float

    def __init__(self, score: float, operation: EditOperation, similarity: float):
        self.score = score
        self.operation = operation
        self.similarity = similarity

class EditDistanceComputer:
    def __init__(self, similarity_computer, insert_delete_costs=1.0, move_costs=0.0, apply_small_change_adjustment=True):
        if insert_delete_costs < 0.0:
            raise ValueError("insert_delete_costs must be non-negative")
        if move_costs < 0.0:
            raise ValueError("move_costs must be non-negative")

        self.similarity_computer = similarity_computer
        self.insert_delete_costs = insert_delete_costs
        self.move_costs = move_costs
        self.similarity_threshold = 0.85
        self.compute_move_operations = move_costs > 0.0
        self.apply_small_change_adjustment = apply_small_change_adjustment

    def compute_edit_distance(self, source_objects, target_objects, precomputed_associations=None):
        if source_objects is None:
            raise ValueError("source_objects cannot be None")
        if target_objects is None:
            raise ValueError("target_objects cannot be None")

        if precomputed_associations and not self.sort_and_validate(precomputed_associations, len(source_objects), len(target_objects)):
            precomputed_associations = None

        edit_distance = EditDistance(len(source_objects), len(target_objects), 0.0)
        array = [[None for _ in range(len(target_objects) + 1)] for _ in range(len(source_objects) + 1)]

        array[0][0] = {'score': 0.0, 'operation': EditOperation.Identity, 'similarity': 0.0}

        for i in range(1, len(source_objects) + 1):
            array[i][0] = {'score': i * self.insert_delete_costs, 'operation': EditOperation.Delete, 'similarity': 0.0}

        for j in range(1, len(target_objects) + 1):
            array[0][j] = {'score': j * self.insert_delete_costs, 'operation': EditOperation.Insert, 'similarity': 0.0}

        for i in range(1, len(source_objects) + 1):
            for j in range(1, len(target_objects) + 1):
                array[i][j] = {'score': 0.0, 'operation': EditOperation.Identity, 'similarity': 0.0}

        for i in range(1, len(source_objects) + 1):
            for j in range(1, len(target_objects) + 1):
                similarity = self.similarity_computer(source_objects[i - 1], target_objects[j - 1])
                change_cost = 1.0 - similarity if similarity >= 0 else float('inf')
                delete_cost = array[i - 1][j]['score'] + self.insert_delete_costs
                insert_cost = array[i][j - 1]['score'] + self.insert_delete_costs
                change_cost = array[i - 1][j - 1]['score'] + change_cost

                min_cost = min(delete_cost, insert_cost, change_cost)
                operation = (
                    EditOperation.Delete if min_cost == delete_cost else
                    EditOperation.Insert if min_cost == insert_cost else
                    EditOperation.Change if similarity < 1.0 else
                    EditOperation.Identity
                )

                array[i][j] = {'score': min_cost, 'operation': operation, 'similarity': similarity}

        i, j = len(source_objects), len(target_objects)
        edit_distance.distance = array[i][j]['score']

        while i > 0 or j > 0:
            item = EditDistanceItem()
            operation = array[i][j]['operation']
            item.operation = operation

            if operation == EditOperation.Identity:
                i, j = i - 1, j - 1
                item.costs = 0.0
            elif operation == EditOperation.Change:
                i, j = i - 1, j - 1
                item.costs = 1.0 - array[i + 1][j + 1]['similarity']
            elif operation == EditOperation.Insert:
                j -= 1
                item.costs = self.insert_delete_costs
            elif operation == EditOperation.Delete:
                i -= 1
                item.costs = self.insert_delete_costs

            item.source = i
            item.target = j
            edit_distance.add_at_start(item)

        return edit_distance

    @staticmethod
    def sort_and_validate(precomputed_associations, source_count, target_count):
        for pair in precomputed_associations:
            if not (0 <= pair[0] < source_count and 0 <= pair[1] < target_count):
                return False
        precomputed_associations.sort(key=lambda x: (x[0], x[1]))
        return True

class SimilarityComputers:

    @staticmethod
    def get_char_similarity_ex(a: str, b: str, use_to_base: bool) -> float:
        if a == b:
            return 1.0
        c, c2 = a.lower(), b.lower()
        if c == c2:
            return 0.95
        if not use_to_base:
            return 0.0
        c3, c4 = StringUtils.to_base(c), StringUtils.to_base(c2)
        return 0.9 if c3 == c4 else 0.0

    @staticmethod
    def get_char_similarity(a: str, b: str) -> float:
        return SimilarityComputers.get_char_similarity_ex(a, b, True)

    @staticmethod
    def get_char_similarity_without_to_base(a: str, b: str) -> float:
        return SimilarityComputers.get_char_similarity_ex(a, b, False)

    @staticmethod
    def get_string_similarity(a: str, b: str, similarity_computer = None, apply_small_change_adjustment: bool = True) -> float:
        if similarity_computer is None:
            similarity_computer = SimilarityComputers.get_char_similarity

        if a == b:
            return 1.0
        if a.lower() == b.lower():
            return 0.95

        edit_distance_computer = EditDistanceComputer(similarity_computer, apply_small_change_adjustment)
        edit_distance = edit_distance_computer.compute_edit_distance(list(a), list(b))
        return edit_distance.score

    @staticmethod
    def get_placeable_similarity(a: Token, b: Token, disabled_auto_substitutions: int) -> float:
        if not a.is_placeable or not b.is_placeable:
            return 0.0

        if a.type != b.type or type(a) != type(b):
            return 0.0

        if isinstance(a, Token) and isinstance(b, Token):
            if a.type != b.type:
                return -1.0

        if disabled_auto_substitutions != BuiltinRecognizers.RecognizeNone:
            flag = False
            if a.type == TokenType.Abbreviation:
                flag = disabled_auto_substitutions & BuiltinRecognizers.RecognizeAcronyms
            elif a.type == TokenType.Date:
                flag = disabled_auto_substitutions & BuiltinRecognizers.RecognizeDates

            if flag:
                return 1.0 if a == b else 0.7

        similarity = a.get_similarity(b)
        return {SegmentElement.Similarity.Non: 0.7,
                SegmentElement.Similarity.IdenticalType: 0.85,
                SegmentElement.Similarity.IdenticalValueAndType: 1.0}.get(similarity, 0.0)

    @staticmethod
    def get_placeable_similarity_async(a, b, disabled_auto_substitutions):
        if not a.is_placeable or not b.is_placeable:
            return 0.0
        elif a.type != b.type or type(a) != type(b):
            return 0.0
        else:
            tag_token_a = isinstance(a, TagToken)
            tag_token_b = isinstance(b, TagToken)

            if tag_token_a or tag_token_b:
                if not (tag_token_a and tag_token_b):
                    return -1.0
                if a.tag.type != b.tag.type:
                    return -1.0

            if disabled_auto_substitutions != BuiltinRecognizers.RecognizeNone:
                flag = False
                if a.type == TokenType.Abbreviation:
                    flag = (
                                       disabled_auto_substitutions & BuiltinRecognizers.RecognizeAcronyms) > BuiltinRecognizers.RecognizeNone
                elif a.type == TokenType.Date:
                    flag = (
                                       disabled_auto_substitutions & BuiltinRecognizers.RecognizeDates) > BuiltinRecognizers.RecognizeNone
                elif a.type == TokenType.Time:
                    flag = (
                                       disabled_auto_substitutions & BuiltinRecognizers.RecognizeTimes) > BuiltinRecognizers.RecognizeNone
                elif a.type == TokenType.Variable:
                    flag = (
                                       disabled_auto_substitutions & BuiltinRecognizers.RecognizeVariables) > BuiltinRecognizers.RecognizeNone
                elif a.type == TokenType.Number:
                    flag = (
                                       disabled_auto_substitutions & BuiltinRecognizers.RecognizeNumbers) > BuiltinRecognizers.RecognizeNone
                elif a.type == TokenType.Measurement:
                    flag = (
                                       disabled_auto_substitutions & BuiltinRecognizers.RecognizeMeasurements) > BuiltinRecognizers.RecognizeNone

                if flag:
                    return 1.0 if a == b else 0.7

            similarity_result = a.get_similarity(b)

            if similarity_result == SegmentElement.Similarity.Non:
                return 0.7
            elif similarity_result == SegmentElement.Similarity.IdenticalType:
                return 0.85
            elif similarity_result == SegmentElement.Similarity.IdenticalValueAndType:
                return 1.0
            else:
                return 0.0

    @staticmethod
    def get_token_similarity(
            a, b, use_string_edit_distance, disabled_auto_substitutions,
            characters_normalize_safely=True, apply_small_change_adjustment=True
    ):
        num = 0.0
        flag = isinstance(a, TagToken)
        flag2 = isinstance(b, TagToken)

        if flag != flag2 or a.is_whitespace != b.is_whitespace or a.is_punctuation != b.is_punctuation:
            num = -1.0
        elif flag and flag2:
            if a.tag.type == b.tag.type:
                num = 0.95
            elif ((a.tag.type == TagType.Standalone and b.tag.type == TagType.TextPlaceholder) or
                  (a.tag.type == TagType.TextPlaceholder and b.tag.type == TagType.Standalone)):
                num = 0.85
            else:
                num = -1.0
        else:
            num2 = 0.0
            if a.is_placeable and b.is_placeable:
                num = SimilarityComputers.get_placeable_similarity(a, b, disabled_auto_substitutions)
            elif a.text is None or b.text is None:
                num = 0.0
            else:
                if a.is_word != b.is_word:
                    num2 = 0.1

                if a.text == b.text:
                    num4 = 1.0
                elif a.is_whitespace or a.is_punctuation:
                    num4 = 0.94
                elif SimilarityComputers.string_equals_ordinal_ignore_case_and_diacritics(
                        a.text, b.text, characters_normalize_safely
                ):
                    num4 = 0.95
                else:
                    simple_token_a = isinstance(a, SimpleToken)
                    simple_token_b = isinstance(b, SimpleToken)
                    if simple_token_a and simple_token_b:
                        if (a.stem is not None and b.stem is not None and
                                SimilarityComputers.string_equals_ordinal_ignore_case_and_diacritics(
                                    a.stem, b.stem, True
                                )):
                            num4 = 0.95
                        else:
                            num4 = 0.0
                            similarity_computer = None
                            if not use_string_edit_distance:
                                return max(0.0, num4 - num2)

                            text = a.text
                            text2 = b.text
                            if not characters_normalize_safely:
                                similarity_computer = SimilarityComputers.get_char_similarity_without_to_base
                            num4 = SimilarityComputers.get_threshold(
                                SimilarityComputers.get_string_similarity(
                                    text, text2, similarity_computer, apply_small_change_adjustment
                                )
                            )
                    else:
                        num4 = (
                            0.95 * SimilarityComputers.get_threshold(
                                SimilarityComputers.get_string_similarity(
                                    a.text, b.text, None, True
                                )
                            ) if use_string_edit_distance else 0.0
                        )
                num = max(0.0, num4 - num2)

        return num

    @staticmethod
    def get_threshold(sim: float) -> float:
        if sim == 1.0:
            return 1.0
        elif sim >= 0.9:
            return 0.9
        elif sim >= 0.75:
            return 0.75
        elif sim < 0.5:
            return 0.0
        return 0.5

    @staticmethod
    def string_equals_ordinal_ignore_case_and_diacritics(a: str, b: str, characters_normalize_safely: bool = True) -> bool:
        if not a or not b:
            return a == b

        if len(a) != len(b):
            return False

        for c1, c2 in zip(a, b):
            if c1 != c2:
                if characters_normalize_safely:
                    c1, c2 = StringUtils.to_base(c1), StringUtils.to_base(c2)
                if c1.lower() != c2.lower():
                    return False

        return True
