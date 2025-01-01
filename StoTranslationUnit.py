from datetime import datetime
from typing import List, Optional
from StoSegment import StoSegment
from TuContext import *

class StoTranslationUnit:
    def __init__(
        self,
        id: int,
        guid: str,
        tm_id: int,
        source: StoSegment,
        target: StoSegment,
        creation_date: datetime,
        creation_user: str,
        change_date: datetime,
        change_user: str,
        last_used_date: datetime,
        last_used_user: str,
        usage_counter: int,
        flags: int,
        source_token_data: Optional[bytes] = None,
        target_token_data: Optional[bytes] = None,
        alignment_data: Optional[bytes] = None,
        align_model_date: Optional[datetime] = None,
        insert_date: Optional[datetime] = None,
        serialization_version: int = 0,
        format: Optional[str] = None,
        origin: Optional[str] = None,
        confirmation_level: Optional[str] = None,
    ):
        self.id = id
        self.tm_id = tm_id
        self.guid = guid
        self.source = source
        self.target = target
        self.creation_date = self.normalize_date(creation_date)
        self.creation_user = creation_user
        self.change_date = self.normalize_date(change_date)
        self.change_user = change_user
        self.last_used_date = self.normalize_date(last_used_date)
        self.last_used_user = last_used_user
        self.usage_counter = usage_counter
        self.flags = flags
        self.source_token_data = source_token_data
        self.target_token_data = target_token_data
        self.alignment_data = alignment_data
        self.align_model_date = align_model_date
        self.insert_date = insert_date
        self.serialization_version = serialization_version
        self.format = format
        self.origin = origin
        self.confirmation_level = confirmation_level
        self.attributes = []
        self.contexts = TuContexts()
        self.id_contexts = TuIdContexts()

    @staticmethod
    def normalize_date(date: datetime) -> datetime:
        return date.replace(microsecond=0)

    def add_context(self, left_source: Optional[int] = None, left_target: Optional[int] = None):
        if left_source is not None and left_target is not None:
            context = {"left_source": left_source, "left_target": left_target}
            return self.contexts.add(context)
        return False

    def add_id_context(self, id_context: str):
        return self.id_contexts.add(id_context)

    def compare(self, other):
        if not isinstance(other, StoTranslationUnit):
            raise TypeError("Can only compare with another StoTranslationUnit")
        return self.id - other.id if self.id and other.id else 0

