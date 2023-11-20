""" 存储发牌等相关信息 """

from collections import namedtuple
import itertools
import random
import gc

from src.hand import Deck, Hand
from src.player import Player


class Dealer:
    def __init__(self, players: list[Player]) -> None:
        self.player_list = players
        self._deck = Deck()

    # 发牌函数
    def deal_cards(self, number) -> Hand:
        return Hand([self._deck.pop() for _ in range(number)])
    
    def deal_preflop(self,):
        self.comminity_cards = Hand()
        for player in self.player_list:
            player.set_hand(self.deal_cards(2))
        return
    
    def deal_flop(self):
        self.comminity_cards += self.deal_cards(3)

    def deal_turn(self):
        self.comminity_cards += self.deal_cards(1)
    
    def deal_river(self):
        self.comminity_cards += self.deal_cards(1)
    
    def show_comminity_cards(self):
        # print(f"   FLOP   TURN  RIVER")
        print("Comminity Cards: ",end="")
        self.comminity_cards.show()

    def reset_deck(self):
        self._deck = Deck()
        self.comminity_cards = []
        gc.collect()


if __name__ == '__main__':
    pass
# 示例：发牌
# player_cards = dealer.deal_cards(2)
# community_cards = dealer.deal_cards(5)

# # 合并玩家和公共牌
# all_cards = player_cards + community_cards


# # 示例：评估手牌
# best_hand = dealer.evaluate_hand(all_cards)

# # 打印结果（仅作示例）
# print("玩家的牌:", player_cards)
# print("公共牌:", community_cards)
# print("最强手牌:", best_hand)
