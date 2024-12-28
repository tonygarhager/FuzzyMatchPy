import struct
from enum import Enum

from lxml.html.diff import tag_token

from NumberToken import *
from Tag import Tag
from TagToken import TagToken
from Token import *
from DateTimeRecognizer import *
import datetime
from DateTimeToken import *
from SimpleToken import *

class TokenClass(Enum):
    DateTimeToken = 1
    NumberToken = 2
    MeasureToken = 3
    SimpleToken = 4
    TagToken = 5
    GenericPlaceableToken = 6


class MemoryStream:
    def __init__(self, data: bytes):
        # Initialize with a byte buffer (data)
        self.stream = io.BytesIO(data)

    def read(self, size: int) -> bytes:
        # Read 'size' bytes from the stream
        return self.stream.read(size)

    def seek(self, offset: int, whence: int = io.SEEK_SET):
        # Move the stream position to 'offset'
        self.stream.seek(offset, whence)

    def tell(self) -> int:
        # Return the current position in the stream
        return self.stream.tell()

    def length(self) -> int:
        # Return the total length of the stream
        current_pos = self.stream.tell()
        self.stream.seek(0, io.SEEK_END)
        length = self.stream.tell()
        self.stream.seek(current_pos, io.SEEK_SET)
        return length


class BinaryReader:
    def __init__(self, stream: MemoryStream):
        self.stream = stream

    def read_byte(self) -> int:
        # Read a single byte
        return ord(self.stream.read(1))

    def read_sbyte(self) -> int:
        # Read a signed byte
        return struct.unpack('<b', self.stream.read(1))[0]

    def read_short(self) -> int:
        # Read a 2-byte short (little-endian)
        return struct.unpack('<h', self.stream.read(2))[0]

    def read_int(self) -> int:
        # Read a 4-byte integer (little-endian)
        return struct.unpack('<i', self.stream.read(4))[0]

    def read_long(self) -> int:
        # Read an 8-byte long (little-endian)
        return struct.unpack('<q', self.stream.read(8))[0]

    def read_string(self, length: int) -> str:
        # Read a string of 'length' bytes and decode it
        return self.stream.read(length).decode('utf-8')

    def read_string_with_length_prefix(self) -> str:
        # Read a string with a length prefix (1 byte indicating string length)
        length = self.read_byte()
        return self.read_string(length)

    def read_bytes(self, length: int) -> bytes:
        # Read a specific number of bytes
        return self.stream.read(length)

    def read_boolean(self) -> bool:
        # Read a single boolean value (0 or 1 byte)
        return self.read_byte() == 1

    def read_float(self) -> float:
        # Read a 4-byte float (little-endian)
        return struct.unpack('<f', self.stream.read(4))[0]

    def read_double(self) -> float:
        # Read an 8-byte double (little-endian)
        return struct.unpack('<d', self.stream.read(8))[0]

