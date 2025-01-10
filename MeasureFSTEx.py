from typing import Dict, Optional
from CustomUnitDefinition import CustomUnitDefinition, Unit


class MeasureFSTEx:
    CURRENT_VERSION = 1

    def __init__(self):
        self.version = 1
        self.unit_definitions: Optional[Dict[str, CustomUnitDefinition]] = None

    @staticmethod
    def from_binary(data: bytes) -> 'MeasureFSTEx':
        data_str = data.decode('utf-8')
        lines = data_str.split('\r')
        lines = [line for line in lines if line.strip()]

        if len(lines) == 0:
            return MeasureFSTEx()

        try:
            version = int(lines[0])
        except ValueError:
            raise Exception("Unexpected data during MeasureFSTEx deserialization")

        if version > 1:
            raise Exception(f"Unexpected MeasureFSTEx version: {version}")

        lines = lines[1:]
        unit_definitions = {}

        for line in lines:
            parts = [part.strip() for part in line.split('\t') if part.strip()]

            if len(parts) == 0 or len(parts) >= 4:
                raise Exception("Unexpected custom unit serialization format")

            name = parts[0]
            category_name = None
            unit_str = None

            if len(parts) > 1:
                unit_str = parts[1]

            if len(parts) > 2:
                category_name = parts[2]

            custom_unit_definition = None
            if unit_str:
                try:
                    unit = Unit[unit_str]
                except KeyError:
                    raise Exception(f"Unexpected custom unit serialization type: {unit_str}")

                custom_unit_definition = CustomUnitDefinition(unit=unit, category_name=category_name)
                if custom_unit_definition.category_name and custom_unit_definition.unit != Unit.NoUnit:
                    raise Exception(
                        f"Unexpected category name in custom unit data for unit {parts[0]} of type {unit_str}")

            unit_definitions[name] = custom_unit_definition

        instance = MeasureFSTEx()
        instance.unit_definitions = unit_definitions
        instance.version = version
        return instance

    def to_binary(self) -> bytes:
        result = []

        if self.unit_definitions and len(self.unit_definitions) > 0:
            result.append(str(self.CURRENT_VERSION))

            for name, definition in self.unit_definitions.items():
                line = [name]
                if definition:
                    line.append(definition.unit.name)
                    line.append(definition.category_name or "")
                result.append("\t".join(line))

        return "\r".join(result).encode('utf-8')
