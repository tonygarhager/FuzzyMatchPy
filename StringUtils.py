import unicodedata
import pycountry
import string
import re
from typing import List
from typing import Tuple
from enum import Enum
import ctypes
from ctypes import wintypes
class LPNLSVERSIONINFO(ctypes.Structure):
    _fields_ = [
        ("dwNLSVersionInfoSize", wintypes.DWORD),  # Size of the structure
        ("dwNLSVersion", wintypes.DWORD),         # Version of the NLS data
        ("dwDefinedVersion", wintypes.DWORD),     # Defined version of the NLS data
    ]
class UnicodeCategory(Enum):
    # Uppercase letter
    UppercaseLetter = 0
    # Lowercase letter
    LowercaseLetter = 1
    # Titlecase letter
    TitlecaseLetter = 2
    # Modifier letter character
    ModifierLetter = 3
    # Other letter
    OtherLetter = 4
    # Nonspacing mark
    NonSpacingMark = 5
    # Spacing combining mark
    SpacingCombiningMark = 6
    # Enclosing mark
    EnclosingMark = 7
    # Decimal digit number
    DecimalDigitNumber = 8
    # Letter number
    LetterNumber = 9
    # Other number
    OtherNumber = 10
    # Space separator
    SpaceSeparator = 11
    # Line separator
    LineSeparator = 12
    # Paragraph separator
    ParagraphSeparator = 13
    # Control character
    Control = 14
    # Format character
    Format = 15
    # Surrogate character
    Surrogate = 16
    # Private-use character
    PrivateUse = 17
    # Connector punctuation
    ConnectorPunctuation = 18
    # Dash punctuation
    DashPunctuation = 19
    # Open punctuation
    OpenPunctuation = 20
    # Close punctuation
    ClosePunctuation = 21
    # Initial quote punctuation
    InitialQuotePunctuation = 22
    # Final quote punctuation
    FinalQuotePunctuation = 23
    # Other punctuation
    OtherPunctuation = 24
    # Mathematical symbol
    MathSymbol = 25
    # Currency symbol
    CurrencySymbol = 26
    # Modifier symbol
    ModifierSymbol = 27
    # Other symbol
    OtherSymbol = 28
    # Other not assigned
    OtherNotAssigned = 29

