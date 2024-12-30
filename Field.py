from enum import Enum
from typing import List, Optional, Union
from abc import ABC, abstractmethod
from ErrorCode import ErrorCode
from datetime import datetime, timedelta

class FieldValueType(Enum):
    SINGLE_STRING = "SingleString"
    MULTIPLE_STRING = "MultipleString"
    DATE_TIME = "DateTime"
    SINGLE_PICKLIST = "SinglePicklist"
    MULTIPLE_PICKLIST = "MultiplePicklist"
    INTEGER = "Integer"
    UNKNOWN = "Unknown"


class FieldType(Enum):
    USER = "User"
    SYSTEM = "System"
    PSEUDO = "Pseudo"


class LanguagePlatformException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Field:
    # Special fields container
    _special_fields = []

    # Constants
    STRUCTURE_CONTEXT_FIELD_NAME = "StructureContext"
    TEXT_CONTEXT_FIELD_NAME = "TextContext"

    def __init__(self, name: str = "", value_type: FieldValueType = FieldValueType.UNKNOWN, field_type: FieldType = FieldType.USER):
        self.name = name
        self.value_type = value_type
        self.field_type = field_type

    @staticmethod
    def is_valid_name(name: str) -> bool:
        return bool(name and not name.isspace() and not name[0].isspace() and not name[-1].isspace())

    @staticmethod
    def remove_illegal_chars(value: str) -> str:
        if not value:
            raise ValueError("Value cannot be null or empty.")
        return value.strip()

    @staticmethod
    def lookup_special_field(name: str) -> Optional['Field']:
        for field in Field._special_fields:
            if field.name.lower() == name.lower():
                return field
        return None

    @staticmethod
    def get_field_type(name: str) -> FieldType:
        if not name:
            raise LanguagePlatformException("Invalid field name.")
        field = Field.lookup_special_field(name.strip())
        return field.field_type if field else FieldType.USER

    def equals_declaration(self, other: 'Field') -> bool:
        return self.value_type == other.value_type and self.name.lower() == other.name.lower()

    def create_value(self):
        if self.value_type == FieldValueType.SINGLE_STRING:
            return SingleStringFieldValue(self.name)
        elif self.value_type == FieldValueType.MULTIPLE_STRING:
            return MultipleStringFieldValue(self.name)
        elif self.value_type == FieldValueType.DATE_TIME:
            return DateTimeFieldValue(self.name)
        elif self.value_type == FieldValueType.SINGLE_PICKLIST:
            return SinglePicklistFieldValue(self.name)
        elif self.value_type == FieldValueType.MULTIPLE_PICKLIST:
            return MultiplePicklistFieldValue(self.name)
        elif self.value_type == FieldValueType.INTEGER:
            return IntFieldValue(self.name)
        else:
            return None

    def clone(self):
        return Field(self.name, self.value_type, self.field_type)


class FieldValue(ABC):
    def __init__(self, name: str = ""):
        self._name = None
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not Field.is_valid_name(value):
            raise LanguagePlatformException(ErrorCode.TMInvalidFieldName)
        self._name = value

    @property
    def value_type(self) -> FieldValueType:
        pass

    @value_type.setter
    def value_type(self, value: FieldValueType):
        pass

    @abstractmethod
    def merge(self, rhs: 'FieldValue') -> bool:
        pass

    @abstractmethod
    def add(self, rhs: 'FieldValue') -> bool:
        pass

    @abstractmethod
    def subtract(self, rhs: 'FieldValue') -> bool:
        pass

    @abstractmethod
    def duplicate(self) -> 'FieldValue':
        pass

    @abstractmethod
    def parse(self, s: str):
        pass

    @abstractmethod
    def add_string(self, s: str) -> bool:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def get_value_string(self) -> str:
        pass

