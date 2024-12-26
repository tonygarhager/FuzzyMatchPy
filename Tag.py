from SegmentElement import SegmentElement

class TagType:
    Undefined = 0
    Start = 1
    End = 2
    Standalone = 3
    TextPlaceholder = 4
    LockedContent = 5
    UnmatchedStart = 6
    UnmatchedEnd = 7

class Tag(SegmentElement):
    def __init__(self, type:TagType = TagType.Undefined,
                 tagid:str = '',
                 anchor:int = 0,
                 alignment_anchor:int = 0,
                 text_equivalent:str = '',
                 canhide:bool = False,):
        self.anchor = anchor
        self.alignment_anchor = alignment_anchor
        self.tagid = tagid
        self.type = type
        self.canhide = canhide

        if type == TagType.TextPlaceholder or type == TagType.LockedContent:
            self.text_equivalent = text_equivalent

    def get_similarity(self, other):
        if isinstance(other, Tag) == False or self.type != other.type:
            return SegmentElement.Similarity.Non
        if self.tagid is None and other.tagid is None:
            if self.anchor != other.anchor:
                return SegmentElement.Similarity.IdenticalType
            return SegmentElement.Similarity.IdenticalValueAndType
        else:
            if self.tagid is None and other.tagid is None:
                return SegmentElement.Similarity.IdenticalType
            if self.tagid == other.tagid:
                return SegmentElement.Similarity.IdenticalType
            return SegmentElement.Similarity.IdenticalValueAndType

    def to_string(self):
        sb = '<'
        if self.type == TagType.End:
            sb += '/'
        sb += str(self.anchor)
        if self.type != TagType.End:
            if self.alignment_anchor != 0:
                sb += ' x=' + str(self.alignment_anchor)
            if self.tagid is not None and len(self.tagid) > 0:
                sb += ' id=' + str(self.tagid)
        if (self.type == TagType.Standalone or
            self.type == TagType.TextPlaceholder or
            self.type == TagType.LockedContent):
            if (self.type == TagType.TextPlaceholder or
            self.type == TagType.LockedContent):
                sb += ' text-equiv=\"'
                if self.text_equivalent is not None:
                    sb += self.text_equivalent
                sb += '\"'
            sb += '/'
        sb += '>'
        return sb