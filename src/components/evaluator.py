""" 
This file is inspired by the word of SirRender00 from GitHub
https://github.com/SirRender00/texasholdem/blob/main/texasholdem/evaluator/evaluator.py

MIT License

Copyright (c) 2021 SirRender00

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import itertools

from src.components import Card, LOOKUP_TABLE


class Evaluator:
    """ 
    牌力判断
    Evaluates hand strengths with optimizations in terms of speed and memory usage.
    """
    @staticmethod
    def evaluate(cards: list[Card], board: list[Card])-> tuple[int, str, list[Card]]:
        """ Combine functions
        Args:
            cards (list[int]): A list of length two of card ints that a player holds.
            board (list[int]): A list of length 3, 4, or 5 of card ints.
        Returns:
            str: A human-readable string of the hand rank (i.e. Flush, Ace High).
            list: The best cards combination.
        """

        hand_rank, combo = Evaluator.calculate(cards=cards, board=board)
        rank_string = Evaluator.rank_to_string(hand_rank)
        return hand_rank, rank_string, combo

    @staticmethod
    def _five(cards: list[Card]) -> int:
        """
        Performs an evaluation given card in integer form, mapping them to
        a rank in the range [1, 7462], with lower ranks being more powerful.

        Variant of Cactus Kev's 5 card evaluator.

        Args:
            cards (list[Card]): A list of 5 card ints.
        Returns:
            int: The rank of the hand.(rank class)

        """
        # if flush
        if cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000:
            hand_or = (cards[0] | cards[1] | cards[2] | cards[3] | cards[4]) >> 16
            prime = Card.prime_product_from_rankbits(hand_or)
            return LOOKUP_TABLE.flush_lookup[prime]

        # otherwise
        prime = Card.prime_product_from_hand(cards)
        return LOOKUP_TABLE.unsuited_lookup[prime]

    @staticmethod
    def calculate(cards: list[Card], board: list[Card]) -> tuple[int, list[Card]]:
        """
        Evaluates the best five-card hand from the given cards and board. Returns
        the corresponding rank.

        Args:
            cards (list[int]): A list of length two of card ints that a player holds.
            board (list[int]): A list of length 3, 4, or 5 of card ints.
        Returns:
            int: A number between 1 (highest) and 7462 (lowest) representing the relative
                hand rank of the given card.
            list: The best cards combination.

        """
        all_cards = cards + board
        # 生成(评分, hand)元组的列表
        hands_with_scores = [(Evaluator._five(hand), hand) for hand in itertools.combinations(all_cards, 5)] # type: ignore
        # 找到评分最低的元组
        hand_rank, best_hand = min(hands_with_scores)
        return hand_rank, best_hand # type: ignore

    @staticmethod
    def get_rank_class(hand_rank: int) -> int:
        """
        Returns the class of hand given the hand hand_rank returned from evaluate from
        9 rank classes.

        Example:
            straight flush is class 1, high card is class 9, full house is class 3.

        Returns:
            int: A rank class int describing the general category of hand from 9 rank classes.
                Example, straight flush is class 1, high card is class 9, full house is class 3.

        """
        max_rank = min(
            rank for rank in LOOKUP_TABLE.MAX_TO_RANK_CLASS if hand_rank <= rank)
        return LOOKUP_TABLE.MAX_TO_RANK_CLASS[max_rank]

    @staticmethod
    def rank_to_string(hand_rank: int) -> str:
        """
        Returns a string describing the hand of the hand_rank.

        Example:
            166 -> "Four of a Kind"

        Args:
            hand_rank (int): The rank of the hand given by :meth:`evaluate`
        Returns:
            string: A human-readable string of the hand rank (i.e. Flush, Ace High).

        """
        return LOOKUP_TABLE.RANK_CLASS_TO_STRING[Evaluator.get_rank_class(hand_rank)]

    @staticmethod
    def get_five_card_rank_percentage(hand_rank: int) -> float:
        """
        The percentage of how many of the 7462 hand strengths are worse than the given one.

        Args:
            hand_rank (int): The rank of the hand given by :meth:`evaluate`
        Returns:
            float: The percentile strength of the given hand_rank (i.e. what percent of hands is worse
                than the given one).

        """
        return 1 - float(hand_rank) / float(LOOKUP_TABLE.MAX_HIGH_CARD)
