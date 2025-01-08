import numpy as np

from BuiltinRecognizers import BuiltinRecognizers
from EditDistance import EditDistance, EditOperation, EditDistanceItem, EditDistanceResolution
from SimilarityComputers import MatrixItem, SimilarityComputers
from SimilarityMatrix import SimilarityMatrix


class SegmentEditDistanceComputer:
    def __init__(self, compute_moves:bool = True):
        self._compute_moves = compute_moves

    @staticmethod
    def can_compute_edit_distance(source_token_count:int, target_token_count:int) -> bool:
        return source_token_count * target_token_count <= 4194304

    @staticmethod
    def create_edit_distance_matrix(source_tokens, target_tokens):
        source_count = len(source_tokens)
        target_count = len(target_tokens)

        # Create a 2D NumPy array of MatrixItem
        array = np.empty((source_count + 1, target_count + 1), dtype=object)

        # Initialize the matrix
        array[0, 0] = MatrixItem(0.0, EditOperation.Identity, 0.0)
        for i in range(1, source_count + 1):
            array[i, 0] = MatrixItem(i * 1.0, EditOperation.Delete, 0.0)
        for j in range(1, target_count + 1):
            array[0, j] = MatrixItem(j * 1.0, EditOperation.Insert, 0.0)
        for i in range(1, source_count + 1):
            for j in range(1, target_count + 1):
                array[i, j] = MatrixItem(0.0, EditOperation.Undefined, 0.0)

        return array

    @staticmethod
    def get_operation(chage_costs:float, insert_costs:float, delete_costs:float, similarity:float) -> EditOperation:
        num = min(chage_costs, insert_costs, delete_costs)
        if num == chage_costs:
            if similarity == 1.0:
                return EditOperation.Identity
            return EditOperation.Change
        elif num == delete_costs:
            return EditOperation.Delete
        return EditOperation.Insert



    def compute_edit_distance(self, source_tokens, target_tokens, compute_diagonal_only:bool,
                              disabled_auto_substitutions:BuiltinRecognizers,
                              characters_normalize_safely:bool,
                              apply_small_change_adjustment:bool,
                              diagonal_only:bool):
        self._characters_normalize_safely = characters_normalize_safely
        self._apply_small_change_adjustment = apply_small_change_adjustment
        return self.compute_edit_distance_impl_original(source_tokens, target_tokens, disabled_auto_substitutions, diagonal_only)

    def compute_cell(self, matrix, sim:SimilarityMatrix, i:int, j:int):
        if matrix[i, j].operation != EditOperation.Undefined:
            return
        self.compute_cell(matrix, sim, i - 1, j - 1)
        similarity = sim.get_element_at(i - 1, j - 1)
        change_costs = 100000.0 if similarity < 0.0 else (matrix[i - 1, j - 1].score + (1.0 - similarity))
        insert_costs = 0.0
        delete_costs = 0.0

        if i < j:
            self.compute_cell(matrix, sim, i, j - 1)
            insert_costs = matrix[i, j - 1].score + 1.0
            if insert_costs >= change_costs or change_costs == 100000.0:
                self.compute_cell(matrix, sim, i - 1, j)
                delete_costs = matrix[i - 1, j].score + 1.0
                edit_operation = SegmentEditDistanceComputer.get_operation(change_costs, insert_costs, delete_costs, similarity)
            else:
                edit_operation = EditOperation.Insert if insert_costs < change_costs else EditOperation.Change
        else:
            self.compute_cell(matrix, sim, i - 1, j)
            delete_costs = matrix[i - 1, j].score + 1.0
            if delete_costs >= change_costs or change_costs == 100000.0:
                self.compute_cell(matrix, sim, i, j - 1)
                insert_costs = matrix[i, j - 1].score + 1.0
                edit_operation = SegmentEditDistanceComputer.get_operation(change_costs, insert_costs, delete_costs, similarity)
            else:
                edit_operation = EditOperation.Delete if delete_costs < change_costs else EditOperation.Change

        matrix[i, j].similarity = similarity
        matrix[i, j].operation = edit_operation

        if edit_operation == EditOperation.Insert:
            matrix[i, j].score = insert_costs
        elif edit_operation == EditOperation.Delete:
            matrix[i, j].score = delete_costs
        else:
            matrix[i, j].score = change_costs

    def compute_edit_distance_matrix_lazy(self, matrix, sim:SimilarityMatrix):
        self.compute_cell(matrix, sim, len(sim.source_tokens), len(sim.target_tokens))

    def compute_edit_distance_impl_original(self, source_tokens, target_tokens, disabled_auto_substitutions:BuiltinRecognizers, diagonal_only:bool):
        if diagonal_only and len(target_tokens) != len(source_tokens):
            raise Exception("diagonal_only and target_tokens must have same length")
        aligned_tags = None
        result = EditDistance(len(source_tokens), len(target_tokens), 0.0)
        sim = SimilarityMatrix(source_tokens, target_tokens, False, disabled_auto_substitutions, self._characters_normalize_safely, self._apply_small_change_adjustment)
        matrix = SegmentEditDistanceComputer.create_edit_distance_matrix(source_tokens, target_tokens)

        if diagonal_only:
            for k in range(len(source_tokens) + 1):
                matrix[k, k].operation = EditOperation.Change
                matrix[k, k].similarity = 0.0
        else:
            self.compute_edit_distance_matrix_lazy(matrix, sim)

        i = len(source_tokens)
        j = len(target_tokens)
        result.distance = matrix[i, j].score
        while i > 0 or j > 0:
            item = EditDistanceItem()
            item.resolution = EditDistanceResolution.Non
            item.operation = matrix[i, j].operation

            if item.operation == EditOperation.Identity:
                item.costs = 0.0
                i -= 1
                j -= 1
            elif item.operation == EditOperation.Change:
                item.costs = 1.0 - SimilarityComputers.get_token_similarity(source_tokens[i - 1], target_tokens[j - 1], True, disabled_auto_substitutions, self._characters_normalize_safely, self._apply_small_change_adjustment)

                if diagonal_only:
                    if item.costs < 0.001:
                        item.operation = EditOperation.Identity
                    else:
                        result.distance += 1.0

                i -= 1
                j -= 1
            elif item.operation == EditOperation.Insert:
                item.costs = 1.0
                j -= 1
            elif item.operation == EditOperation.Delete:
                item.costs = 1.0
                i -= 1
            elif item.operation == EditOperation.Undefined:
                raise Exception("Internal ED computation error")
            item.source = i
            item.target = j
            result.add_at_start(item)

        if self._compute_moves:
            num = self.detect_moves(result, matrix)
            if num > 0:
                result.distance -= num * 2.0
                result.distance += num * 1.1
        return result, aligned_tags

