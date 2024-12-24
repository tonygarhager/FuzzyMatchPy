from typing import List

class SortDirection:
    Ascending = 0
    Descending = 1

class SortCriterium:
    def __init__(self, field_name:str=None, dir:SortDirection=None):
        self.field_name = field_name.lower()
        self.direction = dir

    def get_field_name(self):
        return self.field_name
    def set_field_name(self, field_name:str):
        self.field_name = field_name.lower()

class SortSpecification:
    def __init__(self, sort_spec:str = None):
        self.criteria = []

        if not sort_spec or len(sort_spec) == 0:
            return

        for text in [s for s in sort_spec.split(' ') if s]:
            num = text.find('/')
            if num > 0:
                text2 = text[num + 1:].lower()
                text3 = text[:num].lower()

                if (len(text2) <= 0 or len(text3) <= 0 or (not text2.lower().startswith('d') and not text2.lower().startswith('a'))):
                    raise("TMInvalidSortSpecification")
                dir: SortDirection = SortDirection.Ascending
                if text2.lower().startswith('d'):
                    dir = SortDirection.Descending

                self.criteria.append(SortCriterium(text3, dir))

    def __len__(self):
        return len(self.criteria)

    def __getitem__(self, item):
        return self.criteria[item]

    def add(self, sc:SortCriterium):
        self.criteria.append(sc)


