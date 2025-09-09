"""
Twitter/X数据抓取模块
支持通过Twitter API和网页爬虫两种方式抓取数据
"""

import os
import json
import time
from datetime import datetime, timedelta
import tweepy
from typing import List, Dict, Optional
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterScraper:
    def __init__(self, use_api=True):
        self.use_api = use_api
        if use_api:
            self._init_api()
        else:
            self._init_selenium()
    
    def _init_api(self):
        """初始化Twitter API"""
        try:
            # 从环境变量获取认证信息
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            # 使用Bearer Token进行认证（v2 API）
            if bearer_token:
                self.client = tweepy.Client(bearer_token=bearer_token)
                logger.info("Twitter API v2 client initialized successfully")
            
            # 使用OAuth 1.0a进行认证（v1.1 API）
            if all([api_key, api_secret, access_token, access_token_secret]):
                auth = tweepy.OAuthHandler(api_key, api_secret)
                auth.set_access_token(access_token, access_token_secret)
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                logger.info("Twitter API v1.1 client initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise
    
    def _init_selenium(self):
        """初始化Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置代理
        proxy = os.getenv('HTTP_PROXY')
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options
        )
    
    def search_complaints_api(self, keywords: List[str], max_results: int = 100, 
                            days_back: int = 7) -> List[Dict]:
        """使用API搜索吐槽和问题相关的推文"""
        results = []
        
        # 构建搜索查询
        complaint_terms = [
            "problem", "issue", "bug", "error", "crash", "slow", "broken",
            "doesn't work", "not working", "failed", "failure", "sucks",
            "terrible", "awful", "hate", "annoying", "frustrated",
            "问题", "出错", "崩溃", "很慢", "坏了", "不能用", "失败",
            "糟糕", "讨厌", "烦人", "沮丧", "垃圾", "吐槽"
        ]
        
        # 对每个关键词进行搜索
        for keyword in keywords:
            # 构建包含吐槽词的查询
            query_parts = [f'"{keyword}"']
            query_parts.append(f'({" OR ".join(complaint_terms[:10])})')  # 限制查询长度
            query = ' '.join(query_parts) + ' -is:retweet'
            
            try:
                # 设置时间范围
                end_time = datetime.now()
                start_time = end_time - timedelta(days=days_back)
                
                # 使用Twitter API v2搜索
                tweets = self.client.search_recent_tweets(
                    query=query,
                    max_results=min(max_results, 100),
                    start_time=start_time.isoformat() + 'Z',
                    end_time=end_time.isoformat() + 'Z',
                    tweet_fields=['created_at', 'author_id', 'lang', 'public_metrics', 'context_annotations'],
                    user_fields=['username', 'name'],
                    expansions=['author_id']
                )
                
                if tweets.data:
                    users = {u.id: u for u in tweets.includes.get('users', [])}
                    
                    for tweet in tweets.data:
                        user = users.get(tweet.author_id, {})
                        results.append({
                            'id': tweet.id,
                            'text': tweet.text,
                            'created_at': tweet.created_at,
                            'author_username': getattr(user, 'username', 'unknown'),
                            'author_name': getattr(user, 'name', 'unknown'),
                            'lang': tweet.lang,
                            'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                            'like_count': tweet.public_metrics.get('like_count', 0),
                            'reply_count': tweet.public_metrics.get('reply_count', 0),
                            'keyword': keyword,
                            'source': 'api'
                        })
                
                logger.info(f"Found {len(tweets.data) if tweets.data else 0} tweets for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error searching for keyword {keyword}: {e}")
                continue
        
        return results
    
    def search_complaints_selenium(self, keywords: List[str], max_results: int = 100) -> List[Dict]:
        """使用Selenium爬虫搜索吐槽和问题相关的推文"""
        results = []
        
        complaint_terms = ["problem", "issue", "bug", "error", "问题", "出错", "吐槽"]
        
        for keyword in keywords:
            for complaint_term in complaint_terms[:3]:  # 限制搜索数量
                search_query = f"{keyword} {complaint_term}"
                search_url = f"https://twitter.com/search?q={search_query}&src=typed_query&f=live"
                
                try:
                    self.driver.get(search_url)
                    time.sleep(3)  # 等待页面加载
                    
                    # 滚动加载更多推文
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    tweets_collected = 0
                    
                    while tweets_collected < max_results:
                        # 获取推文元素
                        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                        
                        for element in tweet_elements[tweets_collected:]:
                            try:
                                # 提取推文文本
                                text_element = element.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                                text = text_element.text
                                
                                # 提取时间
                                time_element = element.find_element(By.TAG_NAME, 'time')
                                created_at = time_element.get_attribute('datetime')
                                
                                # 提取用户信息
                                user_element = element.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Names"]')
                                username = user_element.find_element(By.CSS_SELECTOR, 'span').text
                                
                                results.append({
                                    'text': text,
                                    'created_at': created_at,
                                    'author_username': username,
                                    'keyword': keyword,
                                    'source': 'selenium'
                                })
                                
                                tweets_collected += 1
                                
                            except Exception as e:
                                logger.debug(f"Error extracting tweet: {e}")
                                continue
                        
                        # 滚动页面
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        
                        # 检查是否有新内容
                        new_height = self.driver.execute_script("return document.body.scrollHeight")
                        if new_height == last_height:
                            break
                        last_height = new_height
                    
                    logger.info(f"Collected {tweets_collected} tweets for {search_query}")
                    
                except Exception as e:
                    logger.error(f"Error with Selenium search for {search_query}: {e}")
                    continue
        
        return results
    
    def search_complaints(self, keywords: List[str], max_results: int = 100, 
                         days_back: int = 7) -> List[Dict]:
        """搜索吐槽和问题相关的推文"""
        if self.use_api and hasattr(self, 'client'):
            return self.search_complaints_api(keywords, max_results, days_back)
        else:
            return self.search_complaints_selenium(keywords, max_results)
    
    def close(self):
        """关闭资源"""
        if hasattr(self, 'driver'):
            self.driver.quit()


if __name__ == "__main__":
    # 测试代码
    from dotenv import load_dotenv
    load_dotenv()
    
    scraper = TwitterScraper(use_api=True)
    results = scraper.search_complaints(["ChatGPT", "OpenAI"], max_results=10)
    
    for tweet in results[:5]:
        print(f"\n{tweet['created_at']}: {tweet['text'][:100]}...")