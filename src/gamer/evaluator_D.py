""" 牌力判断 """
from collections import namedtuple
from enum import Enum
from functools import total_ordering
from typing import Optional

from src.components import Card, Hand, LOOKUP_TABLE
from src.gamer.player import Player


HandTypeTuple = namedtuple("HandTypeTuple", ["htype", "hrank"])


@total_ordering
class HandType(Enum):
    """ 手牌牌力类型 """

    ROYAL_FLUSH = HandTypeTuple("Royal Flush", 1)
    STRAIGHT_FLUSH = HandTypeTuple("Straight Flush", 2)
    FOUR_OF_A_KIND = HandTypeTuple("Four of a Kind", 3)
    FULL_HOUSE = HandTypeTuple("Full House", 4)
    FLUSH = HandTypeTuple("Flush", 5)
    STRAIGHT = HandTypeTuple("Straight", 6)
    THREE_OF_A_KIND = HandTypeTuple("Three of a Kind", 7)
    TWO_PAIRS = HandTypeTuple("Two Pair", 8)
    ONE_PAIR = HandTypeTuple("One Pair", 9)
    HIGH_CARD = HandTypeTuple("High Card", 10)

    def __str__(self):
        return self.value.htype

    def __lt__(self, other):
        if isinstance(other, HandType):
            return self.value.hrank < other.value.hrank
        else:
            raise NotImplementedError(
                f"Can only compare HandType class instance, {type(other)} found.")

    def __eq__(self, other):
        if isinstance(other, HandType):
            return self.value.hrank == other.value.hrank
        else:
            raise NotImplementedError(
                f"Can only compare HandType class instance, {type(other)} found.")

    def __hash__(self) -> int:
        return super().__hash__()


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
        l = [str(s) for s in self._cards]
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
"""

# type Hand = list[Card]

class Evaluator:
    """ 牌力判断机 """
    RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
             '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

    def __init__(self, community_cards: dict):
        self.community_cards: Hand = sum(community_cards.values())

        self.ranking_handles = {
            HandType.ROYAL_FLUSH: self.is_royal_flush,
            HandType.STRAIGHT_FLUSH: self.is_straight_flush,
            HandType.FOUR_OF_A_KIND: self.is_four_of_a_kind,
            HandType.FULL_HOUSE: self.is_full_house,
            HandType.FLUSH: self.is_flush,
            HandType.STRAIGHT: self.is_straight,
            HandType.THREE_OF_A_KIND: self.is_three_of_a_kind,
            HandType.TWO_PAIRS: self.is_two_pairs,
            HandType.ONE_PAIR: self.is_one_pair,
        }

        return

    def parse_card(self, card: Card) -> tuple:
        """ Parse suit and rank, return: suit, rank """
        return card.suit, self.RANKS[card.rank]

    def sort_cards(self, cards: list[Card]) -> list[Card]:
        """ 不会修改原列表 """
        return sorted(cards, key=lambda card: self.parse_card(card)[1], reverse=True)

    def evaluate_hand(self, hand: Hand) -> tuple[HandType, Hand]:
        # 更精细的比较：两个同样等级的手牌的大小比
        hand += self.community_cards  # 这里已经是新的对象了
        cards = self.sort_cards(hand.cards)  # 7张

        for hand_type, hand_check in self.ranking_handles.items():
            max_hand: Optional[list[Card]] = None
            # cards 有7张, combo是5张 combo - combination
            for combo in itertools.combinations(cards, 5):
                # 同一副手牌可能既是两对又是葫芦，如果找到先找到两对就返回，则会判断失误
                # 同样的，如果出现三对牌，则要找到最大的两对，
                # 出现可能出现两个葫芦、多个顺子的情形，则需要找出最大的作为手牌返回
                # 精细化，不能简单地使用for循环，应该根据每种情况做不同的处理
                if hand_check(combo):
                    # 存在该牌型
                    if not max_hand or self.compare_hands(combo, max_hand, hand_type) == 1:
                        # 选择最大的牌型组合 更新max_hand
                        max_hand = combo
            if max_hand:
                return hand_type, Hand(self.sort_cards(max_hand))

        # 如果没有找到以上牌型，则返回高牌
        return "High Card", Hand(self.sort_cards(cards)[:5])

    def compare_hands(self, cards1: list[Card], cards2: list[Card], hand_type: HandType) -> int:
        """ 实现两手牌的比较，返回1表示hand1更大，-1表示hand2更大，0表示相等 """
        if not isinstance(hand_type, HandType):
            raise TypeError(f"Wrong input type: {hand_type} found")

        if hand_type in (HandType.ROYAL_FLUSH,
                         HandType.STRAIGHT_FLUSH,
                         HandType.FOUR_OF_A_KIND,
                         HandType.FLUSH,
                         HandType.STRAIGHT,
                         HandType.HIGH_CARD):
            return self._compare_high_cards(cards1, cards2)
        elif hand_type == HandType.FULL_HOUSE:
            return self._compare_full_house(cards1, cards2)
        elif hand_type == HandType.THREE_OF_A_KIND:
            return self._compare_three_of_a_kind(cards1, cards2)
        elif hand_type == HandType.TWO_PAIRS:
            return self._compare_two_pairs(cards1, cards2)
        elif hand_type == HandType.ONE_PAIR:
            return self._compare_one_pair(cards1, cards2)
        else:
            raise ValueError(f"Wrong input hand_type: {hand_type.value} found")

    def find_winners(self, player_hand_info: list[tuple[Player, HandType, Hand]]):
        """ 从各家的手牌中找出胜者 """
        # TODO 找出胜者
        # 按牌力大小排序玩家
        player_hand_info.sort(key=lambda x: (x[1],
                                            self.get_hand_score(x[2])), reverse=True)

        # 返回排序后的玩家列表
        return [player for player, _, _ in player_hand_info]
    
    def get_hand_score():
        return
        

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
    def _compare_high_card(self, cards1: list[Card], cards2: list[Card]) -> int:
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
