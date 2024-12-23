from TokenizerParameters import TokenizerParameters
from Segment import Segment
from Tag import Tag
from Token import Token
from SegmentRange import SegmentRange
from Text import Text

class Tokenizer:
    def __init__(self, parameters: TokenizerParameters):
        self.parameters = parameters

    def tokenize(self, s, allow_token_bundles):
        return self.get_tokens(s, allow_token_bundles, True)

    def get_tokens(self, s:Segment, allow_token_bundles, enhanced_asian):
        list = []
        num = -1

        for segment_element in s.elements:
            num += 1
            if not segment_element:
                continue

            if isinstance(segment_element, Tag):
                pass#mod
            elif isinstance(segment_element, Token):
                fro = {}
                fro['index'] = num
                fro['position'] = 0
                into = {}
                into['index'] = num
                into['position'] = 0
                segment_element.span = SegmentRange(fro, into)
                segment_element.culture_name = self.parameters.culture_name
                list.append(segment_element)
            elif isinstance(segment_element, Text):
                list2 = self.tokenize_internal(segment_element.value, num, self.parameters.create_whitespace_tokens, allow_token_bundles, self.get_filtered_recognizers(segment_element.value))

                if enhanced_asian:
                    list2 = self.get_advanced_tokens(list2)
                if not list2 and len(list2) > 0:
                    list.extend(list2)

        self.reclassify_achronyms(list, enhanced_asian)
        self.adjust_number_range_tokenization(list)
        return list



