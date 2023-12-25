

from src.components import Move, Action, Pot
import typing
if typing.TYPE_CHECKING:
    from src.gamer import Player


class PotManager:
    """ 彩池管理员 """
    # 可以尝试新建一个专门处理一轮上all-in数额的数据结构，在一条街结束时再处理底池
    def __init__(self):
        # 至少有一个主池
        self.pots:list[Pot] = [Pot()]
        return
        
    def update_pots(self, player_list):
        # 此方法在一条街结束后调用，处理底池的创建和更新
        player_moves = [[player, player.action, player.current_bet]  # type: ignore
                        for player in player_list 
                        if player.action != Action.FOLD]
        player_moves.sort(key=lambda x: x[2]) # 升序排列
        # 我们知道，所有人下注量一定是相等的，除非有人all-in
        # 只有all-in才可以下比别人都小的量
        player_num = len(player_list)
        # 处理剩余玩家的正常投注
        if not any(action == Action.ALL_IN for _, action, _, in player_moves):
            normal_bet_amount = player_moves[0][2]
            self.pots.append(Pot(normal_bet_amount * player_num, set(player_list))) # 增加一个底池
            return

        for i, player_move in enumerate(player_moves):
            # 遍历所有的操作
            if player_move[1] != Action.ALL_IN:
                # 现在下注的玩家的下注量不是all-in
                # 则后续的一定不是all-in
                # 要将后续的筹码都加入到新底池当中。
                pot = Pot()
                for p_move in player_moves[i:]:
                    pot.add_player(p_move[0])
                    pot.add_chips(p_move[2])
                self.pots.append(pot)
                # print(player_moves)
                break
            else:
                # 现在的玩家下注行动是all-in
                # 从后面的玩家的下注量中拿出现在玩家的下注量，
                # 形成新的底池，并将这个底池对象添加到PotManager的属性pots当中
                all_in_amount = player_move[2]
                # 计算超过all-in金额的总注
                for j in range(i,player_num):
                    player_moves[j][2] -= all_in_amount
                side_pot_amount = all_in_amount * (player_num - i)  # 主底池金额 = all-in金额 x 参与人数
                pot = Pot(side_pot_amount, set(p[0] for p in player_moves[i:]))
                # 更新主底池金额
                self.pots.append(pot)
        return
    
    def get_total_chips(self) -> int:
        chips = sum(pot.amount for pot in self.pots)
        return chips

    def distribute_winnings(self, player_rankings):
        # 根据玩家牌力分配彩池
        pass

    def reset_pot(self):
        # 重置彩池
        self.pots = [Pot()]
