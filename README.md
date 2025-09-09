# X(Twitter) 用户吐槽抓取分析工具

一个强大的X(Twitter)数据抓取和分析工具，专门用于收集、分类和分析用户的吐槽和问题反馈。支持中英文内容处理，提供智能分类、难度评估和情感分析功能。

**🆕 新功能：集成Selenium反爬机制绕过功能！**

## ✨ 主要功能

### 🔍 数据抓取
- **双模式抓取**: 支持Twitter API和Selenium反爬模式
- **反检测技术**: 集成undetected-chromedriver和selenium-stealth
- **智能搜索**: 基于关键词搜索相关吐槽和问题
- **多语言支持**: 自动识别和处理中英文内容
- **实时抓取**: 获取最新的用户反馈数据
- **API限制管理**: 自动处理API速率限制

### 🛡️ 反爬机制绕过
- **隐藏自动化特征**: 自动隐藏webdriver属性
- **随机User-Agent**: 动态切换浏览器标识
- **人类行为模拟**: 随机滚动、点击、延迟
- **代理支持**: 支持HTTP/SOCKS代理
- **多重反检测**: 综合多种反检测技术

### 📊 智能分类
- **难度等级**: 1-5级自动难度评估
- **问题分类**: 技术问题、用户体验、功能需求等
- **时间分析**: 按日期、小时、星期统计
- **关键词提取**: 自动提取重要关键词

### 🎯 数据分析
- **情感分析**: 自动计算情感倾向分数
- **趋势分析**: 时间序列趋势图表
- **可视化报告**: 丰富的图表和词云
- **综合报告**: 详细的分析报告和建议

### 💾 本地存储
- **SQLite数据库**: 结构化存储所有数据
- **多格式导出**: CSV、JSON格式导出
- **分类存储**: 按日期、难度、分类自动整理

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆或下载项目文件
# 确保Python 3.7+已安装

# 安装依赖包（包含反爬功能）
pip install -r requirements_selenium.txt

# 或运行自动安装脚本
python setup.py
```

### 2. 配置Twitter API

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 创建应用并获取API凭证
3. 编辑 `config.json` 文件，填入您的API凭证：

```json
{
  "bearer_token": "您的Bearer Token",
  "consumer_key": "您的Consumer Key",
  "consumer_secret": "您的Consumer Secret",
  "access_token": "您的Access Token",
  "access_token_secret": "您的Access Token Secret"
}
```

### 3. 运行数据抓取

```bash
# Twitter API模式（需要API凭证）
python x_scraper.py

# Selenium反爬模式（无需API凭证，推荐）
python x_scraper.py --selenium --stealth

# 流程优化商机发现工具（默认启用反爬）
python process_optimization_scraper.py

# 反爬功能演示和测试
python selenium_stealth_demo.py

# 自定义搜索示例
python -c "
from x_scraper import XScraper
# 使用反爬模式
scraper = XScraper(use_selenium=True, use_stealth=True)
complaints = scraper.search_complaints('微信问题', max_results=100)
scraper.save_complaints(complaints)
"
```

### 4. 数据分析

```bash
# 运行完整分析
python data_analyzer.py
```

## 📁 项目结构

```
x-scraper/
├── x_scraper.py           # 主抓取脚本
├── data_analyzer.py       # 数据分析脚本
├── setup.py              # 自动安装脚本
├── config.json.template   # 配置文件模板
├── config.json           # 实际配置文件（需要创建）
├── requirements.txt      # Python依赖
├── README.md            # 说明文档
├── output/              # 导出数据目录
├── analysis_output/     # 分析结果目录
└── logs/               # 日志目录
```

## 🔧 配置选项

### 搜索配置
```json
{
  "search_queries": [
    "微信", "支付宝", "淘宝", "iPhone", "Android"
  ],
  "max_results_per_query": 100
}
```

### 分类关键词
```json
{
  "difficulty_keywords": {
    "high": {
      "zh": ["系统", "数据库", "服务器"],
      "en": ["system", "database", "server"]
    }
  }
}
```

## 📈 输出文件说明

### 数据文件
- `all_complaints.csv` - 所有数据的CSV格式
- `all_complaints.json` - 所有数据的JSON格式
- `complaints_YYYY-MM-DD.csv` - 按日期分组的数据
- `complaints_level_N.csv` - 按难度等级分组
- `complaints_分类名.csv` - 按问题分类分组

### 分析报告
- `comprehensive_report.md` - 综合分析报告
- `statistics.json` - 统计数据JSON
- `*.png` - 各种分析图表

### 可视化图表
- `time_analysis.png` - 时间分析图表
- `difficulty_analysis.png` - 难度分析图表
- `category_analysis.png` - 分类分析图表
- `sentiment_analysis.png` - 情感分析图表
- `wordcloud_chinese.png` - 中文词云
- `wordcloud_english.png` - 英文词云

## 🎨 使用示例

### 基础使用
```python
from x_scraper import XScraper

