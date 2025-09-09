#!/usr/bin/env python3
"""
X(Twitter)吐槽抓取和分析系统主程序
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import json

from src.twitter_scraper import TwitterScraper
from src.text_analyzer import TextAnalyzer
from src.data_manager import DataManager
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_complaints.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ComplaintAnalysisSystem:
    def __init__(self, use_api=True):
        self.scraper = TwitterScraper(use_api=use_api)
        self.analyzer = TextAnalyzer()
        self.data_manager = DataManager(config.DATA_CONFIG['path'])
        
    def run_analysis(self, keywords: List[str] = None, 
                    max_tweets: int = None,
                    days_back: int = None) -> Dict[str, str]:
        """运行完整的分析流程"""
        # 使用默认值
        if not keywords:
            keywords = config.SEARCH_CONFIG['default_keywords']
        if not max_tweets:
            max_tweets = config.DATA_CONFIG['max_tweets_per_search']
        if not days_back:
            days_back = config.DATA_CONFIG['days_back']
        
        logger.info(f"Starting analysis for keywords: {keywords}")
        logger.info(f"Parameters: max_tweets={max_tweets}, days_back={days_back}")
        
        try:
            # 1. 抓取推文
            logger.info("Step 1: Scraping tweets...")
            raw_tweets = self.scraper.search_complaints(
                keywords=keywords,
                max_results=max_tweets,
                days_back=days_back
            )
            logger.info(f"Scraped {len(raw_tweets)} tweets")
            
            if not raw_tweets:
                logger.warning("No tweets found. Exiting.")
                return {}
            
            # 保存原始数据
            raw_file = self.data_manager.save_raw_tweets(raw_tweets)
            
            # 2. 分析推文
            logger.info("Step 2: Analyzing tweets...")
            analyzed_tweets = []
            
            for i, tweet in enumerate(raw_tweets):
                if i % 10 == 0:
                    logger.info(f"Analyzing tweet {i+1}/{len(raw_tweets)}")
                
                try:
                    analysis = self.analyzer.analyze_tweet(tweet)
                    analyzed_tweets.append(analysis)
                except Exception as e:
                    logger.error(f"Error analyzing tweet {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully analyzed {len(analyzed_tweets)} tweets")
            
            # 3. 保存分析结果
            logger.info("Step 3: Saving analysis results...")
            saved_files = self.data_manager.save_analyzed_data(analyzed_tweets)
            
            # 4. 生成统计摘要
            summary = self._generate_summary(analyzed_tweets)
            
            logger.info("Analysis completed successfully!")
            
            return {
                'raw_file': raw_file,
                'saved_files': saved_files,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise
        finally:
            self.scraper.close()
    
    def _generate_summary(self, analyzed_tweets: List[Dict]) -> Dict:
        """生成分析摘要"""
        total = len(analyzed_tweets)
        complaints = [t for t in analyzed_tweets if t.get('is_complaint', False)]
        
        summary = {
            'total_tweets_analyzed': total,
            'total_complaints': len(complaints),
            'complaint_rate': len(complaints) / total if total > 0 else 0,
            'languages': {},
            'sentiments': {},
            'difficulties': {},
            'categories': {},
            'keywords': []
        }
        
        # 统计各维度数据
        for tweet in analyzed_tweets:
            # 语言
            lang = tweet.get('language', 'unknown')
            summary['languages'][lang] = summary['languages'].get(lang, 0) + 1
            
            # 情感
            sentiment = tweet['sentiment']['sentiment']
            summary['sentiments'][sentiment] = summary['sentiments'].get(sentiment, 0) + 1
            
            # 难度
            difficulty = tweet['difficulty']['level']
            summary['difficulties'][difficulty] = summary['difficulties'].get(difficulty, 0) + 1
            
            # 类别
            for category in tweet.get('categories', []):
                summary['categories'][category] = summary['categories'].get(category, 0) + 1
        
        # 提取关键词
        if complaints:
            complaint_texts = [t['original_tweet']['text'] for t in complaints]
            keywords = self.analyzer.extract_keywords(complaint_texts, top_n=15)
            summary['keywords'] = keywords
        
        return summary
    
    def search_and_display(self, keywords: List[str] = None):
        """搜索并显示结果（交互式）"""
        results = self.run_analysis(keywords)
        
        if results and 'summary' in results:
            summary = results['summary']
            
            print("\n" + "="*60)
            print("📊 分析摘要 | Analysis Summary")
            print("="*60)
            
            print(f"\n总推文数 | Total tweets: {summary['total_tweets_analyzed']}")
            print(f"吐槽数量 | Complaints: {summary['total_complaints']} ({summary['complaint_rate']:.1%})")
            
            print(f"\n语言分布 | Language Distribution:")
            for lang, count in summary['languages'].items():
                lang_name = "中文" if lang == 'zh' else "English" if lang == 'en' else lang
                print(f"  - {lang_name}: {count}")
            
            print(f"\n情感分布 | Sentiment Distribution:")
            for sentiment, count in summary['sentiments'].items():
                emoji = "😊" if sentiment == 'positive' else "😐" if sentiment == 'neutral' else "😔"
                print(f"  {emoji} {sentiment}: {count}")
            
            print(f"\n难度分布 | Difficulty Distribution:")
            for difficulty, count in summary['difficulties'].items():
                level = "🟢 简单" if difficulty == 'easy' else "🟡 中等" if difficulty == 'medium' else "🔴 困难"
                print(f"  {level} ({difficulty}): {count}")
            
            print(f"\n问题类别 | Problem Categories:")
            sorted_categories = sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True)
            for category, count in sorted_categories[:5]:
                print(f"  - {category}: {count}")
            
            if summary['keywords']:
                print(f"\n热门关键词 | Top Keywords:")
                print(f"  {', '.join(summary['keywords'][:10])}")
            
            print(f"\n📁 数据已保存至 | Data saved to: {config.DATA_CONFIG['path']}/")
            print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='X(Twitter)吐槽抓取和分析系统 | Twitter Complaint Analysis System'
    )
    
    parser.add_argument(
        '-k', '--keywords',
        nargs='+',
        help='搜索关键词 | Keywords to search (space-separated)'
    )
    
    parser.add_argument(
        '-n', '--max-tweets',
        type=int,
        default=100,
        help='每个关键词最大抓取数量 | Maximum tweets per keyword (default: 100)'
    )
    
    parser.add_argument(
        '-d', '--days',
        type=int,
        default=7,
        help='搜索过去N天的数据 | Search tweets from past N days (default: 7)'
    )
    
    parser.add_argument(
        '--no-api',
        action='store_true',
        help='不使用API，使用网页爬虫 | Use web scraping instead of API'
    )
    
    parser.add_argument(
        '--analyze-existing',
        type=str,
        help='分析已存在的原始数据文件 | Analyze existing raw data file'
    )
    
    args = parser.parse_args()
    
    try:
        system = ComplaintAnalysisSystem(use_api=not args.no_api)
        
        if args.analyze_existing:
            # 分析已有数据
            logger.info(f"Analyzing existing file: {args.analyze_existing}")
            # TODO: 实现分析已有数据的功能
        else:
            # 执行新的搜索和分析
            system.search_and_display(
                keywords=args.keywords,
                max_tweets=args.max_tweets,
                days_back=args.days
            )
            
    except KeyboardInterrupt:
        logger.info("\nAnalysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()