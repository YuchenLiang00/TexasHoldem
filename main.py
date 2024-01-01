from __future__ import annotations
from src import Dealer
from src import Player


def main():
    """ 接近完整流程 """
    # 初始化
    players = []
    for _ in range(9):
        name = input("Please enter your name(end with enter):")
        if name:
            players.append(Player(name))
        elif len(players) < 2:
            print('\nNo enough players!\n')
            return 
        else:
            print("\033[H\033[J", end="")
            print("Welcome to THU Casino, Texas Hold'em!")
            break
    dealer = Dealer(players)
    # 发牌1
    try:
        dealer.play()
        #再来一次
        dealer.reset_deck()
    except KeyboardInterrupt:
        print("\n\nGame Over!\n")
        return


if __name__ == '__main__':
    main()
