# Unlimited Texas Hold'em
Final Project of the course of Programming and Applications  

## 使用步骤
根据依赖文件创建新环境 
```zsh
conda env create -f environment.yaml
```
切换环境
```zsh
source activate holdem
```
运行主函数
```zsh
python main.py
```

## 遇到的问题
1. 玩家下注行为的细分
   1. Raise, Call, All-in的判断
   2. 玩家出现raise, all-in to call时，当前的current_bet 和 min_raise的维护
2. 奖池的计算
3. 大盲小盲的前置
4. 当玩家出现all-in时，边池的计算
5. 牌桌位置的确定（button, sb, bb）
6. 赢家的确定
7. 同一牌力等级的细分比较
8. 胜率计算器的构造
9. 输光了的玩家需要从玩家名单中踢出
10. 盲注的维护


## Credits

This project uses code from [SirRender00/texasholdem](https://github.com/SirRender00/texasholdem)
under the MIT License. See [card.py](./src/components/card.py) for the source code.
