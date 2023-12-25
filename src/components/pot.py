""" 彩池管理 """

from dataclasses import dataclass, field


@dataclass
class Pot:
    amount: int = 0
    eligible_players: set["Player"] = field(default_factory=set)  # type: ignore

    def add_player(self, player):
        self.eligible_players.add(player)

    def add_chips(self, chips: int):
        self.amount += chips

    def remove_player(self, player):
        self.eligible_players.remove(player) # or discard()
