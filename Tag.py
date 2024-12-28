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

    @staticmethod
    def fromStringType(stype:str):
        if stype == 'Undefined':
            return TagType.Undefined
        elif stype == 'Start':
            return TagType.Start
        elif stype == 'End':
            return TagType.End
        elif stype == 'Standalone':
            return TagType.Standalone
        elif stype == 'TextPlaceholder':
            return TagType.TextPlaceholder
        elif stype == 'LockedContent':
            return TagType.LockedContent
        elif stype == 'UnmatchedStart':
            return TagType.UnmatchedStart
        elif stype == 'UnmatchedEnd':
            return TagType.UnmatchedEnd
        else:
            return TagType.Undefined

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

    @staticmethod
    def from_xml(element):
        stag_type = element.find('Type').text
        tag_type = TagType.fromStringType(stag_type)
        tag_id = element.find('TagID')
        if tag_id is not None:
            tag_id = tag_id.text
        else:
            tag_id = ''
        anchor = element.find('Anchor')
        if anchor is not None:
            anchor = int(anchor.text)
        else:
            anchor = 0
        alignment_anchor = element.find('AlignmentAnchor')
        if alignment_anchor is not None:
            alignment_anchor = int(alignment_anchor.text)
        else:
            alignment_anchor = 0

        canhide = element.find('CanHide')
        if canhide is not None:
            if canhide.text.lower() == 'true':
                canhide = True
            else:
                canhide = False
        else:
            canhide = False

        return Tag(tag_type,tag_id,anchor,alignment_anchor,'', canhide)

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