# 初始化抓取器
scraper = XScraper('config.json')

# 搜索特定关键词
complaints = scraper.search_complaints('iPhone问题', max_results=50)

# 保存数据
scraper.save_complaints(complaints)

# 导出文件
scraper.export_to_files('my_output')
```

### 数据分析
```python
from data_analyzer import DataAnalyzer

# 初始化分析器
analyzer = DataAnalyzer('x_complaints.db')

# 运行完整分析
report = analyzer.run_complete_analysis()
print(report)
```

### 自定义搜索
```python
# 搜索多个关键词
keywords = ['微信支付', '支付宝', '银行卡']
all_data = []

for keyword in keywords:
    data = scraper.search_complaints(f"{keyword} 问题", max_results=30)
    all_data.extend(data)

scraper.save_complaints(all_data)
```

## 📊 数据字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| tweet_id | TEXT | 推文唯一ID |
| user_id | TEXT | 用户ID |
| content | TEXT | 推文内容 |
| language | TEXT | 语言类型(zh/en) |
| created_at | TIMESTAMP | 发布时间 |
| difficulty_level | INTEGER | 难度等级(1-5) |
| category | TEXT | 问题分类 |
| keywords | TEXT | 关键词列表 |
| sentiment_score | REAL | 情感分数(-1到1) |
| like_count | INTEGER | 点赞数 |
| retweet_count | INTEGER | 转发数 |
| reply_count | INTEGER | 回复数 |

## 🔍 难度等级说明

| 等级 | 说明 | 示例关键词 |
|------|------|------------|
| 1 | 简单问题 | 界面、颜色、字体 |
| 2 | 较简单问题 | 设置、显示 |
| 3 | 中等问题 | 功能、配置、同步 |
| 4 | 较困难问题 | 系统、网络、性能 |
| 5 | 困难问题 | 数据库、架构、安全 |

## 🏷️ 问题分类

- **技术问题**: bug、错误、崩溃、故障
- **用户体验**: 界面、交互、设计问题
- **功能需求**: 功能缺失、改进建议
- **服务质量**: 客服、服务态度
- **价格费用**: 价格、收费相关
- **其他**: 未分类的其他问题

## ⚠️ 注意事项

### API使用限制
- Twitter API有速率限制，请合理设置抓取频率
- 建议在搜索间隔添加适当延迟
- 监控API使用量，避免超出限制

### 反爬机制使用建议
- **推荐使用Selenium模式**：无需API凭证，更稳定
- **合理设置延迟**：避免过于频繁的请求
- **使用代理IP**：提高匿名性和成功率
- **定期更换配置**：避免被识别为固定模式

### 数据合规
- 遵守Twitter服务条款
- 尊重用户隐私，不要存储敏感信息
- 仅用于合法的数据分析目的
- 合理使用反爬技术，避免对服务器造成压力

### 性能优化
- 大量数据抓取时建议分批处理
- 定期清理过期数据
- 使用数据库索引提高查询性能
- Selenium模式下适当增加延迟时间

## 🛠️ 故障排除

### 常见问题

**Q: API认证失败**
A: 检查config.json中的API凭证是否正确，确保没有多余的空格或字符

**Q: 抓取数据为空**
A: 检查搜索关键词是否合适，尝试更通用的关键词

**Q: 中文分词效果不佳**
A: 安装更好的中文字体和词典文件

**Q: 图表显示乱码**
A: 安装中文字体，设置matplotlib中文支持

**Q: Selenium反爬模式启动失败**
A: 确保已安装Chrome浏览器，检查依赖包是否完整安装

**Q: 被网站检测为机器人**
A: 尝试使用代理IP，增加延迟时间，或更换User-Agent

**Q: ChromeDriver版本不匹配**
A: 使用undetected-chromedriver会自动处理版本匹配

### 日志查看
```bash
# 查看运行日志
tail -f x_scraper.log

# 查看错误信息
grep "ERROR" x_scraper.log
```

## 🔮 未来功能

- [ ] 支持更多社交平台（微博、小红书等）
- [ ] 实时监控和预警功能
- [ ] 机器学习自动分类优化
- [ ] Web界面和仪表板
- [ ] 多用户和权限管理
- [ ] 数据导出到更多格式
- [ ] 情感分析模型优化
- [x] **Selenium反爬机制绕过** ✅
- [ ] 分布式代理池管理
- [ ] 验证码自动识别
- [ ] 更多反检测技术集成

## 📄 许可证

本项目仅供学习和研究使用。使用时请遵守相关平台的服务条款和数据使用政策。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

---

**注意**: 使用本工具前请确保您有合法的Twitter API访问权限，并遵守相关的服务条款和数据使用政策。