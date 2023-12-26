from __future__ import annotations
from src import Dealer
from src import Player


def main():
    """ 接近完整流程 """
    # 初始化
    alice = Player('Alice',100)
    bob = Player('Bob')
    cindy = Player('Cindy')
    dealer = Dealer([alice, bob, cindy])
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
