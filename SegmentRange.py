

class SegmentRange:
    def __init__(self, fro, into):
        self.fro = fro
        self.into = into

    def length(self):
        if (self.fro['index'] != self.into['index']):
            return -1
        return self.into['position'] - self.fro['position'] + 1