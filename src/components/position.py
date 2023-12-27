from enum import Enum


class Position(Enum):
    """ 玩家位置 """
    BTN = 0
    SB = 1
    BB = 2
    UTG = 3
    UTG1 = 4
    UTG2 = 5
    MP = 6
    HJ = 7
    CO = 8
    
    def __str__(self):
        return self.name

if __name__ == '__main__':
    p = Position(0)
    print(f"{p:>4}")