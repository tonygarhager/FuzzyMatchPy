import json

class ResourceReader:
    def __init__(self, resource_file):
        """
        Initializes the ResourceReader with a given resource file path.
        """
        self.resource_file = resource_file
        self.resources = None

    def open(self):
        """
        Opens and reads the resource file.
        """
        try:
            with open(self.resource_file, 'r', encoding='utf-8') as file:
                self.resources = json.load(file)
        except Exception as e:
            raise IOError(f"Failed to read the resource file: {e}")

    def get_resource(self, key):
        """
        Retrieves a resource by its key.
        """
        if self.resources is None:
            raise ValueError("Resource file is not opened. Call 'open()' first.")
        return self.resources.get(key, None)

    def close(self):
        """
        Closes the resource reader and releases any loaded resources.
        """
        self.resources = None


# Example usage
if __name__ == "__main__":
    # Assume we have a JSON file named 'resources.json' with content:
    # { "hello": "Hello, world!", "goodbye": "Goodbye, world!" }
    reader = ResourceReader('Sdl.LanguagePlatform.NLP.json')
    try:
        reader.open()
        print(reader.get_resource("hello"))  # Output: Hello, world!
        print(reader.get_resource("goodbye"))  # Output: Goodbye, world!
    finally:
        reader.close()
