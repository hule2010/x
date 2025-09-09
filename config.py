"""
配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Twitter API配置
TWITTER_CONFIG = {
    'bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
    'api_key': os.getenv('TWITTER_API_KEY'),
    'api_secret': os.getenv('TWITTER_API_SECRET'),
    'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
    'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
}

# 代理配置
PROXY_CONFIG = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY'),
}

# 数据存储配置
DATA_CONFIG = {
    'path': os.getenv('DATA_PATH', './data'),
    'max_tweets_per_search': 100,
    'days_back': 7,
}

# 搜索配置
SEARCH_CONFIG = {
    # 默认搜索关键词
    'default_keywords': [
        'ChatGPT', 'OpenAI', 'Claude', 'Anthropic',
        'Google Bard', 'Microsoft Copilot', 'AI assistant'
    ],
    
    # 吐槽相关的关键词
    'complaint_keywords': {
        'en': [
            'problem', 'issue', 'bug', 'error', 'crash', 'slow',
            'broken', 'doesn\'t work', 'not working', 'failed',
            'sucks', 'terrible', 'awful', 'hate', 'frustrated'
        ],
        'zh': [
            '问题', '出错', '崩溃', '很慢', '坏了', '不能用',
            '失败', '糟糕', '讨厌', '烦人', '垃圾', '吐槽'
        ]
    }
}

# 分析配置
ANALYSIS_CONFIG = {
    'min_confidence_threshold': 0.5,
    'batch_size': 50,
    'enable_gpu': False,  # 是否使用GPU加速
}

# 报告配置
REPORT_CONFIG = {
    'formats': ['json', 'excel'],  # 支持的报告格式
    'top_complaints_count': 20,  # 显示前N个热门吐槽
    'include_charts': True,  # 是否包含图表
}