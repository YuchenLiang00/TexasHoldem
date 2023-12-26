from enum import Enum


class Action(Enum):
    """ Enum: 玩家动作类型 """

    FOLD = 'Fold'
    CALL = 'Call'
    RAISE = 'Raise'
    CHECK = 'Check'
    ALL_IN = 'ALL-IN'

    def to_string(self):
        return self.value

    @staticmethod
    def from_string(action_str):
        return Action[action_str.upper().replace("-", "_")]
