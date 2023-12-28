from __future__ import annotations
from src import Dealer
from src import Player
from app import app, open_browser
import threading

def main():
    """ 接近完整流程 """
    # 初始化
    players = []
    while True:
        name = input("Please enter your name(end with enter):")
        if name:
            players.append(Player(name))
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
    # main()
    threading.Thread(target=open_browser).start()
    app.run(debug=True)