class TokenSerialization:

    @staticmethod
    def my_assert(test):
        if not test:
            raise Exception("Serialization debug check failure")

    @staticmethod
    def load_tokens(data, segment):
        if not TokenSerialization.use_token_serialization:
            return None
        if data is None:
            return None
        result = []
        with io.BytesIO(data) as binary_reader:
            result = TokenSerialization.load_tokens_from_reader(binary_reader, segment)
        return result

    @staticmethod
    def load_tokens_from_reader(reader, segment):
        return TokenSerialization.TokenDeserializer(reader, segment).deserialize()

    use_token_serialization = True

    _token_type_to_token_class_map = {
        TokenType.Word: TokenClass.SimpleToken,
        TokenType.Whitespace: TokenClass.SimpleToken,
        TokenType.Measurement: TokenClass.MeasureToken,
        TokenType.GeneralPunctuation: TokenClass.SimpleToken,
        TokenType.OpeningPunctuation: TokenClass.SimpleToken,
        TokenType.ClosingPunctuation: TokenClass.SimpleToken,
        TokenType.Number: TokenClass.NumberToken,
        TokenType.Tag: TokenClass.TagToken,
        TokenType.AlphaNumeric: TokenClass.SimpleToken,
        TokenType.Time: TokenClass.DateTimeToken,
        TokenType.Abbreviation: TokenClass.SimpleToken,
        TokenType.Acronym: TokenClass.SimpleToken,
        TokenType.Variable: TokenClass.SimpleToken,
        TokenType.UserDefined: TokenClass.SimpleToken,
        TokenType.Uri: TokenClass.SimpleToken,
        TokenType.Date: TokenClass.DateTimeToken,
        TokenType.OtherTextPlaceable: TokenClass.GenericPlaceableToken,
        TokenType.CharSequence: TokenClass.SimpleToken
    }

    TokenTypeSingleCharFlag = 32
    TokenTypeStopWordFlag = 64
    TokenTypeStandardPlacementFlag = 128

    class TokenSerializer:
        def __init__(self, writer, segment, compact_serialization=True):
            if writer is None:
                raise ValueError("writer cannot be None")
            self._writer = writer
            if segment is None:
                raise ValueError("segment cannot be None")
            self._segment = segment
            self._compact_serialization = compact_serialization

            # This assumes segment.Tokens is a list of tokens
            for token in segment.tokens:
                if token.span.from_index != token.span.into_index:
                    self.unable_to_serialize = True
                    raise Exception("Span.From.Index != Span.To.Index")
                if token.span.from_index >= len(segment.elements):
                    raise Exception("t.Span.From.Index >= segment.Elements.Count")

        @staticmethod
        def get_tokens_of_type(tokens, token_type):
            return [x for x in tokens if isinstance(x, token_type)]

        def visit_text(self, text):
            raise Exception("Unexpected Text in SaveTokens")

        def visit_tag(self, tag):
            raise Exception("Unexpected Tag in SaveTokens")

        def read_text_and_span(self, token, token_has_standard_placement, previous_token, token_is_single_char):
            pass

        def unable_to_serialize(self):
            return False

    class TokenDeserializer:
        def __init__(self, reader, segment):
            if reader is None:
                raise ValueError("reader cannot be None")
            self._reader = reader
            if segment is None:
                raise ValueError("segment cannot be None")
            self._segment = segment

        def deserialize(self):
            serialization_version = struct.unpack("B", self._reader.read(1))[0]
            self.compact_serialization = serialization_version != 1

            list_tokens = []
            num = self.read_int_as_short()
            self._element_index_adjustment = 0
            for i in range(num):
                previous_token = list_tokens[i-1] if i > 0 else None
                token_has_standard_placement = False
                token_is_single_char = False
                num2 = struct.unpack("B", self._reader.read(1))[0]
                is_stopword = False

                if num2 & TokenSerialization.TokenTypeStopWordFlag:
                    is_stopword = True
                    num2 -= TokenSerialization.TokenTypeStopWordFlag

                if num2 & TokenSerialization.TokenTypeSingleCharFlag:
                    num2 -= TokenSerialization.TokenTypeSingleCharFlag
                    token_is_single_char = True

                if num2 & TokenSerialization.TokenTypeStandardPlacementFlag:
                    num2 -= TokenSerialization.TokenTypeStandardPlacementFlag
                    token_has_standard_placement = True

                token_type = num2
                token_class = TokenSerialization._token_type_to_token_class_map.get(token_type)

                if token_class is None:
                    raise Exception(f"Unknown TokenType during deserialization: {token_type}")

                if token_class == TokenClass.DateTimeToken:
                    list_tokens.append(self.read_date_time_token(token_type, token_has_standard_placement, previous_token, token_is_single_char))
                elif token_class == TokenClass.NumberToken:
                    list_tokens.append(self.read_number_token(token_type, token_has_standard_placement, previous_token, token_is_single_char))
                elif token_class == TokenClass.MeasureToken:
                    list_tokens.append(self.read_measure_token(token_type, token_has_standard_placement, previous_token, token_is_single_char))
                elif token_class == TokenClass.SimpleToken:
                    simple_token = self.read_simple_token(False, token_type, token_has_standard_placement, previous_token, token_is_single_char)
                    simple_token.is_stopword = is_stopword
                    list_tokens.append(simple_token)
                elif token_class == TokenClass.TagToken:
                    list_tokens.append(self.read_tag_token(token_type))
                elif token_class == TokenClass.GenericPlaceableToken:
                    list_tokens.append(self.read_simple_token(True, token_type, token_has_standard_placement, previous_token, token_is_single_char))
                else:
                    raise Exception(f"Unexpected TokenClass in LoadTokens: {token_class}")
            self.read_additional_data_if_present(list_tokens)

            for token in list_tokens:
                token.culture_name = self._segment.culture_name
            return list_tokens

        def read_additional_data_if_present(self, tokens):
            self.read_measure_categories_and_datetime_formats_if_present(tokens)

        def read_measure_categories_and_datetime_formats_if_present(self, tokens):
            return#mod

        def read_byte(self):
            return struct.unpack("B", self._reader.read(1))[0]
        def read_short(self):
            return struct.unpack("h", self._reader.read(2))[0]
        def read_int(self):
            return struct.unpack('i', self._reader.read(4))[0]

        def read_int_as_short(self):
            if self.compact_serialization:
                return self.read_short()
            return self.read_int()

        def read_int_as_byte(self) -> int:
            if self.compact_serialization:
                return self.read_byte()
            return self.read_int()

        def read_date_time_token(self, token_type, token_has_standard_placement, previous_token, token_is_single_char):
            # Read the DateTime pattern type (as a byte, assuming it's a byte-based enum)
            pattern_type_value = self.read_int_as_byte()
            pattern_type = DateTimePatternType(pattern_type_value)

            # Read the DateTime value (as 64-bit integer - similar to C#)
            date_time_binary = struct.unpack('<q', self._reader.read(8))[0]
            date_time = datetime.fromtimestamp(date_time_binary)

            # Read a SimpleToken to build the DateTimeToken
            simple_token = SimpleToken(self.read_string_or_null())
            # Apply any additional token properties
            self.read_token(simple_token, token_has_standard_placement, previous_token, token_is_single_char)

            # Create the DateTimeToken
            date_time_token = DateTimeToken(simple_token.text, date_time, pattern_type)
            date_time_token.type = token_type  # Set the token type

            return date_time_token

        def read_number_token(self, token_type, token_has_standard_placement, previous_token, token_is_single_char):
            sign:Sign = self.read_int_as_byte()
            raw_sign = self.read_string_or_null()
            decimal_separator = NumericSeparator(self.read_int_as_sbyte())
            group_separator = NumericSeparator(self.read_int_as_sbyte())
            alternate_group_separator = self._reader.read_char()
            alternate_decimal_separator = self._reader.read_char()
            raw_fractional_digits = self.read_string_or_null()
            raw_decimal_digits = self.read_string_or_null()

            simple_token = SimpleToken()
            self.read_token(simple_token, token_has_standard_placement, previous_token, token_is_single_char)

            number_token = NumberToken(
                simple_token.text,
                group_separator,
                decimal_separator,
                alternate_group_separator,
                alternate_decimal_separator,
                sign,
                raw_sign,
                raw_decimal_digits,
                raw_fractional_digits
            )

            # Assuming TokenSerialization.TokenDeserializer.CopyToken copies token data
            # Copy token details from simple_token to number_token (can be adapted as needed)
            TokenSerialization.TokenDeserializer.copy_token(simple_token, number_token)

            number_token.type = token_type
            return number_token

        def read_measure_token(self, token_type, token_has_standard_placement, previous_token, token_is_single_char):
            raise Exception("read_measure_token")

        def read_tag_token(self, token_type) -> TagToken:
            tag_token = TagToken()
            num = self.read_int_as_byte()
            num -= self._element_index_adjustment
            tag_token.tag = self.read_tag(num)
            tag_token.span = SegmentRange.create_3i(num, 0, 0)
            tag_token.text = str(tag_token.tag)
            tag_token.type = token_type
            return tag_token

        def read_tag(self, seg_elem_index:int) -> Tag:
            if len(self._segment.elements) <= seg_elem_index:
                raise Exception("Segment content incorrect: could not have produced the serialized Tag token")
            return self._segment.elements[seg_elem_index]

        def read_token(self, t:Token, token_has_standard_placement:bool, previous_token:Token, token_is_single_char:bool):
            self.read_text_and_span(t, token_has_standard_placement, previous_token, token_is_single_char)

        def read_text_and_span(self, token:Token, token_has_standard_placement:bool, previous_token:Token, token_is_single_char):
            if token_has_standard_placement:
                num = previous_token.span.fro.index
                num2 = previous_token.span.fro.position + previous_token.span.length
            else:
                num = self.read_int_as_byte()
                num -= self._element_index_adjustment
                num2 = self.read_int_as_short()
            num3 = 1 if token_is_single_char else self.read_int_as_byte()
            token.span = SegmentRange.create_3i(num, num2, num2 + num3 - 1)

            if (previous_token is not None and
                isinstance(token, TagToken) == False and
                isinstance(previous_token, TagToken) == False and
                token.span.fro.index == previous_token.span.fro.index + 1):
                text = self._segment.elements[previous_token.span.fro.index]
                if text is not None:
                    num4 = previous_token.span.fro.position + previous_token.span.length
                    if len(text.value) >= num4 + num3:
                        num2 = num4
                        token.span = SegmentRange.create_3i(previous_token.span.fro.index, num2, num2 + num3 - 1)
                        self._element_index_adjustment += 1
            if len(self._segment.elements) <= token.span.fro.index:
                raise Exception('Segment content incorrect: could not have produced the serialized Token')
            token.text = str(self._segment.elements[token.span.fro.index])[num2:num2 + num3]

        def read_simple_token(self, is_generic_placeable, token_type, token_has_standard_placement, previous_token, token_is_single_char):
            simple_token = SimpleToken()
            if is_generic_placeable:
                token_class = self.read_string()
                is_substitutable = self.read_boolean()
                simple_token = GenericPlaceableToken('', token_class, is_substitutable)
            self.read_token(simple_token, token_has_standard_placement, previous_token, token_is_single_char)
            simple_token.type = token_type
            return simple_token

