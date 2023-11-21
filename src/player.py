""" 存储玩家的信息和行为 """

from collections import namedtuple
import gc
from src.hand import Hand

INIT_MONEY = 1_000


class Move:
    def __init__(self, action:str='', amount:int='') -> None:
        self.action = action
        self.amount = amount

    def __str__(self):
        return self.action + ' ' + str(self.amount)

class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.money = INIT_MONEY
        self._bet_history = {'Pre-Flop': [],
                             'Flop': [], 'Turn': [], 'River': []}

    def bet(self, amount, street):
        """ 下注行为 """
        if amount >= self.money:
            amount = self.money
            self._bet_history[street].append(Move('ALL-IN', amount))
        elif amount < 0:
            # fold
            return self.fold(street)
        elif amount == 0:
            # check
            self._bet_history[street].append(Move('Check', 0))
        else:
            self._bet_history[street].append(Move('Bet', amount))
            self.money -= amount
        return self.money

    def fold(self, street):
        # 标记玩家弃牌
        self._bet_history[street].append(Move('Fold', None))
        return 'Fold'

    def raise_bet(self, amount):
        # TODO 加注, 要判断是否符合加注规则
        return self.bet(amount)

    def set_hand(self, hand: list[Hand]):
        # dealer发牌的功能
        self.hand: list[Hand] = hand
        self._bet_history = {'Pre-Flop': [],
                             'Flop': [], 'Turn': [], 'River': []}
        gc.collect()

    def show_hands(self):
        print(self.name, self.hand,sep='\t', end=":\t")


    def show_move(self,) -> str:
        """ 展示行动 """
        move_list: list[Move] = [str(l[-1]) if l else str(Move()) for l in self._bet_history.values()]

        return '\t'.join(move_list)