from typing import List

from Segment import Segment
from collections import defaultdict
from Tag import TagType

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

    def compute_tag_alignments(src_segment, trg_segment):
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
