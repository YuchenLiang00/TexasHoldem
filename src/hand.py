""" 定义纸牌Card、手牌Hand、一副牌Deck类 """

import random
import itertools
from collections import namedtuple
from copy import deepcopy


Card = namedtuple('Card', ['suit', 'rank'])


class Hand:
    """ 手牌 """
    SUITS = ('♥', '♦', '♣', '♠')
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

    @property
    def cards(self):
        return deepcopy(self._cards)


class Deck(Hand):
    """ 一副完整的牌 (特殊的手牌) """
    def __init__(self) -> None:
        self._cards = [Card(s, r) for s, r
                       in itertools.product(Hand.SUITS, Hand.RANKS)]
        random.shuffle(self._cards)

    def pop(self,):
        return self._cards.pop()


if __name__ == '__main__':
    h1 = Hand([Card('C', '2')])
    h2 = Hand([Card('C', '3')])
    h = h1 + h2
    print(h)

    pass
