""" 存储发牌等相关信息 """

from collections import namedtuple
import itertools
import random
import gc

from src.hand import Deck, Hand
from src.player import Player
from src.evaluator import Evaluator


class Dealer:
    def __init__(self, players: list[Player]) -> None:
        self.player_list = players
        self._deck = Deck()

    # 发牌函数
    def deal_cards(self, number) -> Hand:
        return Hand([self._deck.pop() for _ in range(number)])

    def deal_preflop(self,):
        self.community_cards = Hand()
        for player in self.player_list:
            player.set_hand(self.deal_cards(2))
        return

    def get_players_hands(self) -> list:
        return [player.hand for player in self.player_list]

    def deal_flop(self):
        self.community_cards += self.deal_cards(3)

    def deal_turn(self):
        self.community_cards += self.deal_cards(1)

    def deal_river(self):
        self.community_cards += self.deal_cards(1)

    def show_community_cards(self):
        # print(f"   FLOP   TURN  RIVER")
        print("Community Cards: ", end="")
        self.community_cards.show()

    def eval_hands(self):
        """ 计算全部玩家的手牌大小 """
        evaluator = Evaluator(self.community_cards, self.get_players_hands())
        player_combo = [evaluator.evaluate_hand(
            player.hand) for player in self.player_list]
        print(player_combo)

    def reset_deck(self):
        self._deck = Deck()
        self.community_cards = []
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
