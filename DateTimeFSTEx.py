
class DateTimeFSTEx:
    # Class version constant
    CURRENT_VERSION = 1

    def __init__(self):
        self.version = DateTimeFSTEx.CURRENT_VERSION
        self.patterns = []

    @staticmethod
    def from_binary(data):
        # Deserialize from binary format (using pickle here for simplicity)
        try:
            # Convert bytes to string (UTF-8)
            decoded_str = data.decode('utf-8')
            # Split the string by carriage return, removing empty entries
            lines = [line for line in decoded_str.split('\r') if line.strip()]

            if len(lines) == 0:
                return DateTimeFSTEx()

            # Try parsing the version from the first line
            try:
                version = int(lines[0])
            except ValueError:
                raise Exception("Unexpected data during DateTimeFSTEx deserialization")

            if version > 1:
                raise Exception(f"Unexpected DateTimeFSTEx version: {version}")

            # Remove the first element (version)
            lines.pop(0)

            # Create a new DateTimeFSTEx object
            date_time_fst_ex = DateTimeFSTEx()
            date_time_fst_ex.version = version

            # Add patterns
            date_time_fst_ex.patterns.extend(lines)

            return date_time_fst_ex
        except Exception as e:
            raise Exception(f"Error during deserialization: {str(e)}")

    def to_binary(self):
        # Convert the object to binary (byte array)
        try:
            # Start with version and patterns
            result = str(self.version) + '\r'
            result += '\r'.join(self.patterns)
            # Convert to UTF-8 encoded byte array
            return result.encode('utf-8')
        except Exception as e:
            raise Exception(f"Error during serialization: {str(e)}")

if __name__ == '__main__':
    # Example usage:
    date_time_fst_ex = DateTimeFSTEx()
    date_time_fst_ex.patterns.append("yyyy-MM-dd")
    date_time_fst_ex.patterns.append("MM/dd/yyyy")

    # Serialize the object to a binary (byte array)
    binary_data = date_time_fst_ex.to_binary()
    print("Serialized binary data:", binary_data)

    # Deserialize the binary data back to a DateTimeFSTEx object
    deserialized_date_time_fst_ex = DateTimeFSTEx.from_binary(binary_data)

    # Output the patterns to verify
    for pattern in deserialized_date_time_fst_ex.patterns:
        print("Pattern:", pattern)
