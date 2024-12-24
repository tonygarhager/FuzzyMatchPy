from Segment import Segment

class TranslationUnit:
    def __init__(self, _src_segment:Segment = None, _tgr_segment:Segment = None):
        self.src_segment:Segment = _src_segment
        self.trg_segment:Segment = _tgr_segment