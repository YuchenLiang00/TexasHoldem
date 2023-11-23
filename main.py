from src import Dealer
from src import Player


def main():
    """ 接近完整流程 """
    # 初始化
    bob = Player('Bob')
    alice = Player('Alice')
    dealer = Dealer([bob, alice])
    # 发牌1
    try:
        dealer.play()

        # 比大小
        # TODO evaluate hands

        dealer.eval_hands()
        input("Press Enter to continue...")
        #再来一次
        dealer.reset_deck()
    except KeyboardInterrupt:
        print("\n\nGame Over!\n")
        return


if __name__ == '__main__':
    main()
