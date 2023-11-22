""" 存储发牌等相关信息 """

import gc

from src.hand import Deck, Hand
from src.player import Player, Move
from src.evaluator import Evaluator


class Dealer:
    """ 荷官 """
    STREETS: tuple = ('Pre-Flop', 'Flop', 'Turn', 'River')

    def __init__(self, players: list[Player], big_blind: int = 20) -> None:
        self.player_list = players
        self.big_blind = big_blind

    # 发牌函数
    def deal_cards(self, number) -> Hand:
        return Hand([self._deck.pop() for _ in range(number)])

    def deal_preflop(self,):
        """ 给玩家发牌 """
        for player in self.player_list:
            player.set_hand(self.deal_cards(2))
        return

    def get_players_hands(self) -> list[Hand]:
        """ 
        获取所有玩家的手牌 
        返回是一个包含着hand的list 每个hand是一个玩家的手牌
        目的是传入evaluator参与计算
        """
        return [player._hand for player in self.player_list]
    
    def play(self):
        """ 完整的一局游戏 """
        # TODO 完善play 的功能
        self.reset_deck()
        for street in self.STREETS:
            # 如果是翻前，则给每个人发手牌
            if street == 'Pre-Flop':
                self.deal_preflop()
            self.refresh_screen()
            self.betting_round(street)  # 可能中途结束

            if street != 'Pre-Flop':
                # 确定本轮要发的公共牌张数
                card_num = 3 if street == 'Flop' else 1
                self.community_cards[street] = self.deal_cards(card_num)
        
        # 河牌圈结束 或中途结束
        # TODO 找出胜者，分钱，踢出破产的玩家

    def betting_round(self, street, starting_bet: int = 0) -> bool:
        """ 一局中的一圈游戏 返回True则没有中途结束 返回False则中途结束游戏"""
        # 
        # TODO
        current_bet = starting_bet
        min_raise = starting_bet

        while True:
            for player in self.player_list:
                if player.action == 'Fold':
                    continue

                # 获取玩家的行动，例如使用 input() 函数或GUI组件
                player.show_hands()
                print(f"Player {player._name} Bet:")
                amount = input()
                # 我们在Player类内完成amount的分类和检查
                move: Move = player.bet(amount=amount, street=street,
                                        current_bet=current_bet, min_raise=min_raise)

                # 根据行动更新 current_bet, min_raise 等
                self.examine_player_move(move)

                self.refresh_screen()  # 刷新屏幕，并且也要覆盖掉之前人的手牌和输入的内容
            # 第一轮所有玩家行动结束
            # 判断是不是只有一个人在场上
            if len([p for p in self.player_list
                    if p.action != 'Fold']) < 2:
                # 游戏结束
                return False
            # 不止一个人在场上
            # 判断是不是所有在场玩家都下注整齐
            if all(p.current_bet == current_bet
                   for p in self.player_list
                   if p.action != 'Fold'):
                # 本圈结束
                break

        # 重置玩家的当前下注额
        for player in self.player_list:
            player.reset_current_bet()
        return True

    def examine_player_move(self, move: Move):
        """ 检查玩家的下注操作 适时修改current_bet, min_raise等属性 """
        if move.action == 'Raise':
            # 加注的话
            pass
        elif move.action == 'ALL-IN':

            pass
        elif move.action == 'Fold':
            # TODO Fold 应该有短路机制，把后面的street都标记成Fold
            pass
        return

    def show_community_cards(self):
        # TODO 完善发牌时展示公共牌的流程
        print("Community Cards: ", end=" ")
        for k, v in self.community_cards.items():
            print(k, v, sep=' ', end='\t')
        print()

    def refresh_screen(self):
        # 清除屏幕（终端命令）
        print("\033[H\033[J", end="")  # 这是清屏的ANSI转义码
        self.show_community_cards()
        print("Player\t Money\t" + "\t".join(self.STREETS))
        for player in self.player_list:
            print(player._name+'\t', player._money,
                  player.show_move(), sep=' ')

    def eval_hands(self):
        """ 计算全部玩家的手牌大小 """
        evaluator = Evaluator(self.community_cards)
        # 逐个地将玩家的手牌传入evaluator.evaluate_hand()当中
        print("  ------==  Show Hands!  ==------  ")
        for player in self.player_list:
            hand_name, combo = evaluator.evaluate_hand(player._hand)
            player.show_hands()
            print(combo, hand_name, sep='\t')
            
        winner = evaluator.find_winner() # TODO

    def reset_deck(self):
        """ 重置牌桌 """
        # TODO 完善销毁机制，记得清空玩家的可变游戏信息
        self._deck = Deck()
        self.community_cards = {'Flop': Hand(['??'] * 3),
                                'Turn': Hand(['??']),
                                'River': Hand(['??'])}

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
