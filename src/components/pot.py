""" 彩池管理 """

from src.components import Action, Move


class Pot:
    """ 彩池 """

    def __init__(self):
        # 至少有一个主池
        self.pots = list({"amount": 0, "eligible_players": set()})

    def add_bet(self, player, move: Move):
        # 增加彩池金额
        # 根据玩家下注情况决定增加哪个彩池的金额
        # 如果有玩家all-in，可能需要创建或更新边池
        # 确定应该将下注加入哪个彩池
        if move.action == Action.ALL_IN:
            # 玩家全押，可能需要创建新的边池
            all_in_amount = move.amount
            self.create_side_pot(player, all_in_amount)
        else:
            # 标准情况，加入当前活动的彩池（主彩池或最新的边池）
            self.pots[-1]["amount"] += move.amount
            self.pots[-1]["eligible_players"].add(player)

    def create_side_pot(self, all_in_player, all_in_amount: int):
        # TODO 计算新边池的金额
        new_pot_amount = 0
        for pot in self.pots:
            pot_contribution = min(pot["amount"], all_in_amount)
            new_pot_amount += pot_contribution
            pot["amount"] -= pot_contribution

        # 创建新边池
        new_pot = {"amount": new_pot_amount, "eligible_players": set(
            self.pots[-1]["eligible_players"])}
        new_pot["eligible_players"].remove(all_in_player)
        self.pots.append(new_pot)

    def distribute_winnings(self, player_rankings):
        # 根据玩家牌力分配彩池
        pass

    def reset_pot(self):
        # 重置彩池
        self.pots.clear()
