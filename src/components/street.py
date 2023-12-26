from collections import namedtuple
from enum import Enum
from functools import total_ordering

StreetType = namedtuple("StreetType", ["name", "order"])
""" 
这里，StreetType是通过namedtuple创建的一个类。
您可以将其视为一个类，它的实例是具有命名字段（name和order）的元组。
- 类型还是元组：
StreetType是一个类型，其实例是具有两个命名字段name和order的元组。
- 第一个参数与变量名：
namedtuple的第一个参数是新类型的名称，这个名称用于内部表示和调试。它不必与变量名相同，但通常保持一致是一个好习惯，因为这样做可以提高代码的可读性。
"""


@total_ordering
class Street(Enum):  # 本身就是可迭代的
    """ 四条街 """
    
    PRE_FLOP = StreetType("Pre-Flop", 1)
    FLOP = StreetType("Flop", 2)
    TURN = StreetType("Turn", 3)
    RIVER = StreetType("River", 4)

    def __str__(self):
        return self.value.name

    def __lt__(self, other):
        if isinstance(other, Street):
            return self.value.order < other.value.order
        else:
            raise NotImplementedError(
                f"Can only compare Street class instance, {type(other)} found.")

    def __eq__(self, other):
        if isinstance(other, Street):
            return self.value.order == other.value.order
        else:
            raise NotImplementedError(
                f"Can only compare Street class instance, {type(other)} found.")
        
    def __hash__(self) -> int:
        return super().__hash__()


if __name__ == '__main__':
    t = Street.TURN
    r = Street.RIVER
    print(r)
    print(r >= t)
