from collections import deque
from itertools import chain
import gc
import math
import time
import random
from typing import Optional

from src.components import Action, Deck, Move, Street, Evaluator, Position
from src.gamer import Player, PotManager


class Dealer:
    """ 荷官 """

    def __init__(self, 
                 players: list, 
                 big_blind: int = 20, 
                 small_blind: int = 0) -> None:
        random.shuffle(players)  # 随机打乱玩家顺序
        self.player_queue = deque(players)
        # self.player_list: list[Player] = players
        self.big_blind = big_blind
        self.small_blind = small_blind if small_blind else math.ceil(self.big_blind / 2)
        self.pot_manager = PotManager()

    # 发牌函数
    def deal_cards(self, number) -> list:
        return [self._deck.pop() for _ in range(number)]

    def deal_preflop(self,):
        """ 给玩家发牌 """
        for player in self.player_queue:
            player.set_hand(self.deal_cards(2))
        return

    def play(self):
        """ 完整的一局游戏 """
        # TODO 完善play 的功能
        
        while len(self.player_queue) > 1:
            self.reset_deck()

            # 睡眠机制
            print(f"Players on Board:")
            print("\n".join('\t'.join([str(p), str(p.money)]) 
                            for p in self.player_queue))
            for i in range(1, 4):
                print("\rLoading" + "." * i, end='', flush=True)
                # time.sleep(1)

            for street in Street:
                # 如果是翻前，则给每个人发手牌
                if street == Street.PRE_FLOP:
                    self.set_positions()
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
        print(f"  Winner: {self.player_queue.pop()}  ".center(68, "!"))

    def betting_round(self, street: Street) -> bool:
        """ 一局中的一圈游戏 返回True则没有中途结束 返回False则中途结束游戏"""
        # 每一圈之后重置 如果有盲注，则starting_bet不为0
        current_bet = 0   
        min_raise = 0
        last_raiser = None
        active_players: list[Player] = [p for p in self.player_queue if p not in self.wait_players]
        action_queue: deque[Player] = deque(p for p in active_players
                                            if p.action not in (Action.FOLD, Action.ALL_IN))
        if len(action_queue) == 1: 
            # 只有一位可以行动的玩家，则直接进入河牌圈比大小
            return True
        betted_players = set(active_players)
        if street == Street.PRE_FLOP:
            # 翻前圈，给盲位玩家下注
            rotate_num = self.blind_players_bet(action_queue)
            current_bet = self.big_blind
            min_raise = self.big_blind

            action_queue.rotate(rotate_num)  # 两位玩家都在队列中
            active_players = list(action_queue)
            self.refresh_screen()  # 刷新屏幕，并且也要覆盖掉之前人的手牌和输入的内容


        while action_queue:
            # 翻前强制给SB、BB下注
            # 不能直接遍历这个列表了，因为我们不能允许最后一个加注的人还继续加注。
            player = action_queue.popleft()
            if player is last_raiser:
                continue # 这里continue 和break的作用是一样的

            amount = self.get_player_bet(player)
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
        
        self.pot_manager.update_pots(betted_players)

        # 重置玩家的当前下注额
        for player in active_players:
            if player.action not in (Action.FOLD, Action.ALL_IN):
                player.reset_current_bet()
                player.reset_action()
            else:
                self.wait_players.append(player)

        return True
    
    def get_player_bet(self, player: Player) -> Optional[int]:
        """ 获取玩家的下注量 """
        input(f"\nWaiting Player {player.name} to bet\n"
              "Press Enter to continue...")
        self.refresh_screen()
        print()
        player.show_hand()
        amount = input(f"Bet:")
        try:
            amount = int(amount)
        except ValueError:
            amount = None  # 用户乱输入
        return amount
    
    def blind_players_bet(self, action_queue):
        """ 处理翻前的小盲和大盲下注 """
        sb_player = self.player_queue[0]
        bb_player = self.player_queue[1]
        rotate_num = -2
        # 如果小盲或大盲必须all-in，则移除他们的行动权
        if sb_player.money <= self.small_blind:
            amount = sb_player.money 
            action_queue.remove(sb_player)
            rotate_num += 1
        else:
            amount = self.small_blind
        sb_player.bet(amount=amount, street=Street.PRE_FLOP,
                        current_bet=0, min_raise=0)

        # 如果小盲或大盲必须all-in，则移除他们的行动权
        if bb_player.money <= self.big_blind:
            amount = bb_player.money  
            action_queue.remove(bb_player)
            rotate_num += 1 
        else:
            amount = self.big_blind
        bb_player.bet(amount=amount, street=Street.PRE_FLOP,
                                    current_bet=0, min_raise=0)

        return rotate_num
    
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
        """横向打印一组牌 完善发牌时展示公共牌的流程"""

        print("|  Board Cards  |".center(76, " ")+'\n')
        card_list = []
        for v in self.community_cards.values():
            card_list.extend(v)

        top_lines = "·" + "-" * 4 + "·"
        empty_line = "|" + " " * 4 + "|"
        bottom_lines = "·" + "-" * 4 + "·"

        # 打印牌顶部
        print('  '.join([top_lines for _ in card_list]).center(76, ' '))

        # 打印中间部分
        print('  '.join([f"|{card}  |" for card in card_list]).center(76, ' '))

        for _ in range(2):
            print((' ' * 2).join([empty_line for _ in card_list]).center(76, ' '))

        # 打印牌底部
        print('  '.join([bottom_lines for _ in card_list]).center(76, ' '))

    def eval_hands(self):
        """ 计算全部玩家的手牌大小 """
        # 逐个地将玩家的手牌传入evaluator.evaluate_hand()当中
        print("\n", "  Showdown!  ".center(76, "·"), "\n", sep='')
        player_hand_info = []
        board = list(chain.from_iterable(
            cards for cards in self.community_cards.values()))
        for player in self.player_queue:
            if player.action != Action.FOLD:
                # hand_rank, rank_string, combo = Evaluator.evaluate(player.hand, board)  # type: ignore
                info = Evaluator.evaluate(player.hand, board)  # type: ignore
                player_hand_info.append((player, *info))

        winners = self.find_winners(player_hand_info)  # 找出胜者 ,数字小的手牌大
        for info in player_hand_info:
            player, hand_rank, rank_string, combo = info
            is_winner = True if player in winners else False
            player.show_hand(winner=is_winner)
            print(" ".join(map(str, sorted(combo, reverse=True))), rank_string, sep='\t\t')


    def find_winners(self, player_hand_info):
        ranked_players = sorted(player_hand_info, key=lambda x: x[1])
        winners = []
        # 处理每个底池
        for pot in self.pot_manager.pots:
            # 在这个底池中找到有资格赢得底池的玩家
            eligible_players: list[Player] = [player for player, *_ in ranked_players 
                                              if player in pot.eligible_players]

            # 如果没有资格的玩家，跳过这个底池
            # 我们经常会创建很多空底池，所以需要这个保护机制
            if not eligible_players:
                continue

            # 找出这个底池的最大牌力和对应的玩家
            max_hand_rank = min(hand_rank for p, hand_rank, *_ in player_hand_info 
                                if p in eligible_players)
            winners: list[Player] = [player for player, hand_rank, *_ in player_hand_info 
                       if hand_rank == max_hand_rank and player in eligible_players]
            # pot_winners[pot] = winners
            # 处理底池的分配
            # 分配底池筹码给胜者
            for winner in winners:
                winner.add_chips(round(pot.amount / len(winners)))
        # 返回底池胜者信息
        return winners
    
    def kickoff_losers(self):
        """ 踢掉破产玩家 """
        losers = [p for p in self.player_queue if p.money == 0]
        for loser in losers:
            self.player_queue.remove(loser)
        return
    
    def set_positions(self):
        """ 更新玩家位置 """
        # 为每个玩家分配一个位置
        for i, player in enumerate(self.player_queue):
            player.set_position(Position(i))

        # 将庄家移至队列尾部，为下一轮游戏做准备
        self.player_queue.rotate(-1)

        return

    def refresh_screen(self):
        # 清除屏幕（终端命令）
        # TODO 美化格式化输出
        print("\033[H\033[J", end="")  # 这是清屏的ANSI转义码
        print("\n","     THU Unlimited Texas Hold'em Cash Game Table     ".center(76, '='),"\n",sep="")
        self.show_community_cards()
        
        print("\n",f"|   Total Chips : {self.pot_manager.get_total_chips()}  |".center(76, ' '), sep="")

        print(f"\n{'Player':<9}  {'Money':<5} | {'Pre-Flop':^12} | "
              f"{'Flop':^12} | {'Turn':^12} | {'River':^12}")
        print("-"*16, "·", "-"*12, "·", "-"*12, "·", "-"*12, "·", "-"*12)

        for player in self.player_queue:
            moves = " | ".join([str(move) for move in player.show_move()])
            name = player.name if len(player.name) <= 5 else player.name[:4] + "+" 
            print(f"{name:<5} {player.position:>4} {player.money:>5} | {moves}")

        print("-"*16, "·", "-"*12, "·", "-"*12, "·", "-"*12, "·", "-"*12)


    def reset_deck(self):
        """ 重置牌桌 """
        # 完善销毁机制，记得清空玩家的可变游戏信息
        self._deck = Deck()
        self.community_cards = {Street.FLOP: ['??'] * 3,
                                Street.TURN: ['??'],
                                Street.RIVER: ['??']}
        self.pot_manager.reset_pot()
        self.wait_players = []
        self.set_positions()
        for player in self.player_queue:
            player.reset_action()
            player.reset_current_bet()
            player.reset_position()

        gc.collect()


if __name__ == '__main__':
    pass
