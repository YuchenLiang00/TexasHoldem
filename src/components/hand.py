""" 定义纸牌Card、手牌Hand、一副牌Deck类 """

import random
import itertools
from collections import namedtuple
from copy import deepcopy
from typing import Literal
from enum import Enum


Card = namedtuple('Card', ['suit', 'rank'])


class HandType(Enum):
    """ 手牌牌力类型 """

    ROYAL_FLUSH = "Royal Flush"
    STRAIGHT_FLUSH = "Straight Flush"
    FOUR_OF_A_KIND = "Four of a Kind"
    FULL_HOUSE = "Full House"
    FLUSH = "Flush"
    STRAIGHT = "Straight"
    THREE_OF_A_KIND = "Three of a Kind"
    TWO_PAIRS = "Two Pairs"
    ONE_PAIR = "One Pair"
    HIGH_CARD = "High Card"


class Hand:
    """ 手牌 """
    SUITS: tuple = ('♥', '♦', '♣', '♠')
    RANKS: tuple = ('2', '3', '4', '5', '6','7', 
                    '8', '9', 'T', 'J', 'Q', 'K', 'A')
    SUIT: type = Literal['♥', '♦', '♣', '♠']  # type alias
    RANK: type = Literal['2', '3', '4', '5', '6', '7',
                         '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __init__(self, cards: list[Card] = None) -> None:
        self._cards = cards if cards else []

    def __len__(self,):
        return len(self._cards)

    def __getitem__(self, index):
        return self._cards[index]

    def __str__(self):
        l = [s + r for s, r in self._cards]
        return ' '.join(l)

    def __add__(self, other):
        if isinstance(other, Hand):
            return Hand(self._cards + other._cards)
        else:
            raise NotImplementedError(
                f"Can only add Hand class instance, {type(other)} found.")

    def __radd__(self, other):
        """ 为了使sum函数可以作用在hand实例组成的iterable上 """
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __bool__(self):
        return bool(self._cards)

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