class IntFieldValue(FieldValue):
    def __init__(self, name: str, value: Optional[int] = 0):
        super().__init__(name)
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IntFieldValue):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.name, self.value))

    def merge(self, rhs: 'FieldValue') -> bool:
        if not isinstance(rhs, IntFieldValue):
            return False
        if self != rhs:
            self.value = rhs.value
            return True
        return False

    def add(self, rhs: 'FieldValue') -> bool:
        if isinstance(rhs, IntFieldValue):
            self.value += rhs.value
            return True
        return False

    def subtract(self, rhs: 'FieldValue') -> bool:
        if isinstance(rhs, IntFieldValue):
            self.value -= rhs.value
            return True
        return False

    def duplicate(self) -> 'IntFieldValue':
        return IntFieldValue(self.name, self.value)

    def get_value_string(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def parse(self, s: str):
        self.value = int(s)

    def clear(self):
        self.value = 0

class MultiplePicklistFieldValue(FieldValue):
    def __init__(self, name=None, values=None):
        super().__init__(name)
        self.values = values if values is not None else []

    def __copy__(self):
        return MultiplePicklistFieldValue(self.name, list(self.values))

    def add(self, v):
        if self.has_value(v):
            return False
        self.values.append(v)
        return True

    def has_value(self, v):
        return self.has_value_by_name(v.name) if isinstance(v, PicklistItem) else False

    def has_value_by_name(self, name):
        if not name:
            raise ValueError("Name cannot be null or empty")
        return any(item.name.lower() == name.lower() for item in self.values)

    def has_values(self, other):
        if not isinstance(other, MultiplePicklistFieldValue):
            return False
        return all(self.has_value(v) for v in other.values)

    def remove(self, v):
        if not isinstance(v, PicklistItem):
            raise ValueError("v must be a PicklistItem")
        return self.remove_by_name(v.name)

    def remove_by_name(self, name):
        if not name:
            raise ValueError("Name cannot be null or empty")
        for i, item in enumerate(self.values):
            if item.name.lower() == name.lower():
                del self.values[i]
                return True
        return False

    def get_value_string(self):
        return f"({', '.join([f'\"{self.escape_string(item.name)}\"' for item in self.values])})"

    @property
    def value_type(self):
        return FieldValueType.MULTIPLE_PICKLIST

    def __eq__(self, other):
        if not isinstance(other, MultiplePicklistFieldValue):
            return False
        if not self.values or not other.values:
            return self.values == other.values
        return len(self.values) == len(other.values) and all(self.has_value(v) for v in other.values)

    def __hash__(self):
        return hash(self.name)

    def merge(self, rhs):
        if not isinstance(rhs, MultiplePicklistFieldValue):
            raise LanguagePlatformException(ErrorCode.EditScriptIncompatibleFieldValueTypes)
        flag = False
        for item in rhs.values:
            flag |= self.add(item)
        return flag

    def add_field_value(self, rhs):
        return self.merge(rhs)

    def subtract(self, rhs):
        if not isinstance(rhs, MultiplePicklistFieldValue):
            raise LanguagePlatformException(ErrorCode.EditScriptIncompatibleFieldValueTypes)
        flag = False
        for item in rhs.values:
            flag |= self.remove_by_name(item.name)
        return flag

    def duplicate(self):
        return MultiplePicklistFieldValue(self.name, list(self.values))

    def __str__(self):
        return ", ".join([item.name for item in self.values])

    def parse(self, s):
        pass

    def add_by_name(self, s):
        item = PicklistItem(name=s)
        return self.add(item)

    def clear(self):
        self.values.clear()

    def escape_string(self, s):
        return s.replace("\"", "\\\"")

class PicklistItem:
    def __init__(self, name=None, id=None):
        self.id = id
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, PicklistItem):
            return False
        return self.name.lower() == other.name.lower() if self.name and other.name else False

    def __hash__(self):
        return hash(self.name.lower()) if self.name else 0

    def __str__(self):
        return self.name if self.name else "None"

    def clone(self):
        return PicklistItem(self.name, self.id)

