from Segment import Segment
from SegmentRange import SegmentRange
from Text import Text


class SegmentEditor:
    @staticmethod
    def clean_segment(segment):
        if segment.tokens is None:
            elements_list = list(segment.elements)
            segment.elements.clear()
            for element in elements_list:
                if element is not None:
                    text = element if isinstance(element, Text) else None
                    if text is None or text.value:
                        segment.add(element)
            return

        tokens_list = [token for token in segment.tokens if token is not None]
        segment.elements.clear()
        segment.tokens.clear()
        SegmentEditor.insert_tokens(segment, tokens_list, 0)

    @staticmethod
    def change_tokens(segment, tokens, start_token_index, length):
        SegmentEditor.validate_args(segment, start_token_index)
        if start_token_index >= len(segment.tokens):
            raise Exception("start_token_index >= proposal_target.tokens_count")
        if length < 1:
            raise Exception("length < 1")
        return SegmentEditor.delete_tokens(segment, start_token_index, length) and \
               SegmentEditor.insert_tokens(segment, tokens, start_token_index)

    @staticmethod
    def delete_tokens(segment, start_token_index, length):
        SegmentEditor.validate_args(segment, start_token_index)
        if start_token_index >= len(segment.tokens):
            raise Exception("start_token_index >= proposal_target.tokens_count")
        if length < 0:
            raise Exception("length < 0")
        if start_token_index + length > len(segment.tokens):
            raise Exception("(start_token_index + length) > segment.tokens_count")

        for _ in range(length):
            SegmentEditor.delete_token(segment, start_token_index)
        return True

    @staticmethod
    def delete_token(segment, token_index):
        token = segment.tokens[token_index]
        index = token.span.from_index
        text = segment.elements[index] if isinstance(segment.elements[index], Text) else None
        num = token.span.into_position - token.span.from_position + 1

        if text is None or (token.span.from_position == 0 and num == len(text.value)):
            segment.elements.pop(index)
            segment.tokens.pop(token_index)
            for i in range(token_index, len(segment.tokens)):
                segment.tokens[i].span.from_index -= 1
                segment.tokens[i].span.into_index -= 1
            return

        new_value = text.value[:token.span.from_position] + text.value[token.span.into_position + 1:]
        text.value = new_value
        segment.tokens.pop(token_index)

        for i in range(token_index, len(segment.tokens)):
            if segment.tokens[i].span.from_index == index:
                segment.tokens[i].span.from_position -= num
                segment.tokens[i].span.into_position -= num

    @staticmethod
    def validate_args(segment, start_token_index):
        if segment.tokens is None:
            raise ValueError("Tokens are None")
        if start_token_index < 0:
            raise IndexError("start_token_index < 0")

    @staticmethod
    def clone(other):
        segment = Segment(other.culture)
        for element in other.elements:
            segment.elements.append(element.duplicate() if element else None)

        if other.tokens is None:
            return segment

        segment.tokens = [token.duplicate() for token in other.tokens]
        return segment

    @staticmethod
    def append_tokens(segment, tokens):
        return SegmentEditor.insert_tokens(segment, tokens, len(segment.tokens))

    @staticmethod
    def insert_tokens(segment, tokens, start_token_index):
        return SegmentEditor.insert_tokens_internal(segment, tokens, start_token_index, None)

    @staticmethod
    def insert_tokens_internal(segment, tokens, start_token_index, tokens_inserted=None):
        SegmentEditor.validate_args(segment, start_token_index)
        if start_token_index > len(segment.tokens):
            raise Exception("start_token_index > proposal_target.tokens_count")

        tokens = [token.duplicate() for token in tokens]
        if tokens_inserted is not None:
            tokens_inserted.extend(tokens)

        new_text = "".join(token.text for token in tokens)
        if start_token_index == len(segment.tokens):
            segment.tokens.extend(tokens)
            segment.add(Text(new_text))
            index = len(segment.elements) - 1
            num = 0
            for i, token in enumerate(tokens):
                token.span = SegmentRange.create_3i(index, num, num + len(token.text) - 1)
                num += len(token.text)
        elif start_token_index == 0:
            segment.tokens = tokens + segment.tokens
            segment.elements.insert(0, Text(new_text))
            num2 = 0
            for i, token in enumerate(tokens):
                token.span = SegmentRange.create_3i(0, num2, num2 + len(token.text) - 1)
                num2 += len(token.text)
        else:
            segment.tokens[start_token_index:start_token_index] = tokens
            token4 = segment.tokens[start_token_index - 1]
            token5 = segment.tokens[start_token_index + len(tokens)]
            index2 = token5.span.from_index
            if token5.span.from_index != token5.span.into_index or token4.span.from_index != token4.span.into_index:
                return False

            if token4.span.into_index == index2:
                text = segment.elements[index2] if isinstance(segment.elements[index2], Text) else None
                if text is None:
                    return False

                new_value = ''#plmodtext.value[:token4.span.into_position + 1] + new_text + text.value[len(new_value):]
                text.value = new_value
                num3 = token4.span.into_position + 1
                for token in tokens:
                    token.span = SegmentRange(token4.span.into_index, num3, num3 + len(token.text) - 1)
                    num3 += len(token.text)
            else:
                segment.elements.insert(index2, Text(new_text))
                num5 = 0
                for token in tokens:
                    token.span = SegmentRange(index2, num5, num5 + len(token.text) - 1)
                    num5 += len(token.text)
                for i in range(start_token_index + len(tokens), len(segment.tokens)):
                    segment.tokens[i].span.from_position += len(new_text)
                    segment.tokens[i].span.into_position += len(new_text)
        return True
