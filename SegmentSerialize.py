import struct, io
from typing import List, Optional
from Tag import *
from Text import *
from Segment import *

class SegmentSerializer:
    """Serializer for segment objects."""

    @staticmethod
    def read_string_or_null(reader):
        """Reads a string from binary data or returns None."""
        if struct.unpack('?', reader.read(1))[0]:  # Reads the boolean value (1 byte)
            return reader.read().decode('utf-8')
        return None

    @staticmethod
    def write_string_or_null(s, writer):
        """Writes a string to binary data, or null if the string is None."""
        if s is None:
            writer.write(struct.pack('?', False))  # False means None
        else:
            writer.write(struct.pack('?', True))  # True means not None
            writer.write(s.encode('utf-8'))

    @staticmethod
    def save(segment, binary_data: List[bytearray]):
        """Saves the segment to binary data."""
        flag = True
        result = SegmentSerializer.save_internal(segment, binary_data, flag)
        if not flag:
            result = SegmentSerializer.save_internal(segment, binary_data, flag)
        return result

    @staticmethod
    def write_int_as_sbyte(writer, i):
        """Write an int as signed byte."""
        if i < -128 or i > 127:
            return False
        writer.write(struct.pack('b', i))  # 'b' is format for signed byte
        return True

    @staticmethod
    def write_uint_as_byte(writer, i):
        """Write an unsigned int as byte."""
        if i > 255:
            return False
        writer.write(struct.pack('B', i))  # 'B' is format for unsigned byte
        return True

    @staticmethod
    def write_unsigned_int(writer, i, compact_serialization):
        """Write unsigned int with possible compact serialization."""
        if compact_serialization:
            return SegmentSerializer.write_uint_as_byte(writer, i)
        writer.write(struct.pack('I', i))  # 'I' is format for unsigned int
        return True

    @staticmethod
    def write_int(writer, i, compact_serialization):
        """Write int with possible compact serialization."""
        if compact_serialization:
            return SegmentSerializer.write_int_as_sbyte(writer, i)
        writer.write(struct.pack('i', i))  # 'i' is format for signed int
        return True

    @staticmethod
    def save_internal(segment, binary_data, compact_serialization):
        """Internal function to save the segment."""
        binary_data.clear()
        if not segment.elements:
            return None

        num = 0
        num2 = 0
        string_builder = []
        num3 = len([e for e in segment.elements if isinstance(e, Tag)])

        if num3 > 0:
            with bytearray() as memory_stream:
                serialization_version = 1 if compact_serialization else 2  # Version 1 or 2
                with memory_stream:
                    writer = memory_stream
                    writer.write(struct.pack('B', serialization_version))
                    if not SegmentSerializer.write_int(writer, num3, compact_serialization):
                        compact_serialization = False
                        return None
                    for segment_element in segment.elements:
                        if isinstance(segment_element, Text):
                            num += len(segment_element.value)
                            string_builder.append(segment_element.value)
                        elif isinstance(segment_element, Tag):
                            if writer:
                                writer.write(struct.pack('B', num - num2))
                                num2 = num
                                writer.write(struct.pack('B', segment_element.type))
                                if not SegmentSerializer.write_int(writer, segment_element.anchor,
                                                                   compact_serialization):
                                    compact_serialization = False
                                    return None
                                if segment_element.type != TagType.End:
                                    if not SegmentSerializer.write_int(writer, segment_element.alignment_anchor,
                                                                       compact_serialization):
                                        compact_serialization = False
                                        return None
                                SegmentSerializer.write_string_or_null(segment_element.tagid, writer)
                                if segment_element.type in [TagType.TextPlaceholder, TagType.LockedContent]:
                                    SegmentSerializer.write_string_or_null(segment_element.text_equivalent, writer)
                                writer.write(struct.pack('?', segment_element.canhide))  # CanHide is a boolean
                binary_data.append(memory_stream)
                return ''.join(string_builder)
        return ''.join(string_builder)

    @staticmethod
    def read_int(reader, compact_serialization):
        """Reads an int, handling compact serialization if necessary."""
        if compact_serialization:
            return struct.unpack('b', reader.read(1))[0]  # 'b' is for signed byte
        return struct.unpack('i', reader.read(4))[0]  # 'i' is for signed int

    @staticmethod
    def read_unsigned_int(reader, compact_serialization):
        """Reads an unsigned int, handling compact serialization if necessary."""
        if compact_serialization:
            return struct.unpack('B', reader.read(1))[0]  # 'B' is for unsigned byte
        return struct.unpack('I', reader.read(4))[0]  # 'I' is for unsigned int

    @staticmethod
    def load(text, binary_data, culture):
        """Load segment from text and binary data."""
        segment = Segment(culture)
        if binary_data is None:
            if text is None:
                return segment
            segment.add(Text(text))
            return segment

        num = 0
        with io.BytesIO(binary_data) as memory_stream:  # Replacing MemoryStream with io.BytesIO
            reader = memory_stream
            b = struct.unpack('B', reader.read(1))[0]
            serialization_version = 1 if b == 1 else 2  # Version 1 or 2

            compact_serialization = serialization_version == 1
            for i in range(SegmentSerializer.read_int(reader, compact_serialization)):
                num2 = SegmentSerializer.read_unsigned_int(reader, compact_serialization)
                num3 = num + num2
                b2 = struct.unpack('B', reader.read(1))[0]
                anchor = SegmentSerializer.read_int(reader, compact_serialization)
                alignment_anchor = 0
                if b2 != 2:
                    alignment_anchor = SegmentSerializer.read_int(reader, compact_serialization)
                tag_id = SegmentSerializer.read_string_or_null(reader)
                tag = Tag(b2, tag_id, anchor)
                if b2 != 2:
                    tag.alignment_anchor = alignment_anchor
                if b2 == TagType.TextPlaceholder or b2 == TagType.LockedContent:
                    tag.text_equivalent = SegmentSerializer.read_string_or_null(reader)
                tag.can_hide = struct.unpack('?', reader.read(1))[0]
                if text and num3 > num:
                    segment.add(Text(text[num:num3]))
                num = num3
                segment.add(tag)
        if text and num < len(text):
            segment.add(Text(text[num:]))
        return segment


class SegmentSerialization:
    """Handles serialization and deserialization of segments."""

    # Current version of serialization
    CurrentSerializationVersion = 1

    @staticmethod
    def save(segment, storage_segment):
        """
        Saves a segment into the storage segment (serialization).

        Args:
            segment (Segment): The segment object to serialize.
            storage_segment (StorageSegment): The storage segment where serialized data will be stored.
        """
        # Clear previous data
        storage_segment.text = None
        storage_segment.serialized_tags = None

        # List to hold binary data
        binary_data = []

        # Serialize the segment and store the text and tags
        storage_segment.text = SegmentSerializer.save(segment, binary_data)
        if binary_data:
            storage_segment.serialized_tags = bytes(binary_data)

    @staticmethod
    def load(storage_segment, culture):
        """
        Loads a segment from the storage segment (deserialization).

        Args:
            storage_segment (StorageSegment): The storage segment containing serialized data.
            culture (str): The culture associated with the segment.

        Returns:
            Segment: The deserialized segment.
        """
        return SegmentSerializer.load(storage_segment.text, storage_segment.serialized_tags, culture)
