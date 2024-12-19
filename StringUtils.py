

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