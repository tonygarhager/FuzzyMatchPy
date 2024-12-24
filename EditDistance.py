from typing import List

class EditOperation:
    Identity = 0
    Change = 1
    Move = 2
    Insert = 3
    Delete = 4
    Undefined = 5

class EditDistanceResolution:
    Non = 0
    Substitution = 1
    Deletion = 2
    Move = 3
    Other = 4

class EditDistanceItem:
    def __init__(self):
        self.source:int = 0
        self.target:int = 0
        self.operation:int = EditOperation.Undefined
        self.resolution:int = EditDistanceResolution.Non
        self.costs:float = 0
        self.move_source_target = 0
        self.move_target_source = 0

class EditDistance:
    def __init__(self, source_object_count:int, target_object_count:int, distance:float):
        self.source_object_count = source_object_count
        self.target_object_count = target_object_count
        self.distance = distance
        self.items = List[EditDistanceItem]

    def __getitem__(self, item):
        return self.items[item]

    def set_source_at(self, index:int, offset:int):
        value:EditDistanceItem = self.items[index]
        value.source = offset
        self.items[index] = value

    def set_target_at(self, index:int, offset:int):
        value:EditDistanceItem = self.items[index]
        value.target = offset
        self.items[index] = value

    def set_resolution_at(self, index:int, resolution:int):
        value:EditDistanceItem = self.items[index]
        value.resolution = resolution
        self.items[index] = value

    def find_source_item_index(self, source_token_offset:int) -> int:
        for i in range(len(self.items)):
            if self.items[i].source == source_token_offset and self.items[i].operation != EditOperation.Insert:
                return i
        return -1

    def find_target_item_index(self, target_token_offset:int) -> int:
        for i in range(len(self.items)):
            if self.items[i].target == target_token_offset and self.items[i].operation != EditOperation.Delete:
                return i
        return -1

    @staticmethod
    def sort_delegate(self, x:EditDistanceItem, y:EditDistanceItem):
        num = 0
        if x.operation != EditOperation.Insert and y.operation != EditOperation.Insert:
            num = x.source - y.source
        if num == 0  and x.operation != EditOperation.Delete and y.operation != EditOperation.Delete:
            num = x.target - y.target
        return num

    def sort(self):
        self.items.sort(key=self.sort_delegate)

    def get_score(self) -> float:
        num = self.source_object_count + self.target_object_count
        num -= sum(1 for item in self.items if
                   item.operation == EditOperation.Insert and item.resolution == EditDistanceResolution.Deletion)

        if num <= 0.0:
            return 0.0

        num = (num - 2.0 * self.distance) / num

        if num <= 0.0:
            return 0.0

        if num >= 1.0:
            return 1.0
        return num

    def add(self, item:EditDistanceItem):
        self.items.append(item)

    def add_at_start(self, item:EditDistanceItem):
        self.items.insert(0, item)





