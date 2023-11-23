class Move:
    """ 玩家的行动 """

    def __init__(self, action=None, amount: int = 0) -> None:
        self._action = action
        self._amount: int = amount

    def __str__(self):
        if self._amount and self.action:
            return self._action.to_string() + ' ' + str(self._amount)
        else:
            return ""

    @property
    def action(self):
        return self._action

    @property
    def amount(self):
        return self._amount
