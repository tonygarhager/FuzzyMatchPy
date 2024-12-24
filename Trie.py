class TrieNode:
    def __init__(self):
        self.children = {}  # Dictionary to store child nodes
        self.value = None    # Value associated with the key (if any)


class Trie:
    def __init__(self):
        self.root = TrieNode()  # Initialize the root node

    def insert(self, key: str, value: int):
        """Insert a key-value pair into the trie."""
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()  # Create a new TrieNode if char is not found
            node = node.children[char]
        node.value = value  # Set the value for the key

    def search(self, key: str) -> int:
        """Search for a key and return its associated value, or None if not found."""
        node = self.root
        for char in key:
            if char not in node.children:
                return None  # Return None if the key is not found
            node = node.children[char]
        return node.value  # Return the value if key exists

    def starts_with(self, prefix: str) -> bool:
        """Return True if there is any key that starts with the given prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False  # Return False if the prefix does not exist
            node = node.children[char]
        return True  # Return True if prefix is found

if __name__ == "__main__":
    # Example Usage:
    trie = Trie()
    trie.insert("apple", 10)
    trie.insert("app", 5)

    print(trie.search("apple"))  # Output: 10
    print(trie.search("app"))    # Output: 5
    print(trie.search("appl"))   # Output: None
    print(trie.starts_with("app"))  # Output: True
    print(trie.starts_with("banana"))  # Output: False
