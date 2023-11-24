""" 定义玩家的信息和行为 """


import gc
from copy import deepcopy
from typing import Optional

from src.components import Hand, Street, Action, Move


class Player:
    """ 玩家 """
    INIT_MONEY = 1_000

    def __init__(self, name: str) -> None:
        self._name = name
        self._money = Player.INIT_MONEY
        self._bet_history = {Street.PRE_FLOP: [], Street.FLOP: [],
                             Street.TURN: [], Street.RIVER: []}
        self._action: Action = None
        self._current_bet: int = 0
        self._hand: Hand = None

    def bet(self,
            street: str,
            amount: Optional[int],
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

        我们发现 all-in是call、raise的一个子项。
        如果check或者fold的话是不会触发all-in的
        因此 我们可以不把all-in放在和call、rasie平级的判断中
        而是先判断是否call、raise 再检查是否触发all-in
        all-in 的返回优先级高于call和raise

        例子：
            A bet 100, B raise to 500, C all in 600, 
            则D的最小加注额（跟注额）是多少？
        对于加注raise有两种常见规则：
            - 全额下注规则：如果适用这一规则，C的全押600不构成一个完整的加注，因此不会重新开放下注。在这种情况下，D的最小加注额应该是B的加注额500加上之前的加注增量400（即总额900）​​。
            - 半额下注规则：如果适用这一规则，并且全押额超过了最低下注的一半，那么它就被视为加注并重新开放下注。但具体是否适用这一规则取决于游戏的具体规则设定。
        对于跟注call，玩家D：
            - 他需要匹配当前轮次的最大下注金额，即C的全押金额600。
            - 尽管C的全押没有构成一个有效的加注（因为它没有比前一个玩家的加注额多出最小加注量），但它仍然是当前轮次的最大下注金额。
            - 因此，D需要下注600才能跟注。这是因为在无限注德州扑克中，跟注意味着匹配当前底池中的最大下注额，而不管这个下注额是通过正常加注还是全押形成的。
        """
        if amount is None or 0 < amount < current_bet + min_raise:
            # call
            # 不构成加注的所有正数视为跟注，乱输入也算跟注
            amount = current_bet  # 先纠正乱输入的部份
            # 本轮需要额外下的注
            additional_bet = amount - self._current_bet

            if additional_bet >= self._money:
                #  需要再下注的部份超过所剩金额，并且也要call的话
                #  视为 all-in to call
                self._action = Action.ALL_IN
                self._current_bet += self._money  # 之前可能已经下过注
                self._money = 0
            else:
                # 不超过所剩金额
                self._action = Action.CALL
                self._money -= additional_bet
                self._current_bet = amount
                # self._current_bet永远是这一个street的下注总量（total)
        elif amount >= current_bet + min_raise:
            # raise sanity check
            # 加注, 要判断是否符合加注规则, 要查相关资料确定加注规则
            # 由于加注时，之前可能已经下注，所以要调整本轮下注金额
            # 本轮需要额外下的注
            additional_bet = amount - self._current_bet
            if additional_bet >= self._money:
                # all-in to raise
                self._action = Action.ALL_IN
                self._current_bet += self._money
                self._money = 0
            else:
                self._current_bet = amount
                self._money -= additional_bet  # 加注成立的话，当然满足
                self._action = Action.RAISE
        elif amount == 0 and current_bet == 0:
            # check
            self._action = Action.CHECK
            self._current_bet = 0
        else:
            # fold
            # 标记玩家弃牌
            self._current_bet = None
            self._action = Action.FOLD
            # TODO 直接把玩家的接下来几条街的行动全都标记为Fold，在dealer中直接跳过
        
        move = Move(self._action, self._current_bet)
        if self._aciton in (Action.FOLD, Action.ALL_IN):
            for st in Street:
                if st >= street:
                    self._bet_history[st].append(move)
        else:
            # 更新玩家状态
            self._bet_history[street].append(move)
        return move
    
    def set_hand(self, hand):
        """ 接受荷官的发牌 重置一些参数"""
        self._hand = hand
        self._bet_history = {Street.PRE_FLOP: [], Street.FLOP: [],
                             Street.TURN: [], Street.RIVER: []}
        self._aciton = None
        self._current_bet = 0
        gc.collect()

    def show_hand(self,) -> str:
        """ 展示手牌 """
        print(f"{self._name:<10} {self._hand}", end="\t")
        return self._name, self._hand

    def show_move(self,) -> list[str]:
        """ 展示行动 """
        move_list: list[str] = [str(l[-1]) if l else " " * 15
                                for l in self._bet_history.values()]
        return move_list
    
    def reset_current_bet(self):
        self._current_bet = 0

    def reset_action(self):
        self._aciton = None

    @property
    def name(self):
        return self._name

    @property
    def action(self):
        return self._action

    @property
    def bet_history(self):
        return deepcopy(self._bet_history)  # 深拷贝

    @property
    def current_bet(self):
        return self._current_bet

    @property
    def hand(self):
        return deepcopy(self._hand)

    @property
    def money(self):
        return self._money

if __name__ == '__main__':
    print(Action.FOLD.value)
