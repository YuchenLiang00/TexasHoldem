""" 存储计算手牌胜率的功能 
    Number of Distinct Hand Values::

    Straight Flush   10
    Four of a Kind   156      [(13 choose 2) * (2 choose 1)]
    Full Houses      156      [(13 choose 2) * (2 choose 1)]
    Flush            1277     [(13 choose 5) - 10 straight flushes]
    Straight         10
    Three of a Kind  858      [(13 choose 3) * (3 choose 1)]
    Two Pair         858      [(13 choose 3) * (3 choose 2)]
    One Pair         2860     [(13 choose 4) * (4 choose 1)]
    High card      + 1277     [(13 choose 5) - 10 straights]
    -------------------------
    TOTAL            7462
"""

class Helper:
    """ 手牌胜率计算器 """
    def __init__(self) -> None:
        pass
