# X(Twitter)吐槽抓取和分析系统

一个用于从X(Twitter)抓取用户吐槽和问题反馈的智能系统，支持中英文双语分析，可按日期和难易程度自动分类存储。

## 🌟 功能特点

- **双模式数据抓取**：支持Twitter API和Selenium网页爬虫两种方式
- **中英文智能分析**：自动识别语言并进行相应的情感分析和文本处理
- **多维度分类**：
  - 按日期分类存储
  - 按问题难度分级（简单/中等/困难）
  - 按问题类型分类（技术问题/可用性/功能请求等）
- **情感分析**：识别正面、负面和中性情绪
- **自动报告生成**：生成JSON和Excel格式的分析报告
- **关键词提取**：自动提取热门吐槽关键词

## 📋 系统要求

- Python 3.8+
- Chrome浏览器（如果使用Selenium模式）
- Twitter API认证（如果使用API模式）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd twitter-complaints-analyzer
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量示例文件并填写您的配置：

```bash
cp .env.example .env
```

编辑`.env`文件，填写Twitter API凭证（如果使用API模式）：

```
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### 4. 运行系统

基本使用：
```bash
python main.py
```

指定搜索关键词：
```bash
python main.py -k "ChatGPT" "OpenAI" "Claude"
```

更多选项：
```bash
python main.py -k "产品名称" -n 200 -d 14
```

参数说明：
- `-k, --keywords`：搜索关键词（可指定多个）
- `-n, --max-tweets`：每个关键词最大抓取数量（默认100）
- `-d, --days`：搜索过去N天的数据（默认7）
- `--no-api`：不使用API，使用网页爬虫模式

## 📂 项目结构

```
twitter-complaints-analyzer/
├── src/
│   ├── twitter_scraper.py    # Twitter数据抓取模块
│   ├── text_analyzer.py      # 文本分析模块
│   └── data_manager.py       # 数据管理模块
├── data/                     # 数据存储目录
│   ├── raw/                  # 原始推文数据
│   ├── processed/            # 处理后的数据
│   ├── by_date/             # 按日期分类的数据
│   ├── by_difficulty/       # 按难度分类的数据
│   ├── by_category/         # 按类型分类的数据
│   └── reports/             # 分析报告
├── config.py                # 配置文件
├── main.py                  # 主程序
├── requirements.txt         # 依赖列表
└── .env.example            # 环境变量示例
```

## 🔍 数据分析维度

### 1. 情感分析
- **正面（Positive）**：满意、赞赏的反馈
- **负面（Negative）**：吐槽、抱怨的内容
- **中性（Neutral）**：客观陈述或建议

### 2. 难度分级
- **🟢 简单（Easy）**：小问题、容易修复
- **🟡 中等（Medium）**：一般问题、需要一定工作量
- **🔴 困难（Hard）**：严重问题、需要大量工作

### 3. 问题分类
- **技术问题（Technical）**：bug、崩溃、性能问题
- **可用性（Usability）**：界面、操作相关问题
- **功能请求（Feature Request）**：新功能需求
- **性能问题（Performance）**：速度、资源占用
- **兼容性（Compatibility）**：版本、平台兼容问题
- **服务问题（Service）**：客服、支持相关

## 📊 输出格式

### JSON报告示例
```json
{
  "timestamp": "20240115_143022",
  "total_tweets": 150,
  "date_range": {
    "start": "2024-01-08",
    "end": "2024-01-15"
  },
  "sentiment_distribution": {
    "negative": 89,
    "neutral": 45,
    "positive": 16
  },
  "difficulty_distribution": {
    "easy": 30,
    "medium": 65,
    "hard": 55
  }
}
```

### Excel报告
系统会生成包含以下工作表的Excel文件：
- **All Tweets**：所有推文的详细信息
- **Easy/Medium/Hard Issues**：按难度分类的推文
- **Summary**：汇总统计信息

## 🛠 高级用法

### 使用Python API

```python
from src.twitter_scraper import TwitterScraper
from src.text_analyzer import TextAnalyzer
from src.data_manager import DataManager

# 初始化组件
scraper = TwitterScraper(use_api=True)
analyzer = TextAnalyzer()
manager = DataManager()

# 抓取推文
tweets = scraper.search_complaints(["产品名称"], max_results=100)

# 分析推文
analyzed = [analyzer.analyze_tweet(tweet) for tweet in tweets]

# 保存结果
manager.save_analyzed_data(analyzed)
```

### 自定义分析规则

编辑`src/text_analyzer.py`中的关键词字典来自定义：
- 问题类别关键词
- 难度评估指标
- 情感分析词汇

## ⚠️ 注意事项

1. **API限制**：Twitter API有速率限制，请合理使用
2. **隐私保护**：请遵守相关法律法规，保护用户隐私
3. **数据准确性**：自动分析可能存在误差，建议人工复核重要结论
4. **代理设置**：如需使用代理，请在`.env`文件中配置

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题或建议，请提交Issue。