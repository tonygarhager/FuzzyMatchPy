from typing import List, Dict, Optional, Iterator

from EditDistance import EditOperation
from PairedTag import PairedTag

class TagAssociation:
    def __init__(self, source_tag: PairedTag, target_tag: PairedTag, operation: EditOperation = EditOperation.Undefined):
        self.source_tag: PairedTag = source_tag
        self.target_tag: PairedTag = target_tag
        self.operation: EditOperation = operation

    def __str__(self) -> str:
        source_str = str(self.source_tag) if self.source_tag else "(null)"
        target_str = str(self.target_tag) if self.target_tag else "(null)"
        return f"{source_str} <-> {target_str}, {self.operation}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TagAssociation):
            return False

        return (
            self.operation == other.operation
            and (self.source_tag == other.source_tag if self.source_tag else other.source_tag is None)
            and (self.target_tag == other.target_tag if self.target_tag else other.target_tag is None)
        )

    def __hash__(self) -> int:
        return hash((self.source_tag, self.target_tag, self.operation))

class TagAssociations:
    def __init__(self):
        self._associations: List[TagAssociation] = []
        self._src_position_idx: Dict[int, int] = {}
        self._trg_position_idx: Dict[int, int] = {}

    def __len__(self) -> int:
        return len(self._associations)

    def __getitem__(self, index: int) -> TagAssociation:
        return self._associations[index]

    def add(self, src_tag: Optional[PairedTag], trg_tag: Optional[PairedTag], op: EditOperation = EditOperation.Undefined):
        if op == EditOperation.Undefined:
            if src_tag is None:
                op = EditOperation.Insert
            elif trg_tag is None:
                op = EditOperation.Delete
            else:
                op = EditOperation.Change

        index = len(self._associations)
        self._associations.append(TagAssociation(src_tag, trg_tag, op))

        if src_tag is not None:
            self._src_position_idx[src_tag.start] = index
            self._src_position_idx[src_tag.end] = index

        if trg_tag is not None:
            self._trg_position_idx[trg_tag.start] = index
            self._trg_position_idx[trg_tag.end] = index

    def are_associated(self, source_position: int, target_position: int) -> bool:
        association = self.get_by_source_position(source_position)
        return (
            association is not None
            and association.target_tag is not None
            and (
                association.target_tag.start == target_position
                or association.target_tag.end == target_position
            )
        )

    def get_by_source_position(self, position: int) -> Optional[TagAssociation]:
        index = self._src_position_idx.get(position)
        return self._associations[index] if index is not None else None

    def get_operation_by_source_position(self, position: int) -> EditOperation:
        index = self._src_position_idx.get(position)
        return self._associations[index].operation if index is not None else EditOperation.Undefined

    def get_by_target_position(self, position: int) -> Optional[TagAssociation]:
        index = self._trg_position_idx.get(position)
        return self._associations[index] if index is not None else None

    def get_operation_by_target_position(self, position: int) -> EditOperation:
        index = self._trg_position_idx.get(position)
        return self._associations[index].operation if index is not None else EditOperation.Undefined

    def __iter__(self) -> Iterator[TagAssociation]:
        return iter(self._associations)
