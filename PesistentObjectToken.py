
import uuid

class PersistentObjectToken:
    def __init__(self, id=0, guid=None):
        if guid is None:
            guid = uuid.UUID(int=0)  # Default to empty GUID if not provided
        self.id = id
        self.guid = guid

    @property
    def Id(self):
        return self._id

    @Id.setter
    def Id(self, value):
        self._id = value

    @property
    def Guid(self):
        return self._guid

    @Guid.setter
    def Guid(self, value):
        self._guid = value

    def __eq__(self, other):
        if not isinstance(other, PersistentObjectToken):
            return False
        return self.id == other.id and self.guid == other.guid

    def __hash__(self):
        return hash((self.guid, self.id))

    def __str__(self):
        return f"({self.id}, {self.guid})"