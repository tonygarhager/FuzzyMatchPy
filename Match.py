from dataclasses import dataclass

@dataclass
class Match:
    index: int
    length: int

@dataclass
class FSTMatch(Match):
    output: str