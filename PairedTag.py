from EditDistance import EditOperation


class PairedTag:
    def __init__(self, start: int, end: int, anchor: int):
        self.start: int = start
        self.end: int = end
        self.anchor: int = anchor
        self.start_tag_operation: EditOperation = EditOperation.Undefined
        self.end_tag_operation: EditOperation = EditOperation.Undefined

    def __str__(self) -> str:
        return f"({self.start},{self.end};i={self.anchor})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PairedTag):
            return False

        return (
            self.start == other.start
            and self.end == other.end
            and self.anchor == other.anchor
        )

    def __hash__(self) -> int:
        return hash((self.start, self.end, self.anchor))