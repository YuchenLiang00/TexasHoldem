from src.dealer import Dealer
from src.player import Player


def main():
    """ 接近完整流程 """
    player1 = Player('Bob')
    player2 = Player('Alice')
    dealer = Dealer([player1, player2])
    dealer.deal_preflop()
    dealer.deal_flop()
    dealer.deal_turn()
    dealer.deal_river()
    dealer.show_comminity_cards()
    # TODO evaluate hands
    player1.show_hands()
    player2.show_hands()


if __name__ == '__main__':
    main()
