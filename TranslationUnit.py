from Segment import Segment
from SystemFields import SystemFields
from Tag import *
from typing import *

class TranslationUnit:
    def __init__(self, _src_segment:Segment = None, _tgr_segment:Segment = None):
        self.src_segment:Segment = _src_segment
        self.trg_segment:Segment = _tgr_segment
        self.system_fields:SystemFields = SystemFields()

    @staticmethod
    def get_alignable_tags(segment):
        if segment is None or segment.elements is None or len(segment.elements) == 0:
            return None

        alignable_tags = []

        for segment_element in segment.elements:
            if isinstance(segment_element, Tag):
                tag = segment_element
                if tag.type in [TagType.Start, TagType.Standalone, TagType.TextPlaceholder, TagType.LockedContent]:
                    alignable_tags.append(tag)
                else:
                    tag.alignment_anchor = 0

        return alignable_tags if len(alignable_tags) > 0 else None

    def renumber_tag_anchors(self):
        max_alignment_anchor = [0]  # Using a list to simulate pass-by-reference behavior
        source_segment = self.src_segment
        if source_segment is not None:
            _, max_alignment_anchor = source_segment.renumber_tag_anchors(max_alignment_anchor)

        target_segment = self.trg_segment
        if target_segment is not None:
            _, max_alignment_anchor = target_segment.renumber_tag_anchors(max_alignment_anchor)

        return max_alignment_anchor[0]  # Return the updated value

    @staticmethod
    def assign_tag_idsi(alignable_tags: List[Tag], used_ids: Set[int], next_id: int) -> int:
        """
        Assign unique IDs to tags that do not already have a TagID.

        :param alignable_tags: List of tags to process.
        :param used_ids: Set of already used IDs.
        :param next_id: Starting point for assigning new IDs.
        :return: The updated next_id after assigning new IDs.
        """
        if alignable_tags is None:
            return next_id

        for tag in alignable_tags:
            if not tag.tagid:  # Check for None or empty string
                while next_id in used_ids:
                    next_id += 1
                used_ids.add(next_id)
                tag.tagid = str(next_id)  # Assign the ID as a string
                next_id += 1

        return next_id

    @staticmethod
    def collect_integer_tag_ids(alignable_tags: List[Tag], used_ids: Set[int]) -> None:
        """
        Collect integer TagIDs from the tags and add them to the used_ids set.

        :param alignable_tags: List of tags to process.
        :param used_ids: Set to collect the unique integer TagIDs.
        """
        if alignable_tags is None:
            return

        for tag in alignable_tags:
            if tag.tagid and tag.tagid.isdigit():
                item = int(tag.tagid)
                if item not in used_ids:
                    used_ids.add(item)

    @staticmethod
    def assign_tag_ids(src_alignable_tags: List[Tag], trg_alignable_tags: List[Tag]) -> Set[int]:
        """
        Assign unique TagIDs to tags in source and target alignable tags.
        Returns the set of used IDs.
        """
        used_ids = set()
        TranslationUnit.collect_integer_tag_ids(src_alignable_tags, used_ids)
        TranslationUnit.collect_integer_tag_ids(trg_alignable_tags, used_ids)

        next_id = 0
        next_id = TranslationUnit.assign_tag_idsi(src_alignable_tags, used_ids, next_id)
        next_id = TranslationUnit.assign_tag_idsi(trg_alignable_tags, used_ids, next_id)

        return used_ids

    @staticmethod
    def clear_alignment_anchors(tag_list: List[Tag]):
        """
        Clears the alignment anchors for a list of Tag objects by setting their AlignmentAnchor to 0.

        Args:
            tag_list (iterable): An iterable of Tag objects.
        """
        for tag in tag_list:
            tag.alignment_anchor = 0

    @staticmethod
    def find_aligned_tag(tags, anchor):
        """
        Finds the first tag in the collection with the specified alignment anchor.

        Args:
            tags (iterable): A collection of Tag objects.
            anchor (int): The alignment anchor to search for.

        Returns:
            Tag: The first Tag with the specified alignment anchor, or None if not found.
        """
        if not tags or anchor <= 0:
            return None
        return next((tag for tag in tags if tag.alignment_anchor == anchor), None)

    @staticmethod
    def align_unaligned_locked_content_tags(src_alignable_tags, trg_alignable_tags, max_alignment_anchor):
        """
        Aligns unaligned locked content tags between source and target alignable tags.

        Args:
            src_alignable_tags (iterable): Source alignable tags (list or other iterable of Tag objects).
            trg_alignable_tags (list): Target alignable tags (list of Tag objects).
            max_alignment_anchor (int): Reference to the maximum alignment anchor (modified in place).

        Returns:
            int: Updated maximum alignment anchor.
        """
        for src_tag in src_alignable_tags:
            if src_tag.alignment_anchor == 0 and src_tag.type == TagType.LockedContent:
                for trg_tag in trg_alignable_tags:
                    if (
                            trg_tag.alignment_anchor == 0 and
                            trg_tag.type == TagType.LockedContent and
                            src_tag.text_equivalent == trg_tag.text_equivalent
                    ):
                        max_alignment_anchor += 1
                        src_tag.alignment_anchor = max_alignment_anchor
                        trg_tag.alignment_anchor = max_alignment_anchor
                        break
        return max_alignment_anchor

    @staticmethod
    def tag_ids_are_compatible(t1:Tag, t2:Tag):
        """
        Checks if the TagIDs of two tags are compatible.

        Args:
            t1 (Tag): The first tag.
            t2 (Tag): The second tag.

        Returns:
            bool: True if the TagIDs are compatible, False otherwise.
        """
        return (
                not t1.tagid or
                not t2.tagid or
                t1.tagid.lower() == t2.tagid.lower()
        )

    @staticmethod
    def align_unaligned_tags(src_alignable_tags, trg_alignable_tags, max_alignment_anchor):
        """
        Aligns unaligned tags between source and target alignable tag lists.

        Args:
            src_alignable_tags (list of Tag): Source alignable tags.
            trg_alignable_tags (list of Tag): Target alignable tags.
            max_alignment_anchor (int): Current maximum alignment anchor.

        Returns:
            int: Updated maximum alignment anchor.
        """
        # Align locked content tags
        max_alignment_anchor = TranslationUnit.align_unaligned_locked_content_tags(src_alignable_tags, trg_alignable_tags, max_alignment_anchor)

        for tag in src_alignable_tags:
            if tag.alignment_anchor == 0:
                best_match = None
                best_similarity = SegmentElement.Similarity.Non

                for trg_tag in trg_alignable_tags:
                    if (trg_tag.alignment_anchor == 0
                            and trg_tag.type == tag.type
                            and (best_match is None or tag.get_similarity(trg_tag) > best_similarity)):
                        best_match = trg_tag
                        best_similarity = tag.get_similarity(trg_tag)

                if (best_match is not None
                        and (best_similarity > SegmentElement.Similarity.IdenticalType
                             or TranslationUnit.tag_ids_are_compatible(tag, best_match))):
                    max_alignment_anchor += 1
                    tag.alignment_anchor = max_alignment_anchor
                    best_match.alignment_anchor = tag.alignment_anchor

        return max_alignment_anchor

    @staticmethod
    def ensure_consistent_alignment(src_alignable_tags, trg_alignable_tags, used_tag_ids):
        """
        Ensures consistent alignment of tags between source and target alignable tag lists.

        Args:
            src_alignable_tags (list of Tag): Source alignable tags.
            trg_alignable_tags (list of Tag): Target alignable tags.
            used_tag_ids (set of int): Set of used tag IDs.

        Returns:
            None
        """
        num = max(used_tag_ids.union({0}))  # Get the maximum value from used_tag_ids or 0 if empty.

        for src_tag in src_alignable_tags:
            trg_tag = TranslationUnit.find_aligned_tag(trg_alignable_tags, src_tag.alignment_anchor)

            if trg_tag and (
                    not src_tag.tagid
                    or not trg_tag.tagid
                    or src_tag.tagid.lower() != trg_tag.tagid.lower()
            ):
                if src_tag.tagid:
                    trg_tag.tagid = src_tag.tagid
                elif trg_tag.tagid:
                    src_tag.tagid = trg_tag.tagid
                else:
                    num += 1
                    src_tag.tagid = str(num)
                    trg_tag.tagid = src_tag.tagid

    def check_and_compute_tag_associations(self):
        alignable_tags = TranslationUnit.get_alignable_tags(self.src_segment)
        alignable_tags2 = TranslationUnit.get_alignable_tags(self.trg_segment)
        max_alignment_anchor = 0

        # Check if either of the lists are not empty
        if alignable_tags or alignable_tags2:
            TranslationUnit.renumber_tag_anchors(max_alignment_anchor)

        used_tag_ids = TranslationUnit.assign_tag_ids(alignable_tags, alignable_tags2)

        # If any of the alignable tags are None, clear alignment anchors
        if alignable_tags is None or alignable_tags2 is None:
            if alignable_tags2 is not None:
                TranslationUnit.clear_alignment_anchors(alignable_tags2)
            if alignable_tags is not None:
                TranslationUnit.clear_alignment_anchors(alignable_tags)
            return

        flag = False

        # Process tags in alignable_tags
        for tag in alignable_tags:
            if tag.AlignmentAnchor > 0:
                if TranslationUnit.find_aligned_tag(alignable_tags2, tag.AlignmentAnchor) is None:
                    tag.AlignmentAnchor = 0
            else:
                flag = True

        # Process tags in alignable_tags2
        for tag2 in alignable_tags2:
            if tag2.AlignmentAnchor > 0:
                if TranslationUnit.find_aligned_tag(alignable_tags, tag2.AlignmentAnchor) is None:
                    tag2.AlignmentAnchor = 0
            else:
                flag = True

        # If there were unaligned tags, align them
        if flag:
            TranslationUnit.align_unaligned_tags(alignable_tags, alignable_tags2, max_alignment_anchor)

        # Ensure consistent alignment
        TranslationUnit.ensure_consistent_alignment(alignable_tags, alignable_tags2, used_tag_ids)