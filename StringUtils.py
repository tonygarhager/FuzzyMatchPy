import unicodedata

class StringUtils:
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