class SinglePicklistFieldValue:
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value  # Expecting a PicklistItem object

    @property
    def value_type(self):
        return 'SinglePicklist'

    def get_value_string(self):
        return f'"{self.value.name}"' if self.value else '""'

    def __eq__(self, other):
        if not isinstance(other, SinglePicklistFieldValue):
            return False
        if self.value is None or other.value is None:
            return self.value is other.value
        return self.value.name.lower() == other.value.name.lower()

    def __hash__(self):
        return hash(self.value.name.lower()) if self.value else 0

    def merge(self, rhs):
        if not isinstance(rhs, SinglePicklistFieldValue):
            raise ValueError("Can't compare different field types")
        if self == rhs:
            return False
        self.value = rhs.value
        return True

    def add(self, rhs):
        raise NotImplementedError("Invalid operation for SinglePicklistFieldValue")

    def subtract(self, rhs):
        raise NotImplementedError("Invalid operation for SinglePicklistFieldValue")

    def duplicate(self):
        return SinglePicklistFieldValue(self.name, self.value.clone() if self.value else None)

    def __str__(self):
        return self.value.name if self.value else "None"

    def parse(self, s):
        self.value = PicklistItem(s)

    def add_string(self, s):
        return False

    def clear(self):
        self.value = None

class DateTimeFieldValue:
    def __init__(self, name=None, value=None):
        self.name = name
        self._value = self._normalize(value) if value else datetime.min

    def _normalize(self, value):
        # Normalize the datetime to a consistent format (similar to DateTimeUtilities.Normalize)
        if value is None:
            return datetime.min
        return value.replace(tzinfo=None)  # Assuming UTC normalization for simplicity

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = self._normalize(v)

    @property
    def value_type(self):
        return 'DateTime'

    def __eq__(self, other):
        if not isinstance(other, DateTimeFieldValue):
            return False
        return self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def merge(self, rhs):
        if self == rhs:
            return False
        self._value = rhs._value
        return True

    def add(self, rhs):
        if not isinstance(rhs, DateTimeFieldValue):
            raise ValueError("Incompatible FieldValue types for addition")
        self._value += timedelta(seconds=rhs.value.second)
        return True

    def subtract(self, rhs):
        if not isinstance(rhs, DateTimeFieldValue):
            raise ValueError("Incompatible FieldValue types for subtraction")
        self._value -= timedelta(seconds=rhs.value.second)
        return True

    def duplicate(self):
        return DateTimeFieldValue(self.name, self._value)

    def get_value_string(self):
        return f'"{self._value.isoformat()}"'

    def __str__(self):
        return self._value.isoformat()

    def parse(self, s):
        self._value = datetime.fromisoformat(s)

    def add_string(self, s):
        return False

    def clear(self):
        self._value = datetime.min

class MultipleStringFieldValue(FieldValue):
    def __init__(self, name: str = "", values: List[str] = None):
        super().__init__(name)
        self._values = set()  # Set to store values, case-insensitive
        if values:
            for v in values:
                self.add(v)

    def __copy__(self):
        return MultipleStringFieldValue(self.name, list(self._values))

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value):
        self.clear()
        if value:
            for v in value:
                self.add(v)

    @property
    def count(self) -> int:
        return len(self._values)

    def get_value_string(self) -> str:
        return f"({', '.join([f'\"{self.escape_string(s)}\"' for s in self._values])})"

    def add(self, v: str) -> bool:
        if self._values is None:
            self._values = set()
        return self._values.add(v.lower()) is None

    def has_value(self, v: str) -> bool:
        if self._values is None:
            return False
        return any(v.lower() in value for value in self._values)

    def contains(self, v: str) -> bool:
        return self.has_value(v)

    def has_values(self, other: 'MultipleStringFieldValue') -> bool:
        return all(self.has_value(v) for v in other.values)

    def remove(self, v: str) -> bool:
        if self._values is None:
            return False
        return self._values.remove(v.lower())

    @property
    def value_type(self) -> FieldValueType:
        return FieldValueType.MULTIPLE_STRING

    @value_type.setter
    def value_type(self, value: FieldValueType):
        pass

    def merge(self, rhs: FieldValue) -> bool:
        if not isinstance(rhs, MultipleStringFieldValue):
            raise LanguagePlatformException(ErrorCode.EditScriptIncompatibleFieldValueTypes)
        flag = False
        for s in rhs._values:
            flag |= self.add(s)
        return flag

    def add_field_value(self, rhs: FieldValue) -> bool:
        return self.merge(rhs)

    def subtract(self, rhs: FieldValue) -> bool:
        if not isinstance(rhs, MultipleStringFieldValue):
            raise LanguagePlatformException(ErrorCode.EditScriptIncompatibleFieldValueTypes)
        flag = False
        for v in rhs._values:
            flag |= self.remove(v)
        return flag

    def duplicate(self):
        return MultipleStringFieldValue(self.name, list(self._values))

    def __str__(self) -> str:
        return ", ".join(self.values)

    def parse(self, s: str):
        # Implement logic for parsing a string into values if needed
        pass

    def clear(self):
        self._values.clear()

    def escape_string(self, value: str) -> str:
        # You may want to add an escape logic here
        return value.replace("\"", "\\\"")  # Example: Escape quotes

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MultipleStringFieldValue):
            return False
        return self._values == other._values

    def __hash__(self):
        return hash(frozenset(self._values))

