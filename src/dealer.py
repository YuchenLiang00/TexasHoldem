""" 存储发牌等相关信息 """


from collections import deque
from itertools import chain
import gc
import time

from src.components import Action, Deck, Hand, Move, Street, Evaluator
from src.gamer import Player, PotManager


class Dealer:
    """ 荷官 """

    def __init__(self, players: list, big_blind: int = 20) -> None:
        self.player_list: list[Player] = players
        self.big_blind = big_blind
        self.pot_manager = PotManager()

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
        while self.player_list:
            self.reset_deck()

            # 睡眠机制
            print(f"Players on Board:\n" + "\n".join(repr(s) for s in self.player_list))
            for i in range(1, 4):
                print("\rLoading" + "." * i, end='', flush=True)
                time.sleep(1)

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
            self.refresh_screen()
            self.eval_hands()
            self.kickoff_losers()
            input("Press Enter to continue...")

    def betting_round(self, street, starting_bet: int = 0) -> bool:
        """ 一局中的一圈游戏 返回True则没有中途结束 返回False则中途结束游戏"""
        current_bet = starting_bet  # 每一圈之后重置
        min_raise = starting_bet  # 如果有盲注，则starting_bet不为0
        last_raiser = None
        active_players: list[Player] = [p for p in self.player_list if p not in self.wait_players]
        action_queue = deque(p for p in active_players
                             if p.action not in (Action.FOLD, Action.ALL_IN))
        if len(action_queue) == 1: 
            return True

        while action_queue:
            # 不能直接遍历这个列表了，因为我们不能允许最后一个加注的人还继续加注。
            player = action_queue.popleft()
            if player is last_raiser:
                continue # 这里continue 和break的作用是一样的
            player.show_hand()
            amount = input(f"Bet:")
            # 获取玩家的行动，例如使用 input() 函数或GUI组件
            try:  # Sanity check
                # TODO 下注量必须比大盲大
                amount = int(amount)
            except ValueError:
                amount = None  # 用户乱输入
            move: Move = player.bet(amount=amount, street=street,
                                    current_bet=current_bet, min_raise=min_raise)

            # 如果玩家加注，则重置队列，让其他玩家有机会相应
            if move.amount > current_bet:
                last_raiser = player
                for p in active_players:
                    if (p not in action_queue and 
                        p.action not in (Action.FOLD, Action.ALL_IN, Action.RAISE)):
                        action_queue.append(p)
                if move.action != Action.ALL_IN:
                    action_queue.append(player)

            # 根据行动更新 current_bet, min_raise 等
            current_bet, min_raise = self.examine_player_move(move, current_bet, min_raise)
            self.refresh_screen()  # 刷新屏幕，并且也要覆盖掉之前人的手牌和输入的内容

        self.pot_manager.update_pots(active_players)
        # for pot in self.pot_manager.pots:
        #     print(pot)
        # input()

        # 重置玩家的当前下注额
        for player in active_players:
            if player.action not in (Action.FOLD, Action.ALL_IN):
                player.reset_current_bet()
                player.reset_action()
            else:
                self.wait_players.append(player)

        return True

    def examine_player_move(self,
                            move: Move,
                            current_bet: int,
                            min_raise: int) -> tuple[int, int]:
        """ 检查玩家的下注操作 维护并返回current_bet, min_raise """
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
        # 完善发牌时展示公共牌的流程
        print("Community Cards: ", end=" ")
        for k, v in self.community_cards.items():
            print(k, v, sep=' ', end='\t')
        print()

    def eval_hands(self):
        """ 计算全部玩家的手牌大小 """
        # 逐个地将玩家的手牌传入evaluator.evaluate_hand()当中
        print("===  Showdown!  ===".center(68, "-"))
        player_hand_info = []
        board = list(chain.from_iterable(
            cards for cards in self.community_cards.values()))
        for player in self.player_list:
            if player.action != Action.FOLD:
                hand_rank, rank_string, combo = Evaluator.evaluate(player.hand, board)  # type: ignore
                player.show_hand()
                print(" ".join(map(str, sorted(combo, reverse=True))),
                      rank_string, sep='\t')
                player_hand_info.append((player, hand_rank))

        winners = self.find_winners(player_hand_info)  # 找出胜者 ,数字小的手牌大

    def find_winners(self, player_hand_info):
        ranked_players = sorted(player_hand_info, key=lambda x: x[1])

        # 处理每个底池
        for pot in self.pot_manager.pots:
            # 在这个底池中找到有资格赢得底池的玩家
            eligible_players: list[Player] = [player for player, _ in ranked_players 
                                              if player in pot.eligible_players]

            # 如果没有资格的玩家，跳过这个底池
            # 我们经常会创建很多空底池，所以需要这个保护机制
            if not eligible_players:
                continue

            # 找出这个底池的最大牌力和对应的玩家
            max_hand_rank = min(hand_rank for p, hand_rank in player_hand_info 
                                if p in eligible_players)
            winners: list[Player] = [player for player, hand_rank in player_hand_info 
                       if hand_rank == max_hand_rank and player in eligible_players]
            # pot_winners[pot] = winners
            # 处理底池的分配
            # 分配底池筹码给胜者
            for winner in winners:
                winner.add_chips(round(pot.amount / len(winners)))
                
        # 返回底池胜者信息
        return 
    
    def kickoff_losers(self):
        losers = [p for p in self.player_list if p.money == 0]
        for loser in losers:
            self.player_list.remove(loser)

    def refresh_screen(self):
        # 清除屏幕（终端命令）
        # TODO 美化格式化输出
        print("\033[H\033[J", end="")  # 这是清屏的ANSI转义码
        self.show_community_cards()
        
        print(f"\nTotal Chips : {self.pot_manager.get_total_chips()}")
        print(f"\n{'Player':<10} {'Money':<5} {'Pre-Flop':<12} "
              f"{'Flop':<12} {'Turn':<12} {'River':<12}")
        for player in self.player_list:
            moves = " ".join([str(move) for move in player.show_move()])
            print(f"{player.name:<10} {player.money:>5} {moves}")

    def reset_deck(self):
        """ 重置牌桌 """
        # 完善销毁机制，记得清空玩家的可变游戏信息
        self._deck = Deck()
        self.community_cards = {Street.FLOP: ['??'] * 3,
                                Street.TURN: ['??'],
                                Street.RIVER: ['??']}
        self.pot_manager.reset_pot()
        self.wait_players = []
        for player in self.player_list:
            player.reset_action()
            player.reset_current_bet()

        gc.collect()


if __name__ == '__main__':
    pass
