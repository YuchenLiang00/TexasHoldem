""" 存储发牌等相关信息 """

import gc

from src.hand import Deck, Hand
from src.player import Player
from src.evaluator import Evaluator


STREETS = ('Pre-Flop', 'Flop', 'Turn', 'River',)


class Dealer:
    def __init__(self, players: list[Player], big_blind:int=20) -> None:
        self.player_list = players
        self._deck = Deck()
        self.big_blind = big_blind

    # 发牌函数
    def deal_cards(self, number) -> Hand:
        return Hand([self._deck.pop() for _ in range(number)])

    def deal_preflop(self,):
        self.community_cards = {'Flop': Hand(['??'] * 3),
                                'Turn': Hand(['??']), 
                                'River': Hand(['??'])}
        for player in self.player_list:
            player.set_hand(self.deal_cards(2))
        return

    def get_players_hands(self) -> list:
        return [player.hand for player in self.player_list]

    def play(self):
        # TODO 完善play 的功能
        # TODO 河牌圈还要再下注一次，下注完之后还要打印信息
        self.deal_preflop()
        fold_players:list[Player] = []
        for street in STREETS[1:]:
            self.refresh_screen()
            card_num = 3 if street == 'Flop' else 1
            while True:
                # 所有玩家行动结束退出循环
                for player in self.player_list:
                    amount = int(input(f"Player {player.name} Bet:"))
                    # TODO Sanity check
                    status = player.bet(amount=amount, street=street)
                    if status == 'Fold':
                        fold_players.append(player)
                break
            self.community_cards[street] = self.deal_cards(card_num)

    def show_community_cards(self):
        # TODO 完善发牌时展示公共牌的流程
        # print(f"   FLOP   TURN  RIVER")
        print("Community Cards: ", end=" ")
        for k, v in self.community_cards.items():
            print(k, v, sep=' ',end='\t')

        print()
            
    def refresh_screen(self):
        # 清除屏幕（终端命令）
        print("\033[H\033[J", end="")  # 这是清屏的ANSI转义码
        self.show_community_cards()
        print("Player\t Money\t" + "\t".join(STREETS))
        for player in self.player_list:
            print(player.name+'\t',player.money, player.show_move(), sep=' ')

    def eval_hands(self):
        """ 计算全部玩家的手牌大小 """
        evaluator = Evaluator(self.community_cards)
        # 逐个地将玩家的手牌传入evaluator.evaluate_hand()当中
        print("  ------==  Show Hands!  ==------  ")
        for player in self.player_list:
            hand_name, combo = evaluator.evaluate_hand(player.hand)
            player.show_hands()
            print(combo, hand_name, sep='\t')

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
