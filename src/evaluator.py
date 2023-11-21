from sympy import reduced
from src.hand import Card, Hand
import itertools


class Evaluator:
    RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
             '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

    def __init__(self, community_cards:dict):
        self.community_cards = Hand()
        for hand in community_cards.values():
            self.community_cards += hand
            
        self.RANKING_HANDLES = [
            (self.is_straight_flush, "Straight Flush"),
            (self.is_four_of_a_kind, "Four of a Kind"),
            (self.is_full_house, "Full House"),
            (self.is_flush, "Flush"),
            (self.is_straight, "Straight"),
            (self.is_three_of_a_kind, "Three of a Kind"),
            (self.is_two_pairs, "Two Pairs"),
            (self.is_one_pair, "One Pair")
        ]
        return

    def evaluate_hand(self, hand: Hand) -> tuple[str, Hand]:
        # TODO 更精细的比较：两个同样等级的手牌的大小比较
        hand += self.community_cards  # 这里已经是新的对象了
        cards = self.sort_cards(hand.cards)  # 7张

        for hand_check, hand_name in self.RANKING_HANDLES:
            for combo in itertools.combinations(hand, 5):
                # 应该是不会改变手牌的
                # 精细化，不能简单地使用for循环，应该根据每种情况做不同的处理
                if hand_check(combo):
                    return hand_name, Hand(self.sort_cards(combo))

        # 如果没有找到以上牌型，则返回高牌
        return "High Card", Hand(self.sort_cards(cards)[:5])

    @classmethod
    def parse_card(cls, card: Card) -> tuple:
        """ Parse suit and rank, return: suit, rank """
        return card.suit, cls.RANKS[card.rank]

    @classmethod
    def sort_cards(cls, cards) -> list[Card]:
        cards: list = cards
        return sorted(cards, key=lambda card: cls.parse_card(card)[1], reverse=True)

    # == 检测函数 ==
    @classmethod
    def is_straight_flush(cls, cards: list[Card]):
        if cls.is_flush(cards) and cls.is_straight(cards):
            return True
        return False

    @classmethod
    def is_four_of_a_kind(cls, cards: list[Card]):
        return cls.has_n_of_a_kind(cards, 4)

    @classmethod
    def is_full_house(cls, cards: list[Card]):
        count = {}
        for _, rank in map(cls.parse_card, cards):
            count[rank] = count.get(rank, 0) + 1
        values = list(count.values())
        return 3 in values and 2 in values

    @classmethod
    def is_flush(cls, cards: list[Card]):
        suits = [suit for suit, _ in map(cls.parse_card, cards)]
        return len(set(suits)) == 1

    @classmethod
    def is_straight(cls, cards: list[Card]):
        # 先去重 这是一个由纯数字组成的set
        # reverse=True 表示降序排列，大的在前
        ranks = sorted(set([rank for _, rank
                            in map(cls.parse_card, cards)]), reverse=True)

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

    @classmethod
    def is_three_of_a_kind(cls, cards: list[Card]):
        return cls.has_n_of_a_kind(cards, 3)

    @classmethod
    def is_two_pairs(cls, cards: list[Card]):
        # 不能用has_n_of_a_kind()来判断
        pairs = 0
        count = {}
        for _, rank in map(cls.parse_card, cards):
            # 获取每个数字的拥有的张数
            count[rank] = count.get(rank, 0) + 1
        for v in count.values():
            if v == 2:
                pairs += 1
        return pairs == 2

    @classmethod
    def is_one_pair(cls, cards: list[Card]):
        return cls.has_n_of_a_kind(cards, 2)

    @classmethod
    def has_n_of_a_kind(cls, cards, n) -> bool:
        count = {}
        for _, rank in map(cls.parse_card, cards):
            count[rank] = count.get(rank, 0) + 1
        return any(v >= n for v in count.values())
