import re
import io

import unicodedata

from StringUtils import StringUtils


class SearchOption:
    none = 0
    case_insensitive = 1
    diacritic_insensitive = 2

class Wordlist:
    def __init__(self, _search_opt = SearchOption.none):
        self.flags = _search_opt
        self._init()

    def _init(self):
        self.words = []
        self.word_index = []

    def contains(self, s):
        return s is not None and s != '' and s in self.word_index

    def clear(self):
        self.words = []
        self.word_index = []

    def merge(self, other):
        self.words.extend(other.words)
        self.word_index.extend(other.words)

    @staticmethod
    def merge_list(word_lists):
        word_list = Wordlist()
        for wl in word_lists:
            word_list.merge(wl)
        return word_list

    def get_regular_expression(self):
        first = []
        flag = self.flags == SearchOption.case_insensitive
        self.words.sort(key=len, reverse=True)  # Sort by length descending
        regex_parts = []

        if flag:
            regex_parts.append("(?i-:")

        for word in self.words:
            if word and len(word) > 0:
                char = word[0]
                first.append(char)
                if flag:
                    upper_char = char.upper()
                    lower_char = char.lower()
                    if upper_char != char:
                        first.append(upper_char)
                    if lower_char != char and lower_char != upper_char:
                        first.append(lower_char)

                regex_parts.append(re.escape(word))

        if flag:
            regex_parts.append(")")

        return f"({'|'.join(regex_parts)})", first


    def count(self):
        return len(self.words)

    def add(self, s:str):
        if not s:  # Check if the string is None or empty
            return False
        if self.contains(s):  # Check if the string already exists
            return False
        self.words.append(s)  # Add to the collection
        self.word_index.append(s)  # Maintain index
        return True

    def remove(self, s):
        if not self.contains(s):  # Check if the string exists
            return False
        self.word_index.discard(s)  # Remove from word_index (no error if not found)
        self.words.discard(s)  # Remove from words (no error if not found)
        return True

    def load_internal(self, reader, ignore_comments):
        dictionary = {}
        flag = True
        for text in reader:
            text = StringUtils.remove_invisible_characters(text.decode('utf-8').strip())

            if flag and text.startswith('%version='):
                self.version = int(text[9:])
            flag = False
            if text.startswith('%'):
                if len(text) > 1:
                    text2 = text[1:].strip()

                    if text2.lower() == 'addcasevariants':
                        self.flags |= SearchOption.case_insensitive
                    elif len(text2) == 2:
                        dictionary[text2[0]] = text2[1]
            else:
                if ignore_comments and not text.startswith('#') and len(text) > 0:
                    num = text.find('#')

                    if num >= 0:
                        text = text[:num].rstrip()
                        if len(text) == 0:
                            continue
                    self.add(text)
                    if len(dictionary) == 0:
                        continue

                    hashset = [text]
                    list = []
                    for key, value in dictionary.items():
                        for text3 in hashset:
                            text4 = text3.replace(key, value)
                            if text3 != text4:
                                list.append(text4)
                        for item in list:
                            hashset.append(item)
                        list = []

                    if len(hashset) <= 1:
                        continue

                    for s in hashset:
                        self.add(s)

                if not ignore_comments:
                    self.add(text)

    def load_fn(self, filename, ignore_comments=True):
        with open(filename, 'r', encoding='utf-8') as reader:
            self.load_internal(reader, ignore_comments)

    def load_stream(self, stream, ignore_comments=True):
        self.load_internal(stream, ignore_comments)

    def load_bytes(self, data, ignore_comments=True):
        memory_stream = io.BytesIO()
        memory_stream.write(data)
        memory_stream.seek(0)
        self.load_internal(memory_stream, ignore_comments)

    @property
    def items(self):
        return self.words

