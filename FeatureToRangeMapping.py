from SegmentRange import SegmentRange

class FeatureToRangeMapping:
    def __init__(self, feature:int, range:SegmentRange):
        self.feature = feature
        self.range = range