class SingleStringFieldValue(FieldValue):
    def __init__(self, name: str = "", value: str = None):
        super().__init__(name)
        self.value = value

    @property
    def value_type(self):
        return FieldValueType.SINGLE_STRING

    @value_type.setter
    def value_type(self, value: FieldValueType):
        pass

    def merge(self, rhs: FieldValue) -> bool:
        if not isinstance(rhs, SingleStringFieldValue):
            return False
        if self == rhs:
            return False
        self.value = rhs.value
        return True

    def add(self, rhs: FieldValue) -> bool:
        raise LanguagePlatformException(ErrorCode.EditScriptInvalidOperationForFieldValueType)

    def subtract(self, rhs: FieldValue) -> bool:
        raise LanguagePlatformException(ErrorCode.EditScriptInvalidOperationForFieldValueType)

    def duplicate(self):
        return SingleStringFieldValue(self.name, self.value)

    def parse(self, s: str):
        self.value = s

    def add_string(self, s: str) -> bool:
        return False

    def clear(self):
        self.value = None

    def get_value_string(self) -> str:
        if not self.value:
            return "\"\""
        return f"\"{self.escape_string(self.value)}\""

    def escape_string(self, value: str) -> str:
        # You may want to add escaping logic here
        return value.replace("\"", "\\\"")  # Basic escaping example

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SingleStringFieldValue):
            return False
        return self.value.lower() == other.value.lower()

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.value

class FieldDefinitions:
    def __init__(self):
        self.fields = []

    def add_field(self, field: Field):
        if not isinstance(field, Field):
            raise TypeError("Only instances of Field can be added.")
        self.fields.append(field)

    def lookup(self, name: str) -> Optional[Field]:
        for field in self.fields:
            if field.name.lower() == name.lower():
                return field
        return None

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)

if __name__ == "__main__":
    fields = FieldDefinitions()
    # Initialize special fields (similar to C# static constructor logic)
    Field._special_fields = FieldDefinitions()
    Field._special_fields.add_field(Field(Field.STRUCTURE_CONTEXT_FIELD_NAME, FieldValueType.UNKNOWN, FieldType.SYSTEM))
    Field._special_fields.add_field(Field(Field.TEXT_CONTEXT_FIELD_NAME, FieldValueType.MULTIPLE_STRING, FieldType.SYSTEM))
    Field._special_fields.add_field(Field("chd", FieldValueType.DATE_TIME, FieldType.SYSTEM))
    Field._special_fields.add_field(Field("chu", FieldValueType.SINGLE_STRING, FieldType.SYSTEM))
    Field._special_fields.add_field(Field("src", FieldValueType.SINGLE_STRING, FieldType.PSEUDO))
