""" 存储玩家的信息和行为 """
from src.hand import Hand

INIT_MONEY = 1_000

class Player:
    def __init__(self,name:str) -> None:
        self.name = name
        self.money = INIT_MONEY
        pass

    def set_hand(self, hand: list[Hand]):
        # dealer发牌的功能
        self.hand: list[Hand] = hand

    def bet(self, amount):
        # 实现下注的功能
        pass

    def show_hands(self):
        print(self.name, end=":\t")
        self.hand.show()