class UnicodeBlock(Enum):
    Unknown = 0
    BasicLatin = 1
    Latin1Supplement = 2
    LatinExtendedA = 3
    LatinExtendedB = 4
    IPAExtensions = 5
    SpacingModifierLetters = 6
    CombiningDiacriticalMarks = 7
    GreekAndCoptic = 8
    Cyrillic = 9
    CyrillicSupplement = 10
    Armenian = 11
    Hebrew = 12
    Arabic = 13
    Syriac = 14
    ArabicSupplement = 15
    Thaana = 16
    NKo = 17
    Devanagari = 18
    Bengali = 19
    Gurmukhi = 20
    Gujarati = 21
    Oriya = 22
    Tamil = 23
    Telugu = 24
    Kannada = 25
    Malayalam = 26
    Sinhala = 27
    Thai = 28
    Lao = 29
    Tibetan = 30
    Myanmar = 31
    Georgian = 32
    HangulJamo = 33
    Ethiopic = 34
    EthiopicSupplement = 35
    Cherokee = 36
    UnifiedCanadianAboriginalSyllabics = 37
    Ogham = 38
    Runic = 39
    Tagalog = 40
    Hanunoo = 41
    Buhid = 42
    Tagbanwa = 43
    Khmer = 44
    Mongolian = 45
    Limbu = 46
    TaiLe = 47
    NewTaiLue = 48
    KhmerSymbols = 49
    Buginese = 50
    Balinese = 51
    PhoneticExtensions = 52
    PhoneticExtensionsSupplement = 53
    CombiningDiacriticalMarksSupplement = 54
    LatinExtendedAdditional = 55
    GreekExtended = 56
    GeneralPunctuation = 57
    SuperscriptsAndSubscripts = 58
    CurrencySymbols = 59
    CombiningDiacriticalMarksForSymbols = 60
    LetterlikeSymbols = 61
    NumberForms = 62
    Arrows = 63
    MathematicalOperators = 64
    MiscellaneousTechnical = 65
    ControlPictures = 66
    OpticalCharacterRecognition = 67
    EnclosedAlphanumerics = 68
    BoxDrawing = 69
    BlockElements = 70
    GeometricShapes = 71
    MiscellaneousSymbols = 72
    Dingbats = 73
    MiscellaneousMathematicalSymbolsA = 74
    SupplementalArrowsA = 75
    BraillePatterns = 76
    SupplementalArrowsB = 77
    MiscellaneousMathematicalSymbolsB = 78
    SupplementalMathematicalOperators = 79
    MiscellaneousSymbolsAndArrows = 80
    Glagolitic = 81
    LatinExtendedC = 82
    Coptic = 83
    GeorgianSupplement = 84
    Tifinagh = 85
    EthiopicExtended = 86
    SupplementalPunctuation = 87
    CJKRadicalsSupplement = 88
    KangxiRadicals = 89
    IdeographicDescriptionCharacters = 90
    CJKSymbolsAndPunctuation = 91
    Hiragana = 92
    Katakana = 93
    Bopomofo = 94
    HangulCompatibilityJamo = 95
    Kanbun = 96
    BopomofoExtended = 97
    CJKStrokes = 98
    KatakanaPhoneticExtensions = 99
    EnclosedCJKLettersAndMonths = 100
    CJKCompatibility = 101
    CJKUnifiedIdeographsExtensionA = 102
    YijingHexagramSymbols = 103
    CJKUnifiedIdeographs = 104
    YiSyllables = 105
    YiRadicals = 106
    ModifierToneLetters = 107
    LatinExtendedD = 108
    SylotiNagri = 109
    Phagspa = 110
    HangulSyllables = 111
    HighSurrogates = 112
    HighPrivateUseSurrogates = 113
    LowSurrogates = 114
    PrivateUseArea = 115
    CJKCompatibilityIdeographs = 116
    AlphabeticPresentationForms = 117
    ArabicPresentationFormsA = 118
    VariationSelectors = 119
    VerticalForms = 120
    CombiningHalfMarks = 121
    CJKCompatibilityForms = 122
    SmallFormVariants = 123
    ArabicPresentationFormsB = 124
    HalfwidthAndFullwidthForms = 125
    Specials = 126

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

    class BlockRange:
        def __init__(self, first: str, last: str, block: UnicodeBlock):
            self.first = first
            self.last = last
            self.block = block
    BlockRanges = [
        BlockRange('\0', '\u007f', UnicodeBlock.BasicLatin),
        BlockRange('\u0080', 'ÿ', UnicodeBlock.Latin1Supplement),
        BlockRange('Ā', 'ſ', UnicodeBlock.LatinExtendedA),
        BlockRange('ƀ', 'ɏ', UnicodeBlock.LatinExtendedB),
        BlockRange('ɐ', 'ʯ', UnicodeBlock.IPAExtensions),
        BlockRange('ʰ', '˿', UnicodeBlock.SpacingModifierLetters),
        BlockRange('̀', 'ͯ', UnicodeBlock.CombiningDiacriticalMarks),
        BlockRange('Ͱ', 'Ͽ', UnicodeBlock.GreekAndCoptic),
        BlockRange('Ѐ', 'ӿ', UnicodeBlock.Cyrillic),
        BlockRange('Ԁ', 'ԯ', UnicodeBlock.CyrillicSupplement),
        BlockRange('԰', '֏', UnicodeBlock.Armenian),
        BlockRange('֐', '׿', UnicodeBlock.Hebrew),
        BlockRange('؀', 'ۿ', UnicodeBlock.Arabic),
        BlockRange('܀', 'ݏ', UnicodeBlock.Syriac),
        BlockRange('ݐ', 'ݿ', UnicodeBlock.ArabicSupplement),
        BlockRange('ހ', '޿', UnicodeBlock.Thaana),
        BlockRange('߀', '߿', UnicodeBlock.NKo),
        BlockRange('ऀ', 'ॿ', UnicodeBlock.Devanagari),
        BlockRange('ঀ', '৿', UnicodeBlock.Bengali),
        BlockRange('਀', '੿', UnicodeBlock.Gurmukhi),
        BlockRange('઀', '૿', UnicodeBlock.Gujarati),
        BlockRange('଀', '୿', UnicodeBlock.Oriya),
        BlockRange('஀', '௿', UnicodeBlock.Tamil),
        BlockRange('ఀ', '౿', UnicodeBlock.Telugu),
        BlockRange('ಀ', '೿', UnicodeBlock.Kannada),
        BlockRange('ഀ', 'ൿ', UnicodeBlock.Malayalam),
        BlockRange('඀', '෿', UnicodeBlock.Sinhala),
        BlockRange('฀', '๿', UnicodeBlock.Thai),
        BlockRange('຀', '໿', UnicodeBlock.Lao),
        BlockRange('ༀ', '࿿', UnicodeBlock.Tibetan),
        BlockRange('က', '႟', UnicodeBlock.Myanmar),
        BlockRange('Ⴀ', 'ჿ', UnicodeBlock.Georgian),
        BlockRange('ᄀ', 'ᇿ', UnicodeBlock.HangulJamo),
        BlockRange('ሀ', '፿', UnicodeBlock.Ethiopic),
        BlockRange('ᎀ', '᎟', UnicodeBlock.EthiopicSupplement),
        BlockRange('Ꭰ', '᏿', UnicodeBlock.Cherokee),
        BlockRange('᐀', 'ᙿ', UnicodeBlock.UnifiedCanadianAboriginalSyllabics),
        BlockRange('\u1680', '᚟', UnicodeBlock.Ogham),
        BlockRange('ᚠ', '᛿', UnicodeBlock.Runic),
        BlockRange('ᜀ', 'ᜟ', UnicodeBlock.Tagalog),
        BlockRange('ᜠ', '᜿', UnicodeBlock.Hanunoo),
        BlockRange('ᝀ', '᝟', UnicodeBlock.Buhid),
        BlockRange('ᝠ', '᝿', UnicodeBlock.Tagbanwa),
        BlockRange('ក', '៿', UnicodeBlock.Khmer),
        BlockRange('᠀', '᢯', UnicodeBlock.Mongolian),
        BlockRange('ᤀ', '᥏', UnicodeBlock.Limbu),
        BlockRange('ᥐ', '᥿', UnicodeBlock.TaiLe),
        BlockRange('ᦀ', '᧟', UnicodeBlock.NewTaiLue),
        BlockRange('᧠', '᧿', UnicodeBlock.KhmerSymbols),
        BlockRange('ᨀ', '᨟', UnicodeBlock.Buginese),
        BlockRange('ᬀ', '᭿', UnicodeBlock.Balinese),
        BlockRange('ᴀ', 'ᵿ', UnicodeBlock.PhoneticExtensions),
        BlockRange('ᶀ', 'ᶿ', UnicodeBlock.PhoneticExtensionsSupplement),
        BlockRange('᷀', '᷿', UnicodeBlock.CombiningDiacriticalMarksSupplement),
        BlockRange('Ḁ', 'ỿ', UnicodeBlock.LatinExtendedAdditional),
        BlockRange('ἀ', '῿', UnicodeBlock.GreekExtended),
        BlockRange('\u2000', '⁯', UnicodeBlock.GeneralPunctuation),
        BlockRange('⁰', '₟', UnicodeBlock.SuperscriptsAndSubscripts),
        BlockRange('₠', '⃏', UnicodeBlock.CurrencySymbols),
        BlockRange('⃐', '⃿', UnicodeBlock.CombiningDiacriticalMarksForSymbols),
        BlockRange('℀', '⅏', UnicodeBlock.LetterlikeSymbols),
        BlockRange('⅐', '↏', UnicodeBlock.NumberForms),
        BlockRange('←', '⇿', UnicodeBlock.Arrows),
        BlockRange('∀', '⋿', UnicodeBlock.MathematicalOperators),
        BlockRange('⌀', '⏿', UnicodeBlock.MiscellaneousTechnical),
        BlockRange('␀', '␿', UnicodeBlock.ControlPictures),
        BlockRange('⑀', '⑟', UnicodeBlock.OpticalCharacterRecognition),
        BlockRange('①', '⓿', UnicodeBlock.EnclosedAlphanumerics),
        BlockRange('─', '╿', UnicodeBlock.BoxDrawing),
        BlockRange('▀', '▟', UnicodeBlock.BlockElements),
        BlockRange('■', '◿', UnicodeBlock.GeometricShapes),
        BlockRange('☀', '⛿', UnicodeBlock.MiscellaneousSymbols),
        BlockRange('✀', '➿', UnicodeBlock.Dingbats),
        BlockRange('⟀', '⟯', UnicodeBlock.MiscellaneousMathematicalSymbolsA),
        BlockRange('⟰', '⟿', UnicodeBlock.SupplementalArrowsA),
        BlockRange('⠀', '⣿', UnicodeBlock.BraillePatterns),
        BlockRange('⤀', '⥿', UnicodeBlock.SupplementalArrowsB),
        BlockRange('⦀', '⧿', UnicodeBlock.MiscellaneousMathematicalSymbolsB),
        BlockRange('⨀', '⫿', UnicodeBlock.SupplementalMathematicalOperators),
        BlockRange('⬀', '⯿', UnicodeBlock.MiscellaneousSymbolsAndArrows),
        BlockRange('Ⰰ', 'ⱟ', UnicodeBlock.Glagolitic),
        BlockRange('Ⱡ', 'Ɀ', UnicodeBlock.LatinExtendedC),
        BlockRange('Ⲁ', '⳿', UnicodeBlock.Coptic),
        BlockRange('ⴀ', '⴯', UnicodeBlock.GeorgianSupplement),
        BlockRange('ⴰ', '⵿', UnicodeBlock.Tifinagh),
        BlockRange('ⶀ', '⷟', UnicodeBlock.EthiopicExtended),
        BlockRange('⸀', '⹿', UnicodeBlock.SupplementalPunctuation),
        BlockRange('⺀', '⻿', UnicodeBlock.CJKRadicalsSupplement),
        BlockRange('⼀', '⿟', UnicodeBlock.KangxiRadicals),
        BlockRange('⿰', '⿿', UnicodeBlock.IdeographicDescriptionCharacters),
        BlockRange('\u3000', '〿', UnicodeBlock.CJKSymbolsAndPunctuation),
        BlockRange('぀', 'ゟ', UnicodeBlock.Hiragana),
        BlockRange('゠', 'ヿ', UnicodeBlock.Katakana),
        BlockRange('㄀', 'ㄯ', UnicodeBlock.Bopomofo),
        BlockRange('㄰', '㆏', UnicodeBlock.HangulCompatibilityJamo),
        BlockRange('㆐', '㆟', UnicodeBlock.Kanbun),
        BlockRange('ㆠ', 'ㆿ', UnicodeBlock.BopomofoExtended),
        BlockRange('㇀', '㇯', UnicodeBlock.CJKStrokes),
        BlockRange('ㇰ', 'ㇿ', UnicodeBlock.KatakanaPhoneticExtensions),
        BlockRange('㈀', '㋿', UnicodeBlock.EnclosedCJKLettersAndMonths),
        BlockRange('㌀', '㏿', UnicodeBlock.CJKCompatibility),
        BlockRange('㐀', '䶿', UnicodeBlock.CJKUnifiedIdeographsExtensionA),
        BlockRange('䷀', '䷿', UnicodeBlock.YijingHexagramSymbols),
        BlockRange('一', '鿿', UnicodeBlock.CJKUnifiedIdeographs),
        BlockRange('ꀀ', '꒏', UnicodeBlock.YiSyllables),
        BlockRange('꒐', '꓏', UnicodeBlock.YiRadicals),
        BlockRange('꜀', 'ꜟ', UnicodeBlock.ModifierToneLetters),
        BlockRange('꜠', 'ꟿ', UnicodeBlock.LatinExtendedD),
        BlockRange('ꠀ', '꠯', UnicodeBlock.SylotiNagri),
        BlockRange('ꡀ', '꡿', UnicodeBlock.Phagspa),
        BlockRange('가', '힯', UnicodeBlock.HangulSyllables),
        BlockRange('\ud800', '\udb7f', UnicodeBlock.HighSurrogates),
        BlockRange('\udb80', '\udbff', UnicodeBlock.HighPrivateUseSurrogates),
        BlockRange('\udc00', '\udfff', UnicodeBlock.LowSurrogates),
        BlockRange('', '', UnicodeBlock.PrivateUseArea),
        BlockRange('豈', '﫿', UnicodeBlock.CJKCompatibilityIdeographs),
        BlockRange('ﬀ', 'ﭏ', UnicodeBlock.AlphabeticPresentationForms),
        BlockRange('ﭐ', '﷿', UnicodeBlock.ArabicPresentationFormsA),
        BlockRange('︀', '️', UnicodeBlock.VariationSelectors),
        BlockRange('︐', '︟', UnicodeBlock.VerticalForms),
        BlockRange('︠', '︯', UnicodeBlock.CombiningHalfMarks),
        BlockRange('︰', '﹏', UnicodeBlock.CJKCompatibilityForms),
        BlockRange('﹐', '﹯', UnicodeBlock.SmallFormVariants),
        BlockRange('ﹰ', '﻿', UnicodeBlock.ArabicPresentationFormsB),
        BlockRange('＀', '￯', UnicodeBlock.HalfwidthAndFullwidthForms),
        BlockRange('￰', '￿', UnicodeBlock.Specials)
    ]

    block_range_index = {}

    for blockRange in BlockRanges:
        block_range_index[blockRange.block] = blockRange

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
    def is_in_block(c, b:UnicodeBlock):
        if b in StringUtils.block_range_index.keys():
            block_range = StringUtils.block_range_index[b]
            return c >= block_range.first and c <= block_range.last
        return False

    @staticmethod
    def is_cjk_punctuation(c: str) -> bool:
        """
        Checks if a character is a CJK punctuation character.

        Args:
            c (str): A single character to check.

        Returns:
            bool: True if the character is CJK punctuation, False otherwise.
        """
        return (
                ('\u3001' <= c <= '\u303F') or
                ('\u30FB' <= c <= '\u30FE') or
                ('\u3200' <= c <= '\u32FF') or
                ('\uFF01' <= c <= '\uFF0F') or
                ('\uFF1A' <= c <= '\uFF20') or
                ('\uFF3B' <= c <= '\uFF3D') or
                ('\uFF5B' <= c <= '\uFF5C')
        )

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
