
class Hash:
    @staticmethod
    def get_hashcode_int(s:str) -> int:
        num = 0
        for c in s:
            num = 31 * num + ord(c)  # ord(c) gives the Unicode code point of the character
        return num