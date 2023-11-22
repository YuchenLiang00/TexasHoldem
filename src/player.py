""" 定义玩家的信息和行为 """


from asyncio import protocols
import gc
from telnetlib import STATUS
from typing import Literal
# from src.hand import Hand


class Move:
    """ 玩家的行动 """
    ACTION: type = Literal['Fold', 'Call', 'Raise', 'Check', 'ALL-IN']

    def __init__(self, action: ACTION = '', amount: int = 0) -> None:
        self.action = action
        self.amount = amount

    def __str__(self):
        if self.amount is not None:
            return self.action + ' ' + str(self.amount)
        else:
            return self.action


class Player:
    """ 玩家 """
    INIT_MONEY = 1_000

    def __init__(self, name: str) -> None:
        self._name = name
        self._money = Player.INIT_MONEY
        self._bet_history = {'Pre-Flop': [],
                             'Flop': [], 'Turn': [], 'River': []}
        self._action: Move.ACTION = None

    def bet(self,
            street: str,
            amount: int,
            current_bet: int,
            min_raise: int) -> Move:
        """ 
        下注行为 
        @args:
            street: 街名,可取('Pre-Flop', 'Flop', 'Turn', 'River',)
            amount: 下注量
            current_bet: 上一个人的下注量, 也是call需要的下注量
            min_raise: 加注增量，标记着这个玩家需要完成一次加注行为的最小增量

        @return:
            status: str

        这里要完善根据输入的amout标记call、raise、fold、check的行为:
        if amount > money, 或 current_bet > money且amount > 0, 视为allin
        if amount 
        if amount <= 0, 视为fold
        if current_bet = 0 且 amount = 0, 视为check
        else 视为跟注。逻辑上来说，乱输入也算跟注
        """
        if amount == 0 and current_bet == 0:
            # check
            self._action = 'Check'

        elif amount <= 0:
            # fold
            # 标记玩家弃牌
            amount = None
            self._action = 'Fold'

        # 以下amount>0
        elif amount >= current_bet + min_raise:
            # TODO raise
            # 加注, 要判断是否符合加注规则
            current_bet = amount
            min_raise = amount - current_bet
            self._action = 'Raise'

        elif amount >= self._money or (current_bet > self._money and amount > 0):
            # all in
            amount = self._money
            self._action = 'ALL-IN'

        else:
            # call
            amount = current_bet
            self._action = 'Call'

        # 更新玩家状态
        self._money -= amount
        self._current_bet = amount
        move = Move(self._action, self._current_bet)
        self._bet_history[street].append(move)
        return move

    @property
    def action(self):
        return self._action

    @property
    def bet_history(self):
        return self._bet_history.copy()
    
    @property
    def current_bet(self):
        return self._current_bet
    
    def clear_current_bet(self):
        self._current_bet = 0

    def set_hand(self, hand):
        """ 接受荷官的发牌 """
        # dealer发牌的功能
        self._hand = hand
        self._bet_history = {'Pre-Flop': [],
                             'Flop': [], 'Turn': [], 'River': []}
        self.is_folded = False
        gc.collect()

    def show_hands(self):
        """ 展示手牌 """
        print(self._name, self._hand, sep='\t', end=":\t")

    def show_move(self,) -> str:
        """ 展示行动 """
        move_list: list[str] = [str(l[-1]) if l else str(Move())
                                for l in self._bet_history.values()]
        return '\t'.join(move_list)


if __name__ == '__main__':
    m = Move('Fold', None)
    print(m)
