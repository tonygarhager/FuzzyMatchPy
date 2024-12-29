
class SegmentPosition:
    def __init__(self, run_index:int = 0, position_in_run:int = 0):
        self._run_index = run_index
        self._position_in_run = position_in_run

    @property
    def index(self):
        return self._run_index
    @index.setter
    def index(self, value):
        self._run_index = value
    @property
    def position(self):
        return self._position_in_run
    @position.setter
    def position(self, value):
        self._position_in_run = value

    def duplicate(self):
        return SegmentPosition(self._run_index, self._position_in_run)

class SegmentRange:
    def __init__(self, fro:SegmentPosition, into:SegmentPosition):
        self.fro = fro
        self.into = into

    @staticmethod
    def create_3i(run:int, fro:int, into:int):
        fro_seg = SegmentPosition()
        fro_seg.index = run
        fro_seg.position = fro
        into_seg = SegmentPosition()
        into_seg.index = run
        into_seg.position = into
        return SegmentRange(fro_seg, into_seg)

    @property
    def length(self):
        if (self.fro.index != self.into.index):
            return -1
        return self.into.position - self.fro.position + 1

    def duplicate(self):
        return SegmentRange(self.fro, self.into)