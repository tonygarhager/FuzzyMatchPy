import numpy as np

from BuiltinRecognizers import BuiltinRecognizers
from EditDistance import EditDistance, EditOperation, EditDistanceItem, EditDistanceResolution
from SimilarityComputers import MatrixItem, SimilarityComputers
from SimilarityMatrix import SimilarityMatrix
from Tag import TagType
from TagAligner import TagAligner
from TagToken import TagToken


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

    def detect_moves(self, result, matrix):
        num = 0
        i = 0
        while i < len(result.items):
            print(i)
            operation = result.items[i].operation
            if operation == EditOperation.Delete or operation == EditOperation.Insert:
                num2 = num3 = num4 = num5 = 0
                nj = -1
                for j in range(i + 1, len(result.items)):
                    if operation == EditOperation.Delete and result.items[j].operation == EditOperation.Insert:
                        if matrix[result.items[i].source + 1][result.items[j].target + 1].similarity >= 0.95:
                            num2 = result.items[i].source
                            num4 = result.items[i].target
                            num3 = result.items[j].target
                            num5 = result.items[j].source
                            nj = j
                            break
                    elif operation == EditOperation.Insert and result.items[j].operation == EditOperation.Delete:
                        if matrix[result.items[j].source + 1][result.items[i].target + 1].similarity >= 0.95:
                            num2 = result.items[j].source
                            num4 = result.items[j].target
                            num3 = result.items[i].target
                            num5 = result.items[i].source
                            nj = j
                            break

                if nj != -1 and nj < len(result.items):
                    edit_distance_item = result.items[i]
                    edit_distance_item.operation = EditOperation.Move
                    edit_distance_item.source = num2
                    edit_distance_item.target = num3
                    edit_distance_item.move_source_target = num4
                    edit_distance_item.move_target_source = num5
                    result.items[i] = edit_distance_item
                    result.items.pop(nj)
                    num += 1
            i += 1
        return num

    @staticmethod
    def patch_similarity_matrix(sim, src_tokens, trg_tokens, tag_alignment):
        """
        Patches the similarity matrix based on tag alignment.

        :param sim: SimilarityMatrix instance.
        :param src_tokens: List of source tokens.
        :param trg_tokens: List of target tokens.
        :param tag_alignment: TagAssociations instance for tag alignment.
        """
        if tag_alignment is not None and len(tag_alignment) != 0:
            for s, src_token in enumerate(src_tokens):
                if isinstance(src_token, TagToken):
                    tag = src_token.tag
                    if tag.type in (TagType.Start, TagType.End):
                        for t, trg_token in enumerate(trg_tokens):
                            flag = sim.is_assigned(s, t)
                            flag2 = flag
                            if flag2:
                                num = sim.get_element_at(s, t)
                                flag2 = num < 0.0
                            if not flag2 and isinstance(trg_token, TagToken):
                                tag2 = trg_token.tag
                                if tag2.type in (TagType.Start, TagType.End) and not tag_alignment.are_associated(s, t):
                                    sim.set_element_at(s, t, -1.0)

    @staticmethod
    def compute_edit_distance_matrix_full(matrix, sim, aligned_tags):
        """
        Computes the full edit distance matrix based on the similarity matrix and aligned tags.

        :param matrix: 2D list of MatrixItem objects representing the edit distance matrix.
        :param sim: SimilarityMatrix instance.
        :param aligned_tags: TagAssociations instance for aligned tags.
        """
        for i in range(1, len(sim.source_tokens) + 1):
            for j in range(1, len(sim.target_tokens) + 1):
                num = sim.get_element_at(i - 1, j - 1)
                num2 = num
                num3 = 100000.0 if num2 < 0.0 else (matrix[i - 1][j - 1].score + (1.0 - num2))
                num4 = matrix[i][j - 1].score + 1.0
                num5 = matrix[i - 1][j].score + 1.0
                num6 = min(num3, num5, num4)

                edit_operation = EditOperation.Undefined
                if num6 == num5:
                    edit_operation = EditOperation.Delete
                elif num6 == num4:
                    edit_operation = EditOperation.Insert
                elif num6 == num3:
                    edit_operation = EditOperation.Identity if num2 == 1.0 else EditOperation.Change

                if aligned_tags is not None and len(aligned_tags) > 0:
                    operation_by_source_position = aligned_tags.get_operation_by_source_position(i - 1)
                    operation_by_target_position = aligned_tags.get_operation_by_target_position(j - 1)
                    if (operation_by_source_position in {EditOperation.Insert,
                                                         EditOperation.Delete}) and edit_operation != operation_by_source_position:
                        edit_operation = operation_by_source_position
                    elif (operation_by_target_position in {EditOperation.Insert,
                                                           EditOperation.Delete}) and edit_operation != operation_by_target_position:
                        edit_operation = operation_by_target_position

                matrix[i][j].similarity = num2
                matrix[i][j].operation = edit_operation

                if edit_operation != EditOperation.Insert:
                    matrix[i][j].score = num5 if edit_operation == EditOperation.Delete else num3
                else:
                    matrix[i][j].score = num4

    def compute_edit_distance_impl_original(self, source_tokens, target_tokens, disabled_auto_substitutions:BuiltinRecognizers, diagonal_only:bool):
        if diagonal_only and len(target_tokens) != len(source_tokens):
            raise Exception("diagonal_only and target_tokens must have same length")
        result = EditDistance(len(source_tokens), len(target_tokens), 0.0)
        sim = SimilarityMatrix(source_tokens, target_tokens, False, disabled_auto_substitutions, self._characters_normalize_safely, self._apply_small_change_adjustment)
        matrix = SegmentEditDistanceComputer.create_edit_distance_matrix(source_tokens, target_tokens)

        aligned_tags = TagAligner.align_paired_tags(source_tokens, target_tokens, sim)

        if aligned_tags is not None and len(aligned_tags) > 0:
            SegmentEditDistanceComputer.patch_similarity_matrix(sim, source_tokens, target_tokens, aligned_tags)
            SegmentEditDistanceComputer.compute_edit_distance_matrix_full(matrix, sim, aligned_tags)

        elif diagonal_only:
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

        if aligned_tags is not None and len(aligned_tags) > 0:
            self.fix_tag_actions(source_tokens, target_tokens, result, aligned_tags)

        if self._compute_moves:
            num = self.detect_moves(result, matrix)
            if num > 0:
                result.distance -= num * 2.0
                result.distance += num * 1.1
        return result, aligned_tags

    @staticmethod
    def fix_tag_actions(source_tokens, target_tokens, result, tag_alignment):
        """
        Placeholder function for fixing tag actions in an edit distance result based on tag alignment.

        :param source_tokens: List of source tokens.
        :param target_tokens: List of target tokens.
        :param result: EditDistance instance representing the edit distance result.
        :param tag_alignment: TagAssociations instance for tag alignment.
        """
        pass
