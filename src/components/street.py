from enum import Enum


class Street(Enum):
    """ 四条街 本身就是可迭代的 """

    PRE_FLOP = "Pre-Flop"
    FLOP = "Flop"
    TURN = "Turn"
    RIVER = "River"
    
    def __str__(self):
        return self.value