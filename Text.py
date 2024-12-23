from SegmentElement import SegmentElement

class Text(SegmentElement):
    def __init__(self, text = None):
        self.value = text

    def duplicate(self):
        text = Text(self.value)
        return text

    def get_similarity(self, other):
        if not other or not self.value or not other.value:
            return SegmentElement.Similarity.Non

        if self.value != other.value:
            return SegmentElement.Similarity.Non

        return SegmentElement.Similarity.IdenticalValueAndType