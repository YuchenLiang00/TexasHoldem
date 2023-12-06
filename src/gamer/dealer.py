""" 存储发牌等相关信息 """

from __future__ import annotations
from itertools import chain
import gc

from src.components import Action, Deck, Hand, Move, Pot, Street
from src.components.evaluator import Evaluator
from src.gamer.player import Player  # 非常特殊，需要导入同级别目录下的其他文件


class Dealer:
    """ 荷官 """

    def __init__(self, players: list, big_blind: int = 20) -> None:
        self.player_list: list[Player] = players
        self.big_blind = big_blind
        self.pot = Pot()

    # 发牌函数
    def deal_cards(self, number) -> list:
        return [self._deck.pop() for _ in range(number)]

    def deal_preflop(self,):
        """ 给玩家发牌 """
        for player in self.player_list:
            player.set_hand(self.deal_cards(2))
        return

    def play(self):
        """ 完整的一局游戏 """
        # TODO 完善play 的功能
        self.reset_deck()
        for street in Street:
            # 如果是翻前，则给每个人发手牌
            if street == Street.PRE_FLOP:
                self.deal_preflop()
            else:
                # 确定本轮要发的公共牌张数
                card_num = 3 if street == Street.FLOP else 1
                self.community_cards[street] = self.deal_cards(card_num)

            self.refresh_screen()
            self.betting_round(street)  # 可能中途结束

        # 河牌圈结束 或中途结束
        # TODO evaluate hands
        # TODO 找出胜者，分钱，踢出破产的玩家

        self.eval_hands()
        input("Press Enter to continue...")

    def betting_round(self, street, starting_bet: int = 0) -> bool:
        """ 一局中的一圈游戏 返回True则没有中途结束 返回False则中途结束游戏"""
        # TODO betting_round 逻辑完善
        current_bet = starting_bet  # 每一圈之后重置
        min_raise = starting_bet  # 如果有盲注，则starting_bet不为0
        # TODO 彩池金额维护，升盲等
        while True:
            for player in self.player_list:
                if player.action not in (Action.FOLD, Action.ALL_IN):
                    # 获取玩家的行动，例如使用 input() 函数或GUI组件
                    player.show_hand()
                    amount = input(f"Bet:")
                    try:  # Sanity check
                        # TODO 下注量必须比大盲大
                        amount = int(amount)
                    except ValueError:
                        amount = None  # 用户乱输入
                    move: Move = player.bet(amount=amount, street=street,
                                            current_bet=current_bet, min_raise=min_raise)

                    # 根据行动更新 current_bet, min_raise 等
                    current_bet, min_raise = \
                        self.examine_player_move(move, current_bet, min_raise)
                else:
                    # Fold, ALL-IN 短路机制，把后面的street都标记成Fold
                    pass

                self.refresh_screen()  # 刷新屏幕，并且也要覆盖掉之前人的手牌和输入的内容
            # 第一轮所有玩家行动结束
            # 判断是不是只有一个人在场上
            if len([p for p in self.player_list if p.action != Action.FOLD]) < 2:
                # 游戏结束
                return False
            # 不止一个人在场上
            # 判断是不是所有在场玩家都下注整齐
            if all(p.current_bet == current_bet for p in self.player_list
                   if p.action not in (Action.FOLD, Action.ALL_IN)):
                # 本圈结束
                break

        # 重置玩家的当前下注额
        for player in self.player_list:
            if player.action != Action.FOLD:
                player.reset_current_bet()
                player.reset_action()

        return True

    def examine_player_move(self,
                            move: Move,
                            current_bet: int,
                            min_raise: int) -> tuple[int, int]:
        """ 检查玩家的下注操作 维护并返回current_bet, min_raise """
        # TODO
        if move.action in (Action.FOLD, Action.CHECK, Action.CALL):
            # 玩家call，check，fold无需修改current_bet 和min_raise
            pass
        elif move.action == Action.RAISE:
            # 玩家加注
            min_raise = move.amount - current_bet  # 首先修改加注增量
            current_bet = move.amount
        elif move.action == Action.ALL_IN:
            # 判断是否构成call、raise
            if move.amount <= current_bet:
                # all-in，但不足跟注
                pass
            elif current_bet < move.amount < current_bet + min_raise:
                # all-in，超过call但不足加注
                # 同时修改加注增量和current_bet，使得加注总量不变
                min_raise = current_bet + min_raise - move.amount
                current_bet = move.amount  # 跟注要跟大的，但是加注总量不变
            elif move.amount >= current_bet + min_raise:
                # all-in to raise,视为raise
                min_raise = move.amount - current_bet
                current_bet = move.amount
            else:
                raise ValueError(f"Invalid move amount: {move.amount}")
        else:
            raise NotImplementedError(
                f"Unable to examine move action: {move.action}")

        return current_bet, min_raise

    def show_community_cards(self):
        # TODO 完善发牌时展示公共牌的流程
        print("Community Cards: ", end=" ")
        for k, v in self.community_cards.items():
            print(k, v, sep=' ', end='\t')
        print()

    def eval_hands(self):
        """ 计算全部玩家的手牌大小 """
        # 逐个地将玩家的手牌传入evaluator.evaluate_hand()当中
        print("===  Show Hands!  ===".center(68, "-"))
        player_hand_info = []
        board = list(chain.from_iterable(
            cards for cards in self.community_cards.values()))
        for player in self.player_list:
            if player.action != Action.FOLD:
                # hand_type: HandType; hand:Hand = evaluator.evaluate_hand(player.hand)
                hand_rank, rank_string, combo = Evaluator.evaluate(
                    player.hand, board)  # type: ignore
                player.show_hand()
                print(" ".join(map(str, sorted(combo, reverse=True))),
                      rank_string, sep='\t')
                player_hand_info.append((player, hand_rank))

        winners = self.find_winners(player_hand_info)  # TODO 找出胜者 ,数字小的手牌大

    def find_winners(self, player_hand_info):
        ranked_players = sorted(player_hand_info, key=lambda x: x[1])
        return dict(ranked_players)

    def refresh_screen(self):
        # 清除屏幕（终端命令）
        # TODO 美化格式化输出
        print("\033[H\033[J", end="")  # 这是清屏的ANSI转义码
        self.show_community_cards()
        print(f"{'Player':<10} {'Money':<5} {'Pre-Flop':<12} "
              f"{'Flop':<12} {'Turn':<12} {'River':<12}")
        for player in self.player_list:
            moves = " ".join([str(move) for move in player.show_move()])
            print(f"{player.name:<10} {player.money:>5} {moves}")

    def reset_deck(self):
        """ 重置牌桌 """
        # TODO 完善销毁机制，记得清空玩家的可变游戏信息
        self._deck = Deck()
        self.community_cards = {Street.FLOP: ['??'] * 3,
                                Street.TURN: ['??'],
                                Street.RIVER: ['??']}
        self.pot.reset_pot()
        for player in self.player_list:
            player.reset_action()
            player.reset_current_bet()

        gc.collect()


if __name__ == '__main__':
    pass
