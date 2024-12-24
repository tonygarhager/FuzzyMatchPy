
class PlaceableType:
    Non = 0
    Text = 1
    StandaloneTag = 2
    PairedTagStart = 3
    PairedTagEnd = 4
    TextPlaceholder = 5
    LockedContent = 6

class TagType:
    Undefined = 0
    Start = 1
    End = 2
    Standalone = 3
    TextPlaceholder = 4
    LockedContent = 5
    UnmatchedStart = 6
    UnmatchedEnd = 7

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
