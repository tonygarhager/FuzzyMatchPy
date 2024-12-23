
class Segment:
    def __init__(self):
        self.elements = []
        self.culture_name = 'InvariantCulture'
        self.tokens = []

    def is_empty(self):
        return not self.elements or len(self.elements) == 0

    def last_element(self):
        if self.is_empty():
            return None
        return self.elements[len(self.elements) - 1]

    def add(self, element):
        self.elements.append(element)