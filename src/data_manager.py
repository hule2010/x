"""
数据存储和管理模块
支持将分析后的数据按日期和难度分类存储
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
import jsonlines
from typing import List, Dict, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    def __init__(self, data_path: str = "./data"):
        self.data_path = Path(data_path)
        self._init_directories()
    
    def _init_directories(self):
        """初始化数据存储目录结构"""
        # 创建主目录
        self.data_path.mkdir(exist_ok=True)
        
        # 创建子目录
        directories = [
            'raw',  # 原始数据
            'processed',  # 处理后的数据
            'by_date',  # 按日期分类
            'by_difficulty',  # 按难度分类
            'by_category',  # 按问题类型分类
            'reports'  # 分析报告
        ]
        
        for dir_name in directories:
            (self.data_path / dir_name).mkdir(exist_ok=True)
            
        # 创建难度子目录
        for difficulty in ['easy', 'medium', 'hard']:
            (self.data_path / 'by_difficulty' / difficulty).mkdir(exist_ok=True)
    
    def save_raw_tweets(self, tweets: List[Dict], filename: str = None) -> str:
        """保存原始推文数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tweets_{timestamp}.jsonl"
        
        filepath = self.data_path / 'raw' / filename
        
        with jsonlines.open(filepath, mode='w') as writer:
            for tweet in tweets:
                writer.write(tweet)
        
        logger.info(f"Saved {len(tweets)} raw tweets to {filepath}")
        return str(filepath)
    
    def save_analyzed_data(self, analyzed_tweets: List[Dict]) -> Dict[str, str]:
        """保存分析后的数据，并按不同维度分类"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}
        
        # 1. 保存完整的分析数据
        all_data_file = self.data_path / 'processed' / f'analyzed_{timestamp}.jsonl'
        with jsonlines.open(all_data_file, mode='w') as writer:
            for tweet in analyzed_tweets:
                writer.write(tweet)
        saved_files['all_data'] = str(all_data_file)
        
        # 2. 按日期分类保存
        date_groups = self._group_by_date(analyzed_tweets)
        for date_str, tweets in date_groups.items():
            date_file = self.data_path / 'by_date' / f'{date_str}.jsonl'
            with jsonlines.open(date_file, mode='a') as writer:
                for tweet in tweets:
                    writer.write(tweet)
            saved_files[f'date_{date_str}'] = str(date_file)
        
        # 3. 按难度分类保存
        difficulty_groups = self._group_by_difficulty(analyzed_tweets)
        for difficulty, tweets in difficulty_groups.items():
            diff_file = self.data_path / 'by_difficulty' / difficulty / f'{timestamp}.jsonl'
            with jsonlines.open(diff_file, mode='w') as writer:
                for tweet in tweets:
                    writer.write(tweet)
            saved_files[f'difficulty_{difficulty}'] = str(diff_file)
        
        # 4. 按问题类型分类保存
        category_groups = self._group_by_category(analyzed_tweets)
        for category, tweets in category_groups.items():
            cat_dir = self.data_path / 'by_category' / category
            cat_dir.mkdir(exist_ok=True)
            cat_file = cat_dir / f'{timestamp}.jsonl'
            with jsonlines.open(cat_file, mode='w') as writer:
                for tweet in tweets:
                    writer.write(tweet)
            saved_files[f'category_{category}'] = str(cat_file)
        
        # 5. 生成并保存汇总报告
        report_file = self._generate_report(analyzed_tweets, timestamp)
        saved_files['report'] = report_file
        
        logger.info(f"Saved analyzed data to {len(saved_files)} files")
        return saved_files
    
    def _group_by_date(self, tweets: List[Dict]) -> Dict[str, List[Dict]]:
        """按日期分组"""
        date_groups = {}
        
        for tweet in tweets:
            # 获取推文日期
            created_at = tweet['original_tweet'].get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                else:
                    date = created_at.date()
                
                date_str = date.strftime('%Y-%m-%d')
                if date_str not in date_groups:
                    date_groups[date_str] = []
                date_groups[date_str].append(tweet)
        
        return date_groups
    
    def _group_by_difficulty(self, tweets: List[Dict]) -> Dict[str, List[Dict]]:
        """按难度分组"""
        difficulty_groups = {'easy': [], 'medium': [], 'hard': []}
        
        for tweet in tweets:
            difficulty = tweet['difficulty']['level']
            if difficulty in difficulty_groups:
                difficulty_groups[difficulty].append(tweet)
        
        return difficulty_groups
    
    def _group_by_category(self, tweets: List[Dict]) -> Dict[str, List[Dict]]:
        """按问题类型分组"""
        category_groups = {}
        
        for tweet in tweets:
            categories = tweet.get('categories', ['general'])
            for category in categories:
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(tweet)
        
        return category_groups
    
    def _generate_report(self, tweets: List[Dict], timestamp: str) -> str:
        """生成分析报告"""
        report = {
            'timestamp': timestamp,
            'total_tweets': len(tweets),
            'date_range': self._get_date_range(tweets),
            'language_distribution': self._get_language_distribution(tweets),
            'sentiment_distribution': self._get_sentiment_distribution(tweets),
            'difficulty_distribution': self._get_difficulty_distribution(tweets),
            'category_distribution': self._get_category_distribution(tweets),
            'top_complaints': self._get_top_complaints(tweets, n=10)
        }
        
        # 保存为JSON格式的报告
        report_file = self.data_path / 'reports' / f'report_{timestamp}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        # 同时生成Excel报告
        self._generate_excel_report(tweets, timestamp)
        
        return str(report_file)
    
    def _generate_excel_report(self, tweets: List[Dict], timestamp: str):
        """生成Excel格式的报告"""
        # 准备数据
        data_for_excel = []
        
        for tweet in tweets:
            original = tweet['original_tweet']
            row = {
                'Date': original.get('created_at', ''),
                'Author': original.get('author_username', ''),
                'Text': original.get('text', ''),
                'Language': tweet.get('language', ''),
                'Sentiment': tweet['sentiment']['sentiment'],
                'Sentiment Score': tweet['sentiment']['score'],
                'Categories': ', '.join(tweet.get('categories', [])),
                'Difficulty': tweet['difficulty']['level'],
                'Difficulty Confidence': tweet['difficulty']['confidence'],
                'Likes': original.get('like_count', 0),
                'Retweets': original.get('retweet_count', 0),
                'Replies': original.get('reply_count', 0)
            }
            data_for_excel.append(row)
        
        # 创建DataFrame
        df = pd.DataFrame(data_for_excel)
        
        # 保存到Excel
        excel_file = self.data_path / 'reports' / f'report_{timestamp}.xlsx'
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 主数据表
            df.to_excel(writer, sheet_name='All Tweets', index=False)
            
            # 按难度分组的表
            for difficulty in ['easy', 'medium', 'hard']:
                diff_df = df[df['Difficulty'] == difficulty]
                if not diff_df.empty:
                    diff_df.to_excel(writer, sheet_name=f'{difficulty.capitalize()} Issues', index=False)
            
            # 汇总统计表
            summary_data = {
                'Metric': ['Total Tweets', 'Negative Sentiment', 'Easy Issues', 'Medium Issues', 'Hard Issues'],
                'Count': [
                    len(df),
                    len(df[df['Sentiment'] == 'negative']),
                    len(df[df['Difficulty'] == 'easy']),
                    len(df[df['Difficulty'] == 'medium']),
                    len(df[df['Difficulty'] == 'hard'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logger.info(f"Generated Excel report: {excel_file}")
    
    def _get_date_range(self, tweets: List[Dict]) -> Dict[str, str]:
        """获取日期范围"""
        dates = []
        for tweet in tweets:
            created_at = tweet['original_tweet'].get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    date = created_at
                dates.append(date)
        
        if dates:
            return {
                'start': min(dates).strftime('%Y-%m-%d'),
                'end': max(dates).strftime('%Y-%m-%d')
            }
        return {'start': '', 'end': ''}
    
    def _get_language_distribution(self, tweets: List[Dict]) -> Dict[str, int]:
        """获取语言分布"""
        lang_count = {}
        for tweet in tweets:
            lang = tweet.get('language', 'unknown')
            lang_count[lang] = lang_count.get(lang, 0) + 1
        return lang_count
    
    def _get_sentiment_distribution(self, tweets: List[Dict]) -> Dict[str, int]:
        """获取情感分布"""
        sentiment_count = {}
        for tweet in tweets:
            sentiment = tweet['sentiment']['sentiment']
            sentiment_count[sentiment] = sentiment_count.get(sentiment, 0) + 1
        return sentiment_count
    
    def _get_difficulty_distribution(self, tweets: List[Dict]) -> Dict[str, int]:
        """获取难度分布"""
        difficulty_count = {}
        for tweet in tweets:
            difficulty = tweet['difficulty']['level']
            difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1
        return difficulty_count
    
    def _get_category_distribution(self, tweets: List[Dict]) -> Dict[str, int]:
        """获取类别分布"""
        category_count = {}
        for tweet in tweets:
            for category in tweet.get('categories', []):
                category_count[category] = category_count.get(category, 0) + 1
        return category_count
    
    def _get_top_complaints(self, tweets: List[Dict], n: int = 10) -> List[Dict]:
        """获取最受关注的吐槽（基于互动数）"""
        complaints = []
        
        for tweet in tweets:
            if tweet.get('is_complaint', False):
                original = tweet['original_tweet']
                engagement = (original.get('like_count', 0) + 
                            original.get('retweet_count', 0) * 2 + 
                            original.get('reply_count', 0) * 1.5)
                
                complaints.append({
                    'text': original.get('text', ''),
                    'engagement': engagement,
                    'difficulty': tweet['difficulty']['level'],
                    'categories': tweet.get('categories', []),
                    'created_at': original.get('created_at', '')
                })
        
        # 按互动数排序
        complaints.sort(key=lambda x: x['engagement'], reverse=True)
        
        return complaints[:n]
    
    def load_tweets_by_date(self, date: str) -> List[Dict]:
        """加载特定日期的推文"""
        file_path = self.data_path / 'by_date' / f'{date}.jsonl'
        tweets = []
        
        if file_path.exists():
            with jsonlines.open(file_path) as reader:
                for tweet in reader:
                    tweets.append(tweet)
        
        return tweets
    
    def load_tweets_by_difficulty(self, difficulty: str) -> List[Dict]:
        """加载特定难度的推文"""
        tweets = []
        diff_dir = self.data_path / 'by_difficulty' / difficulty
        
        if diff_dir.exists():
            for file_path in diff_dir.glob('*.jsonl'):
                with jsonlines.open(file_path) as reader:
                    for tweet in reader:
                        tweets.append(tweet)
        
        return tweets
    
    def get_summary_stats(self) -> Dict:
        """获取汇总统计信息"""
        stats = {
            'total_raw_files': len(list((self.data_path / 'raw').glob('*.jsonl'))),
            'total_processed_files': len(list((self.data_path / 'processed').glob('*.jsonl'))),
            'date_files': len(list((self.data_path / 'by_date').glob('*.jsonl'))),
            'reports': len(list((self.data_path / 'reports').glob('*.json'))),
            'last_update': None
        }
        
        # 获取最后更新时间
        processed_files = list((self.data_path / 'processed').glob('*.jsonl'))
        if processed_files:
            latest_file = max(processed_files, key=lambda x: x.stat().st_mtime)
            stats['last_update'] = datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        return stats


if __name__ == "__main__":
    # 测试代码
    manager = DataManager()
    
    # 测试数据
    test_tweets = [
        {
            'original_tweet': {
                'text': 'This app crashes constantly!',
                'created_at': datetime.now().isoformat(),
                'author_username': 'user1',
                'like_count': 10,
                'retweet_count': 5
            },
            'language': 'en',
            'sentiment': {'sentiment': 'negative', 'score': -0.8, 'confidence': 0.8},
            'categories': ['technical'],
            'difficulty': {'level': 'hard', 'confidence': 0.7},
            'is_complaint': True
        }
    ]
    
    # 保存数据
    saved_files = manager.save_analyzed_data(test_tweets)
    print("Saved files:", saved_files)
    
    # 获取统计信息
    stats = manager.get_summary_stats()
    print("Summary stats:", stats)