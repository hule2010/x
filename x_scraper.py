#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X(Twitter) 用户吐槽和问题抓取分析工具
支持中英文内容抓取、智能分类和本地存储
"""

import tweepy
import pandas as pd
import json
import re
import os
from datetime import datetime, timedelta
import sqlite3
from textblob import TextBlob
import jieba
import jieba.analyse
from collections import Counter
import logging
from typing import List, Dict, Optional
import time
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('x_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class XScraper:
    def __init__(self, config_file: str = 'config.json'):
        """初始化X抓取器"""
        self.config = self.load_config(config_file)
        self.api = self.setup_twitter_api()
        self.db_path = self.config.get('database_path', 'x_complaints.db')
        self.setup_database()
        
        # 设置jieba分词
        jieba.set_dictionary('dict.txt.big')  # 使用繁体字典以支持更多中文词汇
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件 {config_file} 未找到，请先创建配置文件")
            return {}
    
    def setup_twitter_api(self) -> Optional[tweepy.API]:
        """设置Twitter API"""
        try:
            # Twitter API v2 客户端
            client = tweepy.Client(
                bearer_token=self.config.get('bearer_token'),
                consumer_key=self.config.get('consumer_key'),
                consumer_secret=self.config.get('consumer_secret'),
                access_token=self.config.get('access_token'),
                access_token_secret=self.config.get('access_token_secret'),
                wait_on_rate_limit=True
            )
            
            # 验证凭证
            try:
                me = client.get_me()
                logger.info(f"API认证成功，用户: {me.data.username}")
                return client
            except Exception as e:
                logger.error(f"API认证失败: {e}")
                return None
                
        except Exception as e:
            logger.error(f"设置Twitter API失败: {e}")
            return None
    
    def setup_database(self):
        """设置SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建主表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id TEXT UNIQUE,
                user_id TEXT,
                username TEXT,
                content TEXT,
                language TEXT,
                created_at TIMESTAMP,
                difficulty_level INTEGER,
                category TEXT,
                keywords TEXT,
                sentiment_score REAL,
                retweet_count INTEGER,
                like_count INTEGER,
                reply_count INTEGER,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建分类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                keywords TEXT
            )
        ''')
        
        # 插入默认分类
        default_categories = [
            ('技术问题', '技术相关的问题和吐槽', 'bug,错误,崩溃,卡顿,慢,不能用,故障,问题'),
            ('用户体验', '界面和交互体验问题', 'UI,界面,体验,难用,复杂,不方便,设计'),
            ('功能需求', '功能缺失或改进建议', '功能,需要,希望,建议,改进,增加,缺少'),
            ('服务质量', '客服和服务相关问题', '客服,服务,态度,回复,处理,解决'),
            ('价格费用', '价格和费用相关抱怨', '贵,便宜,价格,费用,收费,免费,优惠'),
            ('其他', '其他类型的吐槽', '其他,杂项,一般')
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO categories (name, description, keywords) VALUES (?, ?, ?)',
            default_categories
        )
        
        conn.commit()
        conn.close()
        logger.info("数据库设置完成")
    
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        # 简单的语言检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            return 'zh'
        elif english_chars > 0:
            return 'en'
        else:
            return 'unknown'
    
    def extract_keywords(self, text: str, language: str) -> List[str]:
        """提取关键词"""
        if language == 'zh':
            # 中文关键词提取
            keywords = jieba.analyse.extract_tags(text, topK=10, withWeight=False)
        else:
            # 英文关键词提取
            blob = TextBlob(text.lower())
            words = [word for word in blob.words if len(word) > 2]
            word_freq = Counter(words)
            keywords = [word for word, freq in word_freq.most_common(10)]
        
        return keywords
    
    def calculate_difficulty_level(self, text: str, language: str) -> int:
        """计算问题难易程度 (1-5级)"""
        difficulty_score = 1
        
        # 基于关键词判断难度
        high_difficulty_keywords = {
            'zh': ['系统', '数据库', '服务器', '网络', '算法', '架构', '集成', '兼容性', '安全', '性能'],
            'en': ['system', 'database', 'server', 'network', 'algorithm', 'architecture', 'integration', 'compatibility', 'security', 'performance']
        }
        
        medium_difficulty_keywords = {
            'zh': ['功能', '设置', '配置', '导入', '导出', '同步', '备份'],
            'en': ['feature', 'setting', 'configuration', 'import', 'export', 'sync', 'backup']
        }
        
        low_difficulty_keywords = {
            'zh': ['界面', '颜色', '字体', '布局', '显示'],
            'en': ['interface', 'color', 'font', 'layout', 'display']
        }
        
        text_lower = text.lower()
        
        # 检查高难度关键词
        high_count = sum(1 for keyword in high_difficulty_keywords.get(language, []) if keyword in text_lower)
        medium_count = sum(1 for keyword in medium_difficulty_keywords.get(language, []) if keyword in text_lower)
        low_count = sum(1 for keyword in low_difficulty_keywords.get(language, []) if keyword in text_lower)
        
        if high_count >= 2:
            difficulty_score = 5
        elif high_count >= 1:
            difficulty_score = 4
        elif medium_count >= 2:
            difficulty_score = 3
        elif medium_count >= 1 or low_count >= 2:
            difficulty_score = 2
        else:
            difficulty_score = 1
        
        # 基于文本长度调整
        if len(text) > 200:
            difficulty_score = min(5, difficulty_score + 1)
        
        return difficulty_score
    
    def categorize_complaint(self, text: str, keywords: List[str]) -> str:
        """对投诉进行分类"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name, keywords FROM categories')
        categories = cursor.fetchall()
        conn.close()
        
        text_lower = text.lower()
        category_scores = {}
        
        for category_name, category_keywords in categories:
            score = 0
            category_keyword_list = category_keywords.split(',')
            
            for keyword in category_keyword_list:
                if keyword.strip().lower() in text_lower:
                    score += 2
            
            # 检查提取的关键词
            for keyword in keywords:
                if keyword.lower() in [ck.strip().lower() for ck in category_keyword_list]:
                    score += 1
            
            category_scores[category_name] = score
        
        # 返回得分最高的分类
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return '其他'
    
    def calculate_sentiment_score(self, text: str, language: str) -> float:
        """计算情感分数"""
        if language == 'en':
            blob = TextBlob(text)
            return blob.sentiment.polarity
        else:
            # 简单的中文情感分析
            negative_words = ['不好', '差', '烂', '垃圾', '讨厌', '失望', '糟糕', '问题', '错误', '故障']
            positive_words = ['好', '棒', '优秀', '满意', '喜欢', '不错', '完美']
            
            negative_count = sum(1 for word in negative_words if word in text)
            positive_count = sum(1 for word in positive_words if word in text)
            
            if negative_count + positive_count == 0:
                return 0.0
            
            return (positive_count - negative_count) / (positive_count + negative_count)
    
    def search_complaints(self, query: str, max_results: int = 100) -> List[Dict]:
        """搜索抱怨和问题相关的推文"""
        if not self.api:
            logger.error("Twitter API未初始化")
            return []
        
        complaints = []
        
        try:
            # 构建搜索查询
            complaint_keywords = [
                "问题", "bug", "错误", "故障", "不能用", "崩溃", "卡顿",
                "problem", "issue", "error", "broken", "crash", "slow",
                "差评", "吐槽", "抱怨", "不满", "失望",
                "complaint", "disappointed", "frustrated", "terrible"
            ]
            
            search_query = f"{query} ({' OR '.join(complaint_keywords)}) -is:retweet lang:zh OR lang:en"
            
            # 搜索推文
            tweets = tweepy.Paginator(
                self.api.search_recent_tweets,
                query=search_query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang']
            ).flatten(limit=max_results)
            
            for tweet in tweets:
                if not tweet.text:
                    continue
                
                # 过滤转发和回复
                if tweet.text.startswith('RT @') or tweet.text.startswith('@'):
                    continue
                
                language = self.detect_language(tweet.text)
                keywords = self.extract_keywords(tweet.text, language)
                difficulty = self.calculate_difficulty_level(tweet.text, language)
                category = self.categorize_complaint(tweet.text, keywords)
                sentiment = self.calculate_sentiment_score(tweet.text, language)
                
                complaint_data = {
                    'tweet_id': tweet.id,
                    'user_id': tweet.author_id,
                    'content': tweet.text,
                    'language': language,
                    'created_at': tweet.created_at,
                    'difficulty_level': difficulty,
                    'category': category,
                    'keywords': ','.join(keywords),
                    'sentiment_score': sentiment,
                    'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                    'like_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0,
                    'reply_count': tweet.public_metrics['reply_count'] if tweet.public_metrics else 0
                }
                
                complaints.append(complaint_data)
                
                # 添加延迟以避免API限制
                time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            logger.error(f"搜索推文时出错: {e}")
        
        logger.info(f"找到 {len(complaints)} 条相关推文")
        return complaints
    
    def save_complaints(self, complaints: List[Dict]):
        """保存抱怨数据到数据库"""
        if not complaints:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for complaint in complaints:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO complaints 
                    (tweet_id, user_id, username, content, language, created_at, 
                     difficulty_level, category, keywords, sentiment_score, 
                     retweet_count, like_count, reply_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    complaint['tweet_id'],
                    complaint['user_id'],
                    complaint.get('username', ''),
                    complaint['content'],
                    complaint['language'],
                    complaint['created_at'],
                    complaint['difficulty_level'],
                    complaint['category'],
                    complaint['keywords'],
                    complaint['sentiment_score'],
                    complaint['retweet_count'],
                    complaint['like_count'],
                    complaint['reply_count']
                ))
            except Exception as e:
                logger.error(f"保存数据时出错: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"成功保存 {len(complaints)} 条数据")
    
    def export_to_files(self, output_dir: str = 'output'):
        """导出数据到文件"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        conn = sqlite3.connect(self.db_path)
        
        # 导出所有数据
        df_all = pd.read_sql_query('SELECT * FROM complaints ORDER BY created_at DESC', conn)
        df_all.to_csv(f'{output_dir}/all_complaints.csv', index=False, encoding='utf-8')
        df_all.to_json(f'{output_dir}/all_complaints.json', orient='records', ensure_ascii=False, indent=2)
        
        # 按日期分组导出
        df_all['date'] = pd.to_datetime(df_all['created_at']).dt.date
        for date in df_all['date'].unique():
            date_df = df_all[df_all['date'] == date]
            date_str = str(date)
            date_df.to_csv(f'{output_dir}/complaints_{date_str}.csv', index=False, encoding='utf-8')
        
        # 按难度等级导出
        for level in range(1, 6):
            level_df = df_all[df_all['difficulty_level'] == level]
            if not level_df.empty:
                level_df.to_csv(f'{output_dir}/complaints_level_{level}.csv', index=False, encoding='utf-8')
        
        # 按分类导出
        for category in df_all['category'].unique():
            if pd.isna(category):
                continue
            cat_df = df_all[df_all['category'] == category]
            safe_category = re.sub(r'[^\w\-_\.]', '_', category)
            cat_df.to_csv(f'{output_dir}/complaints_{safe_category}.csv', index=False, encoding='utf-8')
        
        conn.close()
        logger.info(f"数据已导出到 {output_dir} 目录")
    
    def generate_report(self) -> str:
        """生成分析报告"""
        conn = sqlite3.connect(self.db_path)
        
        # 基本统计
        total_count = pd.read_sql_query('SELECT COUNT(*) as count FROM complaints', conn).iloc[0]['count']
        
        # 按语言统计
        lang_stats = pd.read_sql_query('''
            SELECT language, COUNT(*) as count 
            FROM complaints 
            GROUP BY language 
            ORDER BY count DESC
        ''', conn)
        
        # 按难度等级统计
        difficulty_stats = pd.read_sql_query('''
            SELECT difficulty_level, COUNT(*) as count 
            FROM complaints 
            GROUP BY difficulty_level 
            ORDER BY difficulty_level
        ''', conn)
        
        # 按分类统计
        category_stats = pd.read_sql_query('''
            SELECT category, COUNT(*) as count 
            FROM complaints 
            GROUP BY category 
            ORDER BY count DESC
        ''', conn)
        
        # 按日期统计
        daily_stats = pd.read_sql_query('''
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM complaints 
            GROUP BY DATE(created_at) 
            ORDER BY date DESC 
            LIMIT 7
        ''', conn)
        
        # 情感分析统计
        sentiment_stats = pd.read_sql_query('''
            SELECT 
                AVG(sentiment_score) as avg_sentiment,
                MIN(sentiment_score) as min_sentiment,
                MAX(sentiment_score) as max_sentiment
            FROM complaints
        ''', conn)
        
        conn.close()
        
        # 生成报告
        report = f"""
# X(Twitter) 用户吐槽分析报告

## 总体统计
- 总抓取数量: {total_count} 条
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 语言分布
{lang_stats.to_string(index=False)}

## 难度等级分布
{difficulty_stats.to_string(index=False)}

## 分类统计
{category_stats.to_string(index=False)}

## 最近7天数据量
{daily_stats.to_string(index=False)}

## 情感分析
- 平均情感分数: {sentiment_stats.iloc[0]['avg_sentiment']:.3f}
- 最负面分数: {sentiment_stats.iloc[0]['min_sentiment']:.3f}
- 最正面分数: {sentiment_stats.iloc[0]['max_sentiment']:.3f}

注：情感分数范围 -1.0 (最负面) 到 1.0 (最正面)
"""
        
        return report

def main():
    """主函数"""
    scraper = XScraper()
    
    # 示例搜索查询
    queries = [
        "微信",
        "支付宝", 
        "淘宝",
        "iPhone",
        "Android",
        "Windows"
    ]
    
    all_complaints = []
    
    for query in queries:
        logger.info(f"搜索关键词: {query}")
        complaints = scraper.search_complaints(query, max_results=50)
        all_complaints.extend(complaints)
        time.sleep(5)  # 避免API限制
    
    # 保存数据
    if all_complaints:
        scraper.save_complaints(all_complaints)
        
        # 导出文件
        scraper.export_to_files()
        
        # 生成报告
        report = scraper.generate_report()
        with open('output/analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        logger.info("抓取和分析完成！")
    else:
        logger.warning("未找到相关数据")

if __name__ == "__main__":
    main()