""" 存储手牌信息 """

import random
import itertools
from collections import namedtuple


Card = namedtuple('Card', ['suit', 'rank'])


class Hand:
    SUITS = ('H', 'D', 'C', 'S')
    RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')

    def __init__(self, cards:list[Card]=None) -> None:
        self._cards = cards if cards else []

    def __len__(self,):
        return len(self._cards)

    def __getitem__(self, index):
        return self._cards[index]

    def __str__(self):
        l = [s + r for s, r in self._cards]
        return ' '.join(l)

    def __add__(self, other):
        return Hand(self._cards + other._cards)

    def show(self):
        l = [s + r for s, r in self._cards]
        print(' '.join(l))


class Deck(Hand):
    def __init__(self) -> None:
        self._cards = [Card(s, r) for s, r
                       in itertools.product(Hand.SUITS, Hand.RANKS)]
        random.shuffle(self._cards)

    def pop(self,):
        return self._cards.pop()


# 判断牌力大小的函数（需要进一步实现）
def evaluate_hand(hand: Hand):
    # 这里需要编写逻辑来判断手牌的强度
    # 例如检查是否有同花顺、四条等
    pass


if __name__ == '__main__':
    h1 = Hand([Card('C', '2')])
    h2 = Hand([Card('C', '3')])
    h = h1 + h2
    print(h)

    pass
