from typing import List

from Segment import Segment
from collections import defaultdict
from Tag import *
from TagToken import TagToken
from Token import Token
from TokenBundle import TokenBundle


class PlaceableType:
    Non = 0
    Text = 1
    StandaloneTag = 2
    PairedTagStart = 3
    PairedTagEnd = 4
    TextPlaceholder = 5
    LockedContent = 6

class Placeable:
    def __init__(self, t: PlaceableType, source_token_index: int = -1, target_token_index: int = -1):
        self.type = t
        self.source_token_index = source_token_index
        self.target_token_index = target_token_index

    def is_tag(self) -> bool:
        return self.type == PlaceableType.PairedTagStart or self.type == PlaceableType.PairedTagEnd or self.type == PlaceableType.StandaloneTag or self.type == PlaceableType.TextPlaceholder or self.type == PlaceableType.LockedContent

    def is_tag_compatible(self, tag_type: TagType) -> bool:
        if self.type == PlaceableType.StandaloneTag:
            return tag_type == TagType.Standalone
        elif self.type == PlaceableType.PairedTagStart:
            return tag_type == TagType.Start
        elif self.type == PlaceableType.PairedTagEnd:
            return tag_type == TagType.End
        elif self.type == PlaceableType.TextPlaceholder:
            return tag_type == TagType.TextPlaceholder
        elif self.type == PlaceableType.LockedContent:
            return tag_type == TagType.LockedContent
        return False

class PlaceableAssociation:
    def __init__(self, doc_placeable: Placeable, mem_placeable: Placeable):
        self.document = doc_placeable
        self.memory = mem_placeable
        PlaceableAssociation.verify_type_compatibility(self.document, self.memory)

    def get_type(self) -> PlaceableType:
        if self.memory is not None:
            return self.memory.type
        if self.document is not None:
            return self.document.type
        return PlaceableType.Non

    @staticmethod
    def verify_type_compatibility(a: Placeable, b: Placeable) -> bool:
        if PlaceableAssociation.are_associable(a, b) == False:
            raise('Placeable types differ')

    @staticmethod
    def are_associable(a: Placeable, b: Placeable) -> bool:
        return a is not None and b is not None and (a.type == b.type or (a.type == PlaceableType.StandaloneTag and b.type == PlaceableType.TextPlaceholder) or a.type == PlaceableType.TextPlaceholder and b.type == PlaceableType.StandaloneTag)

