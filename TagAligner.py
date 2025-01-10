from SequenceAlignmentComputer import SequenceAlignmentComputer
from SimilarityMatrix import SimilarityMatrix
from Tag import TagType
from TagAssociations import *
from TagToken import TagToken
from TokenIndexLcsScoreProvider import TokenIndexLcsScoreProvider

class TagAligner:
    @staticmethod
    def align_paired_tags(source_tokens: list, target_tokens: list, similarity_matrix: SimilarityMatrix) -> TagAssociations:
        src_paired_tags = TagAligner.find_paired_tags(source_tokens)
        if not src_paired_tags:
            return None

        trg_paired_tags = TagAligner.find_paired_tags(target_tokens)
        if not trg_paired_tags:
            return None

        associations = TagAssociations()
        processed_src_tags = [False] * len(src_paired_tags)
        processed_trg_tags = [False] * len(trg_paired_tags)

        if src_paired_tags and trg_paired_tags:
            scores = TagAligner.compute_tag_association_scores(similarity_matrix, src_paired_tags, trg_paired_tags, True)
            if scores is None:
                return None

            while True:
                max_score = float('-inf')
                best_src_idx = -1
                best_trg_idx = -1

                for i, src_processed in enumerate(processed_src_tags):
                    if not src_processed:
                        for j, trg_processed in enumerate(processed_trg_tags):
                            if not trg_processed and scores[i][j] > max_score:
                                max_score = scores[i][j]
                                best_src_idx = i
                                best_trg_idx = j

                if best_src_idx < 0:
                    break

                associations.add(src_paired_tags[best_src_idx], trg_paired_tags[best_trg_idx], EditOperation.Change)
                processed_src_tags[best_src_idx] = True
                processed_trg_tags[best_trg_idx] = True

        for i, processed in enumerate(processed_src_tags):
            if not processed:
                associations.add(src_paired_tags[i], None)

        for i, processed in enumerate(processed_trg_tags):
            if not processed:
                associations.add(None, trg_paired_tags[i])

        return associations

    @staticmethod
    def find_paired_tags(tokens: list) -> list:
        tag_pairs = []
        for i, token in enumerate(tokens):
            if isinstance(token, TagToken) and token.tag.type == TagType.Start:
                for j in range(i + 1, len(tokens)):
                    if isinstance(tokens[j], TagToken) and tokens[j].tag.type == TagType.End and tokens[j].tag.anchor == token.tag.anchor:
                        tag_pairs.append(PairedTag(i, j, token.tag.anchor))
                        break
        return tag_pairs

    @staticmethod
    def compute_tag_association_scores(similarity_matrix, src_paired_tags, trg_paired_tags, use_end_positions):
        lcs_scores = [[0 for _ in range(len(trg_paired_tags))] for _ in range(len(src_paired_tags))]
        source_indices = list(range(len(similarity_matrix.source_tokens)))
        target_indices = list(range(len(similarity_matrix.target_tokens)))

        token_index_lcs_score_provider = TokenIndexLcsScoreProvider(similarity_matrix, 0.75, True)
        aligner = SequenceAlignmentComputer(source_indices, target_indices, token_index_lcs_score_provider, None, 1, 1)

        for src_tag in range(len(src_paired_tags) - 1, -1, -1):
            s_pt = src_paired_tags[src_tag]
            upto_source = s_pt.end if use_end_positions else s_pt.start

            for trg_tag in range(len(trg_paired_tags) - 1, -1, -1):
                t_pt = trg_paired_tags[trg_tag]
                upto_target = t_pt.end if use_end_positions else t_pt.start

                aligned_substrings = aligner.compute(upto_source, upto_target)
                if aligned_substrings and len(aligned_substrings) > 0:
                    score = aligned_substrings[0].score
                    num = score - (upto_source - score) - (upto_target - score)

                    if use_end_positions:
                        penalty = 0
                    else:
                        penalty = abs(TagAligner.get_tag_span(s_pt) - TagAligner.get_tag_span(t_pt)) // 2

                    lcs_scores[src_tag][trg_tag] = num - penalty

        return lcs_scores

    @staticmethod
    def get_tag_span(pt: PairedTag) -> int:
        return pt.end - pt.start - 1