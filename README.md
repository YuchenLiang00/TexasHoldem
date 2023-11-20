# TexasHoldem
Final Project of Programming Design
my_poker_game/  
│  
├── src/                  # 源代码  
│   ├── __init__.py  
│   ├── game.py           # 游戏逻辑  
│   ├── hand_evaluation/  # 用于评估手牌的模块  
│   │   ├── __init__.py  
│   │   ├── evaluator.py  
│   │   └── helpers.py  
│   ├── network/          # 网络通信模块  
│   │   ├── __init__.py  
│   │   ├── server.py  
│   │   └── client.py  
│   └── ui/               # 用户界面模块  
│       ├── __init__.py  
│       ├── main_window.py  
│       └── widgets.py    
│  
├── tests/                # 测试代码  
│   ├── __init__.py  
│   └── test_game.py  
│  
├── bin/                  # 可执行脚本  
│   └── run_game.py  
│  
├── docs/                 # 文档  
│   └── ...  
│  
├── setup.py              # 安装脚本  
└── README.md             # 项目说明文件  