class PlaceableComputer:
    @staticmethod
    def compute_placeables(src_segment:Segment, trg_segment:Segment) -> List[Placeable]:
        if src_segment is None:
            raise Exception('src_segment is None')
        if src_segment.tokens is None:
            raise Exception('src_segment.tokens is None')

        src_has_bundles = src_segment.has_token_bundles()
        trg_has_bundles = trg_segment is not None and trg_segment.has_token_bundles()
        list = PlaceableComputer.compute_tag_alignments(src_segment, trg_segment)
        list2 = PlaceableComputer.compute_nontag_alignments(src_segment, trg_segment, src_has_bundles, trg_has_bundles)

        if list2 is not None:
            if list is None:
                list = list2
            else:
                list.extend(list2)
        return list

    @staticmethod
    def compute_tag_alignments(src_segment:Segment, trg_segment:Segment) -> List[Placeable]:
        if src_segment is None:
            raise ValueError("srcSegment cannot be None")

        src_dictionary = defaultdict(bool)
        trg_dictionary = defaultdict(bool)

        # Populate source dictionary
        for i, token in enumerate(src_segment.tokens):
            if isinstance(token, TagToken):
                src_dictionary[i] = False

        # Populate target dictionary if target segment is not None
        has_target_tokens = trg_segment and trg_segment.tokens is not None
        if has_target_tokens:
            for j, token in enumerate(trg_segment.tokens):
                if isinstance(token, TagToken):
                    trg_dictionary[j] = False

        # Return None if no tokens exist
        if not src_dictionary and not trg_dictionary:
            return None

        placeables = []

        if has_target_tokens:
            for k, token in enumerate(src_segment.tokens):
                if src_dictionary.get(k) is False:
                    tag_token = token if isinstance(token, TagToken) else None
                    if tag_token:
                        tag = tag_token.tag
                        if tag.alignment_anchor > 0 and tag.type in [
                            TagType.Standalone,
                            TagType.Start,
                            TagType.TextPlaceholder,
                            TagType.LockedContent,
                        ]:
                            num = -1
                            num2 = -1
                            for l, trg_token in enumerate(trg_segment.tokens):
                                if trg_dictionary.get(l) is False:
                                    trg_tag_token = trg_token if isinstance(trg_token, TagToken) else None
                                    if trg_tag_token:
                                        trg_tag = trg_tag_token.tag
                                        if trg_tag.alignment_anchor == tag.alignment_anchor:
                                            src_dictionary[k] = True
                                            trg_dictionary[l] = True
                                            if trg_tag.type == TagType.Standalone:
                                                placeables.append(Placeable(PlaceableType.StandaloneTag, k, l))
                                                break
                                            if trg_tag.type == TagType.TextPlaceholder:
                                                placeables.append(Placeable(PlaceableType.TextPlaceholder, k, l))
                                                break
                                            if trg_tag.type == TagType.LockedContent:
                                                placeables.append(Placeable(PlaceableType.LockedContent, k, l))
                                                break
                                            placeables.append(Placeable(PlaceableType.PairedTagStart, k, l))
                                            num = trg_tag.anchor
                                        elif trg_tag.type == TagType.End and num >= 0 and trg_tag.anchor == num:
                                            num2 = l
                                            break
                            if tag.type == TagType.Start and num2 >= 0:
                                for m, src_token in enumerate(src_segment.tokens[k + 1:], start=k + 1):
                                    src_tag_token = src_token if isinstance(src_token, TagToken) else None
                                    if src_tag_token and not src_dictionary[m]:
                                        if src_tag_token.tag.type == TagType.End and src_tag_token.tag.anchor == tag.anchor:
                                            src_dictionary[m] = True
                                            trg_dictionary[num2] = True
                                            placeables.append(Placeable(PlaceableType.PairedTagEnd, m, num2))
                                            break

        # Add unaligned source tokens
        for index, aligned in src_dictionary.items():
            if not aligned:
                placeables.append(Placeable(
                    PlaceableComputer.get_placeable_type(src_segment.tokens[index]),
                    index,
                    -1
                ))

        # Add unaligned target tokens
        if not trg_segment or trg_segment.tokens is None:
            return placeables

        for index, aligned in trg_dictionary.items():
            if not aligned:
                placeables.append(Placeable(
                    PlaceableComputer.get_placeable_type(trg_segment.tokens[index]),
                    -1,
                    index
                ))

        return placeables

    @staticmethod
    def compute_nontag_alignments(src_segment, trg_segment, src_has_bundles, trg_has_bundles):
        src_dict = defaultdict(bool)
        trg_dict = defaultdict(bool)

        # Populate source dictionary
        for i, token in enumerate(src_segment.tokens):
            if token.is_placeable and not isinstance(token, TagToken):
                src_dict[i] = False

        # Populate target dictionary if target segment is not None
        has_target_tokens = trg_segment and trg_segment.tokens is not None
        if has_target_tokens:
            for j, token in enumerate(trg_segment.tokens):
                if token.is_placeable and not isinstance(token, TagToken):
                    trg_dict[j] = False

        # Handle empty dictionaries
        if not src_dict and not trg_dict:
            if src_has_bundles:
                src_segment.remove_token_bundles()
            if trg_has_bundles and trg_segment is not None:
                trg_segment.remove_token_bundles()
            return None

        placeables = []

        if has_target_tokens:
            for k, src_token in enumerate(src_segment.tokens):
                if src_dict.get(k) is False:
                    best_match_index = -1
                    best_similarity = SegmentElement.Similarity.Non

                    # Find the best matching target token
                    for l, trg_token in enumerate(trg_segment.tokens):
                        if trg_dict.get(l) is False:
                            similarity = src_token.get_similarity(trg_token)
                            if similarity > best_similarity:
                                best_similarity = similarity
                                best_match_index = l

                    # If a valid match is found
                    if best_similarity > SegmentElement.Similarity.IdenticalType:
                        src_dict[k] = True
                        trg_dict[best_match_index] = True

                        is_src_bundle = isinstance(src_token, TokenBundle)
                        is_trg_bundle = isinstance(trg_segment.tokens[best_match_index], TokenBundle)

                        if is_src_bundle or is_trg_bundle:
                            trg_token = trg_segment.tokens[best_match_index]
                            PlaceableComputer.get_best_bundle_combination(src_token, trg_token)
                            src_segment.tokens[k] = src_token
                            trg_segment.tokens[best_match_index] = trg_token

                        placeables.append(Placeable(
                            PlaceableComputer.get_placeable_type(src_token),
                            k,
                            best_match_index
                        ))

        # Remove token bundles if applicable
        if src_has_bundles:
            src_segment.remove_token_bundles()
        if trg_has_bundles and trg_segment is not None:
            trg_segment.remove_token_bundles()

        # Add unmatched source tokens
        for index, matched in src_dict.items():
            if not matched:
                placeables.append(Placeable(
                    PlaceableComputer.get_placeable_type(src_segment.tokens[index]),
                    index,
                    -1
                ))

        # Add unmatched target tokens
        if not has_target_tokens:
            return placeables

        for index, matched in trg_dict.items():
            if not matched:
                placeables.append(Placeable(
                    PlaceableComputer.get_placeable_type(trg_segment.tokens[index]),
                    -1,
                    index
                ))

        return placeables

    @staticmethod
    def get_best_bundle_combination(src_token:Token, trg_token:Token):
        """
        Adjusts src_token and trg_token to the best combination based on similarity.

        :param src_token: Source token, can be a TokenBundle or Token
        :param trg_token: Target token, can be a TokenBundle or Token
        :return: Tuple (adjusted_src_token, adjusted_trg_token)
        """
        token_bundle_src = src_token if isinstance(src_token, TokenBundle) else None
        token_bundle_trg = trg_token if isinstance(trg_token, TokenBundle) else None

        if not token_bundle_src and not token_bundle_trg:
            return src_token, trg_token

        # Sort token bundles by decreasing priority
        if token_bundle_src:
            token_bundle_src.sort_by_decreasing_priority()
        if token_bundle_trg:
            token_bundle_trg.sort_by_decreasing_priority()

        best_src_index = -1
        best_trg_index = -1
        best_similarity = SegmentElement.Similarity.Non

        # Evaluate similarities
        if token_bundle_src:
            for i, prioritized_token_src in enumerate(token_bundle_src):
                if token_bundle_trg:
                    for j, prioritized_token_trg in enumerate(token_bundle_trg):
                        similarity = prioritized_token_trg.token.get_similarity(prioritized_token_src.token)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_src_index = i
                            best_trg_index = j
                else:
                    similarity = trg_token.get_similarity(prioritized_token_src.token)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_src_index = i
                        best_trg_index = -1
        else:
            for k, prioritized_token_trg in enumerate(token_bundle_trg):
                similarity = prioritized_token_trg.token.get_similarity(src_token)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_src_index = -1
                    best_trg_index = k

        # Update tokens based on the best match
        if best_src_index >= 0 and token_bundle_src:
            src_token = token_bundle_src[best_src_index].token
            src_token.span = token_bundle_src.span

        if best_trg_index >= 0 and token_bundle_trg:
            trg_token = token_bundle_trg[best_trg_index].token
            trg_token.span = token_bundle_trg.span

        return src_token, trg_token

    @staticmethod
    def get_placeable_type(t:Token) -> PlaceableType:
        if t.is_placeable == False:
            return PlaceableType.Non
        if isinstance(t, TagToken) == False:
            return PlaceableType.Text

        if t.tag.type == TagType.Start:
            return PlaceableType.PairedTagStart
        elif t.tag.type == TagType.End:
            return PlaceableType.PairedTagEnd
        elif t.tag.type == TagType.Standalone:
            return PlaceableType.StandaloneTag
        elif t.tag.type == TagType.TextPlaceholder:
            return PlaceableType.TextPlaceholder
        elif t.type.type == TagType.LockedContent:
            return PlaceableType.LockedContent
        return PlaceableType.Non

    @staticmethod
    def convert_placeables_to_alignments(placeables:[], alignment_data, source_tokens:[], target_tokens:[]):
        pass

