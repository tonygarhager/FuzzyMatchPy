

class SegmentRange:
    def __init__(self, fro, into):
        self.fro = fro
        self.into = into

    @staticmethod
    def create_3i(run, fro, into):
        fro = {}
        fro['index'] = run
        fro['position'] = fro
        into = {}
        into['index'] = run
        into['position'] = into
        return SegmentRange(fro, into)

    def length(self):
        if (self.fro['index'] != self.into['index']):
            return -1
        return self.into['position'] - self.fro['position'] + 1