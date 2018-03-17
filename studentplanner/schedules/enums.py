from enum import Enum

class Degree(Enum):
    BCH = range(1,7)
    BSC = range(1,8)
    MST = range(1,5)
    MSC = range(1,4)

    def semester_choices(self):
        return ((i, "semestr {}".format(i)) for i in self.value)
