""" 定义纸牌Card、手牌Hand、一副牌Deck类 """

import random
import itertools


from src.components import Card


Hand = list[Card]

class Deck:
    """ 一副完整的牌 (特殊的手牌) """
    SUITS: tuple = ('♥', '♦', '♣', '♠')
    RANKS: tuple = ('2', '3', '4', '5', '6','7',
                    '8', '9', 'T', 'J', 'Q', 'K', 'A')
    def __init__(self) -> None:
        self._cards = [Card(s, r) for s, r
                       in itertools.product(Deck.SUITS, Deck.RANKS)]
        random.shuffle(self._cards)

    def pop(self,):
        return self._cards.pop()


if __name__ == '__main__':


    pass
