import unicodedata
import pycountry
import string
import re
from typing import List
from typing import Tuple
import ctypes
from ctypes import wintypes
class LPNLSVERSIONINFO(ctypes.Structure):
    _fields_ = [
        ("dwNLSVersionInfoSize", wintypes.DWORD),  # Size of the structure
        ("dwNLSVersion", wintypes.DWORD),         # Version of the NLS data
        ("dwDefinedVersion", wintypes.DWORD),     # Defined version of the NLS data
    ]

class StringUtils:
    base_chars = {}
    whitespace_characters = ['\t',
			'\n',
			'\v',
			'\f',
			'\r',
			' ',
			'\u0085',
			'\u00a0',
			'\u1680',
			'᠎',
			'\u2000',
			'\u2001',
			'\u2002',
			'\u2003',
			'\u2004',
			'\u2005',
			'\u2006',
			'\u2007',
			'\u2008',
			'\u2009',
			'\u200a',
			'\u2028',
			'\u2029',
			'\u202f',
			'\u205f',
			'\u3000']
    blanks = [' ',
			'\u00a0',
			'\u1680',
			'\u2000',
			'\u2001',
			'\u2002',
			'\u2003',
			'\u2004',
			'\u2005',
			'\u2006',
			'\u2007',
			'\u2008',
			'\u2009',
			'\u200a',
			'\u202f',
			'\u205f',
			'\u3000']
    @staticmethod
    def compare_ordinal_ignore_case(str1, str2):
        # Convert both strings to lowercase for case-insensitive comparison
        str1_lower = str1.lower()
        str2_lower = str2.lower()

        if str1_lower == str2_lower:
            return 0  # Strings are equal
        elif str1_lower < str2_lower:
            return -1  # str1 is less than str2
        else:
            return 1  # str1 is greater than str2

    @staticmethod
    def is_white_space(char):
        """
        Checks if the character is a whitespace character.
        Equivalent to char.IsWhiteSpace in C#.
        :param char: A single character.
        :return: True if the character is a whitespace, otherwise False.
        """
        if len(char) != 1:
            raise ValueError("Input must be a single character.")
        return char.isspace()

    @staticmethod
    def is_punctuation(char):
        return char in string.punctuation

    @staticmethod
    def is_symbol(char):
        return not char.isalnum() and not char.isspace()

    @staticmethod
    def is_separator(char):
        """
        Checks if the character is a separator character.
        Python does not have a direct equivalent to char.IsSeparator,
        so we mimic the behavior by checking against Unicode separator categories.
        :param char: A single character.
        :return: True if the character is a separator, otherwise False.
        """
        if len(char) != 1:
            raise ValueError("Input must be a single character.")
        return unicodedata.category(char) in ('Zl', 'Zp', 'Zs')  # Line separator, Paragraph separator, Space separator

    @staticmethod
    def get_unicode_category(char):
        # Return the Unicode category of the character
        return unicodedata.category(char)

    @staticmethod
    def is_apostrophe(c):
        return c == "'"

    @staticmethod
    def is_hyphen(c):
        return c == "-"

    @staticmethod
    def is_dash(c):
        return c == "—"

    @staticmethod
    def is_colon(c):
        return c == ":"

    @staticmethod
    def is_semicolon(c):
        return c == ";"

    @staticmethod
    def is_cjk_char(c):
        # Check if the character is within the CJK ranges (Chinese, Japanese, or Korean)
        char_code = ord(c)  # Get the Unicode code point of the character

        # CJK Unicode ranges
        if (0x4E00 <= char_code <= 0x9FFF) or \
                (0x3040 <= char_code <= 0x30FF) or \
                (0xAC00 <= char_code <= 0xD7AF):
            return True
        return False

    @staticmethod
    def half_width_to_full_width(input_str):
        # Convert the input string to a list of characters
        array = list(input_str)

        for i in range(len(array)):
            if array[i] == ' ':
                # Convert half-width space to full-width space
                array[i] = '\u3000'
            elif ord(array[i]) < 0x007f:
                # Convert half-width character to full-width
                array[i] = chr(ord(array[i]) + 0xFEE0)

        # Join the list back into a string and return
        return ''.join(array)

    @staticmethod
    def get_iso_language_code(culture_name):
        try:
            # Split culture name to extract the language part (e.g., "en-US" -> "en")
            language_code = culture_name.split('-')[0]
            # Look up the language in pycountry
            language = pycountry.languages.get(alpha_2=language_code)
            if language:
                return language.alpha_2  # Return the two-letter ISO code
        except Exception:
            pass
        return None  # Return None if not found

    @staticmethod
    def use_fullwidth(culture_name):
        twoletter = StringUtils.get_iso_language_code(culture_name)
        return twoletter == 'ja' or twoletter == 'zh' or twoletter == 'ko'

    @staticmethod
    # Helper function to check if a character is an apostrophe
    def is_apostrophe(ch):
        # Define apostrophe-like characters
        apostrophe_chars = {"'", "’"}  # Adjust this set based on your requirements
        return ch in apostrophe_chars

    @staticmethod
    def is_latin_letter(c):
        """
        Determines if the given character is a Latin letter.

        :param c: A single character string.
        :return: True if the character is a Latin letter, False otherwise.
        """
        if len(c) != 1:
            raise ValueError("Input must be a single character.")

        if ord(c) < 0x3000:
            return c.isalpha() and not StringUtils.is_apostrophe(c)
        return ('Ａ' <= c <= 'Ｚ') or ('ａ' <= c <= 'ｚ')

    @staticmethod
    def get_prefix_length(s:str, prefix_chars:List[str]) -> int:
        if not s or len(s) == 0:
            return 0
        if not prefix_chars or len(prefix_chars) == 0:
            return 0
        for i in range(len(s)):
            if s[i] not in prefix_chars:
                return i
        return len(s)

    @staticmethod
    def get_suffix_length(s:str, suffix_chars:List[str]) -> int:
        if not s or len(s) == 0:
            return 0
        if not suffix_chars or len(suffix_chars) == 0:
            return 0
        num = len(s) - 1
        i = num
        while i >= 0:
            if s[i] not in suffix_chars:
                return num - i
            i -= 1
        return len(s)

    @staticmethod
    def trim_start(s:str, trim_characters:List[str]) -> Tuple[str, str]:
        trimmed_prefix:str = None
        prefix_length:int = StringUtils.get_prefix_length(s, trim_characters)
        if prefix_length <= 0:
            return s, trimmed_prefix
        trimmed_prefix = s[:prefix_length]
        return s[prefix_length:], trimmed_prefix

    @staticmethod
    def trim_end(s:str, trim_characters:List[str]) -> Tuple[str, str]:
        trimmed_suffix:str = None
        suffix_length:int = StringUtils.get_suffix_length(s, trim_characters)
        if suffix_length <= 0:
            return s, trimmed_suffix
        length = len(s)
        trimmed_suffix = s[length - suffix_length:]
        return s[:length - suffix_length], trimmed_suffix

    @staticmethod
    def remove_invisible_characters(text):
        # Match control characters, zero-width spaces, etc.
        invisible_chars = re.compile(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]')
        return invisible_chars.sub('', text)

    @staticmethod
    def is_ja_long_vowel_marker(c:str) -> bool:
        return c == 'ー' or c == 'ｰ'

    @staticmethod
    def to_base(c):
        # Check if the character is within the specified Unicode range
        if '\ud800' <= c <= '':
            return c

        # Check the BaseChars dictionary for the character
        if c in StringUtils.base_chars:
            return StringUtils.base_chars[c]

        # Normalize the character and update the BaseChars dictionary
        normalized_char = unicodedata.normalize('NFD', c)[0]
        StringUtils.base_chars[c] = normalized_char

        return normalized_char
    @staticmethod
    def escape_fn(c):
        return c.replace('\\', '\\\\')

if __name__ == "__main__":
    print(StringUtils.is_latin_letter('A'))  # True
    print(StringUtils.is_latin_letter('ａ'))  # True
    print(StringUtils.is_latin_letter('你'))  # False
    print(StringUtils.is_latin_letter("'"))  # False
    print(StringUtils.is_latin_letter('Ａ'))
