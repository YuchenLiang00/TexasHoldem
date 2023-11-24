""" 游戏环境 """


from gamer.dealer import Dealer
from gamer.player import Player


class GameEnv:
    """ 创建游戏的环境 """

    def __init__(self) -> None:
        pass

    def init_player(self) -> Dealer:
        """ 初始化玩家信息 创建并返回荷官 """
        player_list = []
        while True:
            name = input("Please input the name of player")
            if name:
                player_list.append(Player(name))
            else:
                break
        dealer = Dealer(player_list)
        return dealer
