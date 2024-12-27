from Segment import Segment

class TuContext:
    def __init__(self, context1:int = 0, context2:int = 0):
        self.context1 = context1
        self.context2 = context2
        self.segment1:Segment = None
        self.segment2:Segment = None

    @staticmethod
    def segment_match(s1: Segment, s2: Segment) -> bool:
        return (not s1 and not s2) or (s1 is not None and s2 is not None and s1 == s2)

class TuContextData:
    def __init__(self):
        self.text_context:TuContext = None
        self.id_context:str = ''
        self.current_structure_context_override:str = None