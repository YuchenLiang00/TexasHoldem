""" 牌力判断 """
from typing import Literal, Optional
from src.hand import Card, Hand
import itertools


class Evaluator:
    """ 牌力判断机 """
    RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
             '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    HAND_TYPE = Literal["Royal Flush", "Straight Flush", "Four of a Kind", "Full House",
                        "Flush", "Straight", "Three of a Kind", "Two Pairs", "One Pair", "High Card"]

    def __init__(self, community_cards: dict):
        self.community_cards = sum(community_cards.values())

        self.ranking_handles = {
            "Royal Flush": self.is_royal_flush,
            "Straight Flush": self.is_straight_flush,
            "Four of a Kind": self.is_four_of_a_kind,
            "Full House": self.is_full_house,
            "Flush": self.is_flush,
            "Straight": self.is_straight,
            "Three of a Kind": self.is_three_of_a_kind,
            "Two Pairs": self.is_two_pairs,
            "One Pair": self.is_one_pair,
        }

        return

    def parse_card(self, card: Card) -> tuple[Hand.SUIT, int]:
        """ Parse suit and rank, return: suit, rank """
        return card.suit, self.RANKS[card.rank]

    def sort_cards(self, cards: list[Card]) -> list[Card]:
        """ 不会修改原列表 """
        return sorted(cards, key=lambda card: self.parse_card(card)[1], reverse=True)

    def evaluate_hand(self, hand: Hand) -> tuple[str, Hand]:
        # 更精细的比较：两个同样等级的手牌的大小比
        hand += self.community_cards  # 这里已经是新的对象了
        cards = self.sort_cards(hand.cards)  # 7张

        for hand_check, hand_type in self.ranking_handles.items():
            max_hand: Optional[list[Card]] = None
            # combo - combination
            for combo in itertools.combinations(cards, 5):
                # 同一副手牌可能既是两对又是葫芦，如果找到先找到两对就返回，则会判断失误
                # 同样的，如果出现三对牌，则要找到最大的两对，
                # 出现可能出现两个葫芦、多个顺子的情形，则需要找出最大的作为手牌返回
                # 精细化，不能简单地使用for循环，应该根据每种情况做不同的处理
                result: tuple[bool, list[Card]] = hand_check(combo)
                if result[0]:
                    # 存在该牌型
                    if not max_hand or self.compare_hands(result[1], max_hand, hand_type) == 1:
                        # 选择最大的牌型组合 更新max_hand
                        max_hand = result[1]
            if max_hand:
                return hand_type, Hand(self.sort_cards(max_hand))

        # 如果没有找到以上牌型，则返回高牌
        return "High Card", Hand(self.sort_cards(cards)[:5])

    def compare_hands(self, cards1: list[Card], cards2: list[Card], hand_type: HAND_TYPE) -> int:
        """ 实现两手牌的比较，返回1表示hand1更大，-1表示hand2更大，0表示相等 """
        if hand_type in ("Straight Flush", "Four of a Kind", "Flush", "Straight", "High Card"):
            return self._compare_high_cards(cards1, cards2)
        elif hand_type == "Full House":
            return self._compare_full_house(cards1, cards2)
        elif hand_type == "Three of a Kind":
            return self._compare_three_of_a_kind(cards1, cards2)
        elif hand_type == "Two Pairs":
            return self._compare_two_pairs(cards1, cards2)
        elif hand_type == "One Pair":
            return self._compare_one_pair(cards1, cards2)
        else:
            raise ValueError(f"Wrong input hand_type, {hand_type} found")

    def find_winner(self):
        # TODO 找出胜者
        pass

    # == 检测函数 ==
    # 以下函数的返回值类型均为bool，输入均为5张牌
    def is_royal_flush(self, cards: list[Card]):
        if self.is_straight_flush(cards):
            if self.parse_card(self.sort_cards(cards)[0])[1] == 14:
                return True
        return False

    def is_straight_flush(self, cards: list[Card]):
        if self.is_flush(cards) and self.is_straight(cards):
            return True
        return False

    def is_four_of_a_kind(self, cards: list[Card]):
        return self.has_n_of_a_kind(cards, 4)

    def is_full_house(self, cards: list[Card]):
        count = {}
        for _, rank in map(self.parse_card, cards):
            # 统计5张牌中各个数字出现的频率
            count[rank] = count.get(rank, 0) + 1
        values = list(count.values())
        return 3 in values and 2 in values

    def is_flush(self, cards: list[Card]):
        suits = [suit for suit, _ in map(self.parse_card, cards)]
        return len(set(suits)) == 1

    def is_straight(self, cards: list[Card]):
        # 先去重 这是一个由纯数字组成的set
        # reverse=True 表示降序排列，大的在前
        ranks = sorted(set([rank for _, rank
                            in map(self.parse_card, cards)]), reverse=True)

        if 14 in ranks:
            # 考虑 A 作为最小值的情况
            ranks.append(1)  # 在最尾端
        if len(ranks) < 5:
            # 没有5张不一样的牌
            return False
        # 检查连续的5张牌
        for i in range(len(ranks) - 4):
            if ranks[i] - ranks[i + 4] == 4:
                # 非常经典的算法，从有顺序的列表中计算一段窗口长度为5的子窗口
                # 如果子窗口对应的数字差为5，则一定是顺子
                return True
        return False

    def is_three_of_a_kind(self, cards: list[Card]):
        return self.has_n_of_a_kind(cards, 3)

    def is_two_pairs(self, cards: list[Card]):
        # 不能用has_n_of_a_kind()来判断
        pairs = 0
        count = {}
        for _, rank in map(self.parse_card, cards):
            # 获取每个数字的拥有的张数
            count[rank] = count.get(rank, 0) + 1
        for v in count.values():
            if v == 2:
                pairs += 1
        return pairs == 2

    def is_one_pair(self, cards: list[Card]):
        return self.has_n_of_a_kind(cards, 2)

    def has_n_of_a_kind(self, cards, n) -> bool:
        count = {}
        for _, rank in map(self.parse_card, cards):
            count[rank] = count.get(rank, 0) + 1
        return any(v >= n for v in count.values())

    # == 更细致的检测函数 ==
    # 两手同样等级的牌的比较，都是5张牌
    def _compare_high_cards(self, cards1: list[Card], cards2: list[Card]) -> int:
        """ 高牌的比较，适用于同花顺、四条、同花、顺子、高牌 """
        cards1 = self.sort_cards(cards1)  # 直接把一个列表给传进来了，修改了原列表
        cards2 = self.sort_cards(cards2)
        for c1, c2 in zip(cards1, cards2):
            # 遍历每一张牌 得到数字
            r1, r2 = self.parse_card(c1)[1], self.parse_card(c2)[1]
            if r1 > r2:
                return 1
            elif r1 < r2:
                return -1
        return 0  # 所有的数字都相同

    def _compare_full_house(self, cards1: list[Card], cards2: list[Card]) -> int:
        """ 葫芦的比较 """
        rank_counts1 = self.get_rank_counts(cards1)
        rank_counts2 = self.get_rank_counts(cards2)

        three_rank1 = max(
            rank for rank, count in rank_counts1.items() if count == 3)
        three_rank2 = max(
            rank for rank, count in rank_counts2.items() if count == 3)

        if three_rank1 != three_rank2:
            return 1 if three_rank1 > three_rank2 else -1

        pair_rank1 = max(
            rank for rank, count in rank_counts1.items() if count == 2)
        pair_rank2 = max(
            rank for rank, count in rank_counts2.items() if count == 2)

        return 1 if pair_rank1 > pair_rank2 else -1 if pair_rank1 < pair_rank2 else 0

    def _compare_three_of_a_kind(self, cards1: list[Card], cards2: list[Card]) -> int:
        """ 三条的比较 """
        rank_counts1 = self.get_rank_counts(cards1)
        rank_counts2 = self.get_rank_counts(cards2)

        three_rank1 = max(
            rank for rank, count in rank_counts1.items() if count == 3)
        three_rank2 = max(
            rank for rank, count in rank_counts2.items() if count == 3)

        if three_rank1 != three_rank2:
            return 1 if three_rank1 > three_rank2 else -1

        return self._compare_high_card(cards1, cards2)

    def _compare_two_pairs(self, cards1: list[Card], cards2: list[Card]) -> int:
        """ 两对的比较 """
        rank_counts1 = self.get_rank_counts(cards1)
        rank_counts2 = self.get_rank_counts(cards2)

        pairs1 = sorted(
            [rank for rank, count in rank_counts1.items() if count == 2], reverse=True)
        pairs2 = sorted(
            [rank for rank, count in rank_counts2.items() if count == 2], reverse=True)

        for r1, r2 in zip(pairs1, pairs2):
            if r1 != r2:
                return 1 if r1 > r2 else -1

        return self._compare_high_card(cards1, cards2)

    def _compare_one_pair(self, cards1: list[Card], cards2: list[Card]) -> int:
        """ 一对的比较 """
        rank_counts1 = self.get_rank_counts(cards1)
        rank_counts2 = self.get_rank_counts(cards2)

        pair_rank1 = max(
            rank for rank, count in rank_counts1.items() if count == 2)
        pair_rank2 = max(
            rank for rank, count in rank_counts2.items() if count == 2)

        if pair_rank1 != pair_rank2:
            return 1 if pair_rank1 > pair_rank2 else -1

        return self._compare_high_card(cards1, cards2)

    def get_rank_counts(self, cards: list[Card]) -> dict:
        """ 各种数值牌的数量 """
        rank_counts = {}
        for card in cards:
            rank = self.parse_card(card)[1]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        return rank_counts
