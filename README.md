
# ICO-DataHub

ICO-DataHub 是一个用于抓取和处理区块链相关数据的工具集，专注于从多个来源（如 Uniswap、Etherscan 和 Twitter）提取有价值的信息，并将其存储于 SQLite 数据库中以供分析。


## 文件结构
```
ICO-DataHub/
├──sourceCode
│   ├── ScraperScript/                    # 数据抓取模块
│   │   ├── uniswap_scraper.py            # 用于抓取 Uniswap 平台上的代币信息    
│   │   ├── contract_scrapert.py          # 用于从 Etherscan 抓取智能合约的详细信息
│   │   ├── token_scraper.py              # 用于监控区块链上的新区块并提取代币交易信息
│   │   ├── dextool_scraper.py            # 用于抓取 DexTools 平台上的代币交易和市场表现数据
│   │   ├── social_media_extractor.py     # 用于从智能合约源代码中提取社交媒体链接（如 Twitter、Telegram）
│   │   ├── twitter_scraper.py            # 用于抓取与代币相关的 Twitter 活动数据
│   │   └── README.md                     # 数据抓取模块详细文档     
│   │
│   ├── DatabaseManager/                  # 数据库模块
│   │   ├── DbManager.py                  # 数据库管理                   
│   │   └── README.md                     # 数据库结构文档     
│   │
│   └── runScraperScript.sh                # Run Script        
├──README.md                              # ICO-DataHub 文档
└──requirements.txt                       # python 环境配置
```
## 快速导航
- [数据抓取模块详细说明](sourceCode/ScraperScript/README.md)
- [数据库结构说明](sourceCode/DatabaseManager/README.md)

## 安装与配置

1. **环境需求**
   - Python 3.9 或以上
   - 必要的依赖项列于 `requirements.txt`

2. **安装依赖项**
   ```bash
   pip install -r requirements.txt