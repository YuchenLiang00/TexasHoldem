class Move:
    """ 玩家的行动 """

    def __init__(self, action=None, amount: int = 0) -> None:
        self._action = action
        self._amount: int = amount

    def __str__(self):
        if self._action:
            action_str = self._action.to_string()
            if self._amount > 0:
                return f"{action_str:<6} {self._amount:>5}"
            else:
                return f"{action_str:<12}"
        else:
            return " " * 12


    @property
    def action(self):
        return self._action

    @property
    def amount(self):
        return self._amount
