from AnnotatedSegment import AnnotatedSegment
from AnnotatedTranslationMemory import AnnotatedTranslationMemory
from Segment import Segment
from SegmentEditor import SegmentEditor
from TranslationUnit import TranslationUnit


class AnnotatedTranslationUnit:
    def __init__(self, tm:AnnotatedTranslationMemory, tu:TranslationUnit, keep_tokens:bool, keep_peripheral_whitespace:bool):
        tu.check_and_compute_tag_associations()
        if keep_tokens == False:
            AnnotatedTranslationUnit.clean(tu.src_segment)
            AnnotatedTranslationUnit.clean(tu.trg_segment)

        self.translation_unit = tu
        self.source = AnnotatedSegment(tm, tu.src_segment, False, keep_tokens, keep_peripheral_whitespace)
        self.target = None if tu.trg_segment is None else AnnotatedSegment(tm, tu.trg_segment, True, keep_tokens, keep_peripheral_whitespace)

    @staticmethod
    def clean(segment:Segment):
        if segment is None:
            return
        segment.tokens = None
        if segment.elements is not None:
            SegmentEditor.clean_segment(segment)

    def __str__(self):
        arg = str(self.source) if self.source is not None else "null"

        translation_unit = self.translation_unit
        if translation_unit is None:
            num = None
        else:
            resource_id = translation_unit.resource_id
            num = resource_id.id if resource_id is not None else None

        return f"{num if num is not None else 0}-{arg}"

