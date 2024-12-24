from enum import Enum

class Unit(Enum):
    Mmm = 1
    Mcm = 2
    Mdm = 3
    Mm = 4
    Mkm = 5
    Mmm2 = 6
    Mcm2 = 7
    Mm2 = 8
    Ma = 9
    Mha = 10
    Mkm2 = 11
    Mmg = 12
    Mg = 13
    Mkg = 14
    Mt = 15
    Mml = 16
    Mcm3 = 17
    Mcl = 18
    Mdl = 19
    Ml = 20
    Mm3 = 21
    Mcentigrade = 22
    Mfahrenheit = 23
    Mkelvin = 24
    Mpercent = 25
    Mdegree = 26
    BISin = 27
    BISft = 28
    BISyd = 29
    BISfurlong = 30
    BISmi = 31
    BISin2 = 32
    BISft2 = 33
    BISyd2 = 34
    BISacre = 35
    BISmi2 = 36
    BISoz = 37
    BISlb = 38
    BISstone = 39
    BISshortHW = 40
    BISlongHW = 41
    BISshortTon = 42
    BISlongTon = 43
    BISflozUK = 44
    BISptUK = 45
    BISqtUK = 46
    BISgalUK = 47
    BISbuUK = 48
    BISflozUS = 49
    BISptUS = 50
    BISgalUS = 51
    BISptUSDry = 52
    BISbuUSDry = 53
    Other = 54
    Currency = 55
    NoUnit = 56


class CustomUnitDefinition:
    def __init__(self, unit=Unit.NoUnit, category_name=None):
        self.unit = unit
        self.category_name = category_name

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def category_name(self):
        return self._category_name

    @category_name.setter
    def category_name(self, value):
        self._category_name = value

    def clone(self):
        # Manually clone the object
        return CustomUnitDefinition(
            unit=self.unit,
            category_name=self.category_name if self.category_name is None else str(self.category_name)
        )