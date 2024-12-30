from SortSpecification import *

class Sorter_T:
    def __init__(self, comparer, sort_specification: SortSpecification):
        if len(sort_specification) == 0:
            raise Exception("Sort specification doesn't contain any sort criteria")
        self._comparer = comparer
        self._sort_specification = sort_specification

    def compare(self, x, y):
        num = 0
        num2 = 0
        while (num2 < len(self._sort_specification) and num == 0):
            num = self._comparer.compare(x, y, self._sort_specification[num].field_name)

            if self._sort_specification[num2].direction == SortDirection.Descending:
                num = -num
            num2 += 1

        return num

