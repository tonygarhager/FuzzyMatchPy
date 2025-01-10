import io
from typing import Optional

from StemmingRuleParser import StemmingRuleParser
from StemmingRuleSet import StemmingRuleSet


class StemmingRuleSetReader:
    def __init__(self, reader: Optional[io.TextIOBase] = None, stream: Optional[io.BytesIO] = None,
                 path: Optional[str] = None):
        if reader:
            #reader.read(3)
            self._reader = reader
            self._own_stream = False
        elif stream:
            self._reader = io.TextIOWrapper(io.BufferedReader(stream), encoding="utf-8")
            self._own_stream = True
        elif path:
            self._reader = open(path, 'r', encoding='utf-8')
            self._own_stream = False
        else:
            raise ValueError("One of reader, stream, or path must be provided.")

    def read(self, culture):
        stemming_rule_set = StemmingRuleSet(culture)
        stemming_rule_parser = StemmingRuleParser(stemming_rule_set)

        for line in self._reader:
            line = line.decode('utf-8').strip()
            line = ''.join(char for char in line if char.isprintable())
            if not line.startswith('#') and len(line) != 0:
                stemming_rule_parser.add(line)

        self.close()
        return stemming_rule_set

    def close(self):
        if self._own_stream and self._reader is not None:
            self._reader.close()
        self._reader = None
        self._own_stream = False

    def __del__(self):
        self.close()

    @staticmethod
    def read_static(path, culture):
        with StemmingRuleSetReader(path=path) as reader:
            return reader.read(culture)
