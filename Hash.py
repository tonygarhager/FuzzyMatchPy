
class Hash:
    @staticmethod
    def to_32bit(value):
        # Simulate a 32-bit signed integer
        value = value & 0xFFFFFFFF  # Mask to the lower 32 bits
        if value >= 0x80000000:
            value -= 0x100000000  # Convert to signed 32-bit
        return value
    @staticmethod
    def get_hashcode_int(s:str) -> int:
        num = 0
        for c in s:
            num = (31 * num + ord(c))  # ord(c) gives the Unicode code point of the character
        num = Hash.to_32bit(num)
        return num

    @staticmethod
    def get_hash_code_long(s: str) -> int:
        num = 0
        for c in s:
            num = 31 * num + ord(c)
        return num