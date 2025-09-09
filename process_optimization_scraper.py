#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流程优化商机发现工具 - 基于Selenium的X(Twitter)抓取器
支持Mac和Windows系统，专门抓取流程优化相关的用户抱怨
"""

import os
import sys
import time
import random
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import platform
import subprocess
import requests
import zipfile
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('process_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessOptimizationScraper:
    def __init__(self):
        self.system = platform.system().lower()
        self.driver = None
        self.db_path = 'process_opportunities.db'
        self.setup_database()
        
        # 流程优化相关关键词
        self.process_keywords = {
            'zh': [
                '流程', '步骤', '手续', '办理', '排队', '等待', '审批', '申请',
                '繁琐', '复杂', '麻烦', '慢', '效率', '耗时', '浪费时间',
                '来回跑', '跑腿', '重复', '多次', '反复', '折腾',
                '客服', '人工', '转接', '等客服', '打不通',
                '系统', '网站', 'APP', '卡顿', '崩溃', '登录',
                '银行', '政务', '医院', '学校', '快递', '外卖',
                '退货', '退款', '换货', '售后', '维修'
            ],
            'en': [
                'process', 'procedure', 'workflow', 'steps', 'queue', 'wait', 'waiting',
                'approval', 'application', 'form', 'paperwork', 'bureaucracy',
                'complicated', 'complex', 'confusing', 'slow', 'inefficient', 'waste',
                'time-consuming', 'lengthy', 'tedious', 'frustrating',
                'customer service', 'support', 'call center', 'hold', 'transfer',
                'system', 'website', 'app', 'crash', 'login', 'error',
                'bank', 'government', 'hospital', 'school', 'delivery', 'shipping',
                'return', 'refund', 'exchange', 'repair', 'maintenance'
            ]
        }
        
        # 流程痛点分类
        self.pain_point_categories = {
            '效率问题': ['慢', '等待', '耗时', 'slow', 'wait', 'time-consuming'],
            '复杂度问题': ['复杂', '繁琐', '麻烦', 'complex', 'complicated', 'confusing'],
            '重复操作': ['重复', '反复', '多次', 'repeat', 'multiple', 'again'],
            '系统技术': ['系统', '网站', 'APP', 'system', 'website', 'app'],
            '人工服务': ['客服', '人工', '电话', 'customer service', 'support', 'call'],
            '流程设计': ['流程', '步骤', '手续', 'process', 'procedure', 'workflow'],
            '成本问题': ['贵', '费用', '收费', 'expensive', 'cost', 'fee'],
            '体验问题': ['体验', '不便', '麻烦', 'experience', 'inconvenient', 'hassle']
        }
    
    def setup_database(self):
        """设置数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建流程优化机会表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id TEXT UNIQUE,
                user_handle TEXT,
                content TEXT,
                language TEXT,
                created_at TIMESTAMP,
                pain_point_category TEXT,
                opportunity_score INTEGER,
                business_sector TEXT,
                process_type TEXT,
                optimization_potential TEXT,
                keywords TEXT,
                like_count INTEGER,
                retweet_count INTEGER,
                reply_count INTEGER,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建商机分析表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                description TEXT,
                frequency INTEGER,
                avg_opportunity_score REAL,
                potential_solution TEXT,
                market_size_estimate TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库设置完成")
    
    def get_chrome_driver_path(self):
        """根据系统类型获取Chrome驱动路径"""
        if self.system == 'darwin':  # macOS
            return './drivers/mac/chromedriver'
        elif self.system == 'windows':
            return './drivers/windows/chromedriver.exe'
        else:  # Linux
            return './drivers/linux/chromedriver'
    
    def download_chromedriver(self):
        """自动下载ChromeDriver"""
        drivers_dir = './drivers'
        
        if self.system == 'darwin':
            system_dir = 'mac'
            driver_url = 'https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_mac64.zip'
            driver_name = 'chromedriver'
        elif self.system == 'windows':
            system_dir = 'windows'
            driver_url = 'https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip'
            driver_name = 'chromedriver.exe'
        else:
            system_dir = 'linux'
            driver_url = 'https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip'
            driver_name = 'chromedriver'
        
        system_drivers_dir = os.path.join(drivers_dir, system_dir)
        driver_path = os.path.join(system_drivers_dir, driver_name)
        
        # 如果驱动已存在，直接返回
        if os.path.exists(driver_path):
            return driver_path
        
        # 创建目录
        os.makedirs(system_drivers_dir, exist_ok=True)
        
        try:
            logger.info(f"正在下载 {self.system} 系统的ChromeDriver...")
            response = requests.get(driver_url)
            zip_path = os.path.join(system_drivers_dir, 'chromedriver.zip')
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # 解压
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(system_drivers_dir)
            
            # 删除zip文件
            os.remove(zip_path)
            
            # 给驱动文件执行权限 (Mac/Linux)
            if self.system in ['darwin', 'linux']:
                os.chmod(driver_path, 0o755)
            
            logger.info(f"ChromeDriver下载完成: {driver_path}")
            return driver_path
            
        except Exception as e:
            logger.error(f"下载ChromeDriver失败: {e}")
            return None
    
    def setup_chrome_driver(self, headless=True):
        """设置Chrome浏览器驱动"""
        try:
            # 获取或下载驱动
            driver_path = self.download_chromedriver()
            if not driver_path:
                logger.error("无法获取ChromeDriver")
                return None
            
            # Chrome选项
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            # 创建服务
            service = Service(driver_path)
            
            # 创建驱动
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome驱动设置成功")
            return self.driver
            
        except Exception as e:
            logger.error(f"设置Chrome驱动失败: {e}")
            return None
    
    def search_process_complaints(self, search_terms, max_tweets=50):
        """搜索流程相关抱怨"""
        if not self.driver:
            logger.error("浏览器驱动未初始化")
            return []
        
        complaints = []
        
        for term in search_terms:
            try:
                # 构建搜索URL
                search_query = f"{term} (流程 OR 步骤 OR 麻烦 OR 复杂 OR process OR procedure OR complicated)"
                search_url = f"https://twitter.com/search?q={search_query}&src=typed_query&f=live"
                
                logger.info(f"搜索关键词: {term}")
                self.driver.get(search_url)
                
                # 等待页面加载
                time.sleep(3)
                
                # 滚动加载更多推文
                for _ in range(5):  # 滚动5次
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # 查找推文元素
                tweets = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                
                for tweet in tweets[:max_tweets]:
                    try:
                        complaint_data = self.extract_tweet_data(tweet, term)
                        if complaint_data and self.is_process_related(complaint_data['content']):
                            complaints.append(complaint_data)
                    except Exception as e:
                        logger.warning(f"提取推文数据失败: {e}")
                        continue
                
                # 随机延迟避免被检测
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"搜索 {term} 时出错: {e}")
                continue
        
        logger.info(f"共找到 {len(complaints)} 条流程相关抱怨")
        return complaints
    
    def extract_tweet_data(self, tweet_element, search_term):
        """提取推文数据"""
        try:
            # 提取推文内容
            content_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            content = content_element.text if content_element else ""
            
            # 提取用户信息
            try:
                user_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"] a')
                user_handle = user_element.get_attribute('href').split('/')[-1] if user_element else ""
            except:
                user_handle = ""
            
            # 提取互动数据
            like_count = self.extract_count(tweet_element, '[data-testid="like"]')
            retweet_count = self.extract_count(tweet_element, '[data-testid="retweet"]')
            reply_count = self.extract_count(tweet_element, '[data-testid="reply"]')
            
            # 生成唯一ID
            tweet_id = f"{user_handle}_{hash(content)}_{int(time.time())}"
            
            # 分析内容
            language = self.detect_language(content)
            pain_category = self.categorize_pain_point(content)
            opportunity_score = self.calculate_opportunity_score(content, like_count, retweet_count)
            business_sector = self.identify_business_sector(content)
            process_type = self.identify_process_type(content)
            
            return {
                'tweet_id': tweet_id,
                'user_handle': user_handle,
                'content': content,
                'language': language,
                'created_at': datetime.now(),
                'pain_point_category': pain_category,
                'opportunity_score': opportunity_score,
                'business_sector': business_sector,
                'process_type': process_type,
                'optimization_potential': self.assess_optimization_potential(content),
                'keywords': search_term,
                'like_count': like_count,
                'retweet_count': retweet_count,
                'reply_count': reply_count
            }
            
        except Exception as e:
            logger.warning(f"提取推文数据时出错: {e}")
            return None
    
    def extract_count(self, tweet_element, selector):
        """提取互动数量"""
        try:
            count_element = tweet_element.find_element(By.CSS_SELECTOR, selector)
            count_text = count_element.text
            if count_text:
                # 处理K, M等单位
                if 'K' in count_text:
                    return int(float(count_text.replace('K', '')) * 1000)
                elif 'M' in count_text:
                    return int(float(count_text.replace('M', '')) * 1000000)
                else:
                    return int(count_text) if count_text.isdigit() else 0
            return 0
        except:
            return 0
    
    def detect_language(self, text):
        """检测语言"""
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_chars = len([c for c in text if c.isalpha() and ord(c) < 128])
        
        if chinese_chars > english_chars:
            return 'zh'
        elif english_chars > 0:
            return 'en'
        return 'unknown'
    
    def is_process_related(self, content):
        """判断是否与流程相关"""
        content_lower = content.lower()
        
        # 检查中英文关键词
        for lang in ['zh', 'en']:
            for keyword in self.process_keywords[lang]:
                if keyword in content_lower:
                    return True
        
        return False
    
    def categorize_pain_point(self, content):
        """分类痛点"""
        content_lower = content.lower()
        category_scores = {}
        
        for category, keywords in self.pain_point_categories.items():
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    score += 1
            category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return '其他'
    
    def calculate_opportunity_score(self, content, like_count, retweet_count):
        """计算商机分数 (1-10)"""
        score = 1
        
        # 基于互动数量
        total_engagement = like_count + retweet_count * 2
        if total_engagement > 100:
            score += 3
        elif total_engagement > 50:
            score += 2
        elif total_engagement > 10:
            score += 1
        
        # 基于痛点强度关键词
        pain_intensity_keywords = {
            'zh': ['太', '非常', '极其', '超级', '特别', '真的', '完全', '根本'],
            'en': ['very', 'extremely', 'super', 'really', 'totally', 'completely', 'absolutely']
        }
        
        content_lower = content.lower()
        for lang_keywords in pain_intensity_keywords.values():
            for keyword in lang_keywords:
                if keyword in content_lower:
                    score += 1
                    break
        
        # 基于频次词汇
        frequency_keywords = {
            'zh': ['每次', '总是', '经常', '老是', '一直', '反复'],
            'en': ['every time', 'always', 'often', 'constantly', 'repeatedly']
        }
        
        for lang_keywords in frequency_keywords.values():
            for keyword in lang_keywords:
                if keyword in content_lower:
                    score += 2
                    break
        
        return min(score, 10)  # 最高10分
    
    def identify_business_sector(self, content):
        """识别业务领域"""
        content_lower = content.lower()
        
        sectors = {
            '金融服务': ['银行', '支付', '贷款', '信用卡', 'bank', 'payment', 'loan', 'credit'],
            '电商购物': ['淘宝', '京东', '购物', '下单', 'shopping', 'order', 'amazon', 'ebay'],
            '政务服务': ['政府', '办证', '户籍', '社保', 'government', 'license', 'permit'],
            '医疗健康': ['医院', '挂号', '看病', '医保', 'hospital', 'appointment', 'medical'],
            '教育培训': ['学校', '报名', '考试', '学籍', 'school', 'enrollment', 'exam'],
            '物流快递': ['快递', '物流', '配送', '包裹', 'delivery', 'shipping', 'package'],
            '餐饮外卖': ['外卖', '点餐', '配送', 'food delivery', 'takeout', 'restaurant'],
            '交通出行': ['打车', '地铁', '公交', '停车', 'taxi', 'subway', 'parking'],
            '房产租赁': ['租房', '买房', '中介', 'rent', 'real estate', 'property'],
            '客户服务': ['客服', '售后', '投诉', 'customer service', 'support', 'complaint']
        }
        
        for sector, keywords in sectors.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return sector
        
        return '其他'
    
    def identify_process_type(self, content):
        """识别流程类型"""
        content_lower = content.lower()
        
        process_types = {
            '注册登录': ['注册', '登录', '验证', 'register', 'login', 'verification'],
            '申请审批': ['申请', '审批', '审核', 'application', 'approval', 'review'],
            '支付结算': ['支付', '付款', '结算', 'payment', 'checkout', 'billing'],
            '退换货': ['退货', '退款', '换货', 'return', 'refund', 'exchange'],
            '客户服务': ['客服', '咨询', '投诉', 'customer service', 'inquiry', 'complaint'],
            '预约排队': ['预约', '排队', '等号', 'appointment', 'queue', 'waiting'],
            '信息查询': ['查询', '搜索', '查看', 'search', 'query', 'check'],
            '数据录入': ['填写', '录入', '提交', 'fill', 'input', 'submit']
        }
        
        for process_type, keywords in process_types.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return process_type
        
        return '其他'
    
    def assess_optimization_potential(self, content):
        """评估优化潜力"""
        content_lower = content.lower()
        
        # 高优化潜力指标
        high_potential = ['自动化', '简化', '一键', '直接', 'automation', 'simplify', 'direct']
        medium_potential = ['改进', '优化', '提升', 'improve', 'optimize', 'enhance']
        low_potential = ['习惯', '接受', '理解', 'used to', 'accept', 'understand']
        
        for keyword in high_potential:
            if keyword in content_lower:
                return '高'
        
        for keyword in medium_potential:
            if keyword in content_lower:
                return '中'
        
        for keyword in low_potential:
            if keyword in content_lower:
                return '低'
        
        # 默认基于痛点强度判断
        pain_words = ['太', '非常', '极其', 'very', 'extremely', 'terrible']
        for word in pain_words:
            if word in content_lower:
                return '高'
        
        return '中'
    
    def save_complaints(self, complaints):
        """保存抱怨数据"""
        if not complaints:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for complaint in complaints:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO process_complaints 
                    (tweet_id, user_handle, content, language, created_at, 
                     pain_point_category, opportunity_score, business_sector, 
                     process_type, optimization_potential, keywords, 
                     like_count, retweet_count, reply_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    complaint['tweet_id'],
                    complaint['user_handle'],
                    complaint['content'],
                    complaint['language'],
                    complaint['created_at'],
                    complaint['pain_point_category'],
                    complaint['opportunity_score'],
                    complaint['business_sector'],
                    complaint['process_type'],
                    complaint['optimization_potential'],
                    complaint['keywords'],
                    complaint['like_count'],
                    complaint['retweet_count'],
                    complaint['reply_count']
                ))
            except Exception as e:
                logger.error(f"保存数据时出错: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"成功保存 {len(complaints)} 条数据")
    
    def analyze_business_opportunities(self):
        """分析商业机会"""
        conn = sqlite3.connect(self.db_path)
        
        # 按痛点分类统计
        pain_point_analysis = pd.read_sql_query('''
            SELECT 
                pain_point_category,
                COUNT(*) as frequency,
                AVG(opportunity_score) as avg_score,
                business_sector,
                process_type,
                optimization_potential
            FROM process_complaints 
            GROUP BY pain_point_category, business_sector, process_type
            ORDER BY frequency DESC, avg_score DESC
        ''', conn)
        
        # 生成商机建议
        opportunities = []
        for _, row in pain_point_analysis.iterrows():
            if row['frequency'] >= 3 and row['avg_score'] >= 5:  # 高频高分的痛点
                opportunity = {
                    'category': row['pain_point_category'],
                    'description': f"{row['business_sector']}领域的{row['process_type']}流程优化",
                    'frequency': row['frequency'],
                    'avg_opportunity_score': row['avg_score'],
                    'potential_solution': self.generate_solution_suggestion(row),
                    'market_size_estimate': self.estimate_market_size(row['frequency'], row['avg_score'])
                }
                opportunities.append(opportunity)
        
        # 保存商机分析
        cursor = conn.cursor()
        cursor.execute('DELETE FROM business_opportunities')  # 清除旧数据
        
        for opp in opportunities:
            cursor.execute('''
                INSERT INTO business_opportunities 
                (category, description, frequency, avg_opportunity_score, 
                 potential_solution, market_size_estimate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                opp['category'],
                opp['description'],
                opp['frequency'],
                opp['avg_opportunity_score'],
                opp['potential_solution'],
                opp['market_size_estimate']
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"识别出 {len(opportunities)} 个商业机会")
        return opportunities
    
    def generate_solution_suggestion(self, row):
        """生成解决方案建议"""
        category = row['pain_point_category']
        sector = row['business_sector']
        process_type = row['process_type']
        
        solution_templates = {
            '效率问题': f"开发{sector}领域的{process_type}自动化工具，减少等待时间",
            '复杂度问题': f"设计简化版{process_type}流程，降低{sector}行业用户的操作复杂度",
            '重复操作': f"创建{process_type}一键式解决方案，消除{sector}中的重复步骤",
            '系统技术': f"优化{sector}的{process_type}系统架构，提升稳定性和用户体验",
            '人工服务': f"引入AI客服系统，改善{sector}的{process_type}人工服务效率",
            '流程设计': f"重新设计{sector}的{process_type}流程，采用更直观的用户界面",
            '成本问题': f"提供{sector}{process_type}的低成本替代方案或免费工具",
            '体验问题': f"开发专注于{sector}{process_type}用户体验的解决方案"
        }
        
        return solution_templates.get(category, f"优化{sector}的{process_type}流程")
    
    def estimate_market_size(self, frequency, avg_score):
        """估算市场规模"""
        if frequency >= 20 and avg_score >= 8:
            return "大型市场 (>1000万用户)"
        elif frequency >= 10 and avg_score >= 6:
            return "中型市场 (100万-1000万用户)"
        elif frequency >= 5 and avg_score >= 5:
            return "小型市场 (10万-100万用户)"
        else:
            return "细分市场 (<10万用户)"
    
    def export_results(self):
        """导出结果"""
        output_dir = 'process_optimization_output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        conn = sqlite3.connect(self.db_path)
        
        # 导出原始数据
        complaints_df = pd.read_sql_query('SELECT * FROM process_complaints ORDER BY opportunity_score DESC', conn)
        complaints_df.to_csv(f'{output_dir}/process_complaints.csv', index=False, encoding='utf-8')
        
        # 导出商机分析
        opportunities_df = pd.read_sql_query('SELECT * FROM business_opportunities ORDER BY avg_opportunity_score DESC', conn)
        opportunities_df.to_csv(f'{output_dir}/business_opportunities.csv', index=False, encoding='utf-8')
        
        conn.close()
        
        logger.info(f"结果已导出到 {output_dir} 目录")
    
    def generate_report(self):
        """生成分析报告"""
        conn = sqlite3.connect(self.db_path)
        
        # 基础统计
        total_complaints = pd.read_sql_query('SELECT COUNT(*) as count FROM process_complaints', conn).iloc[0]['count']
        opportunities = pd.read_sql_query('SELECT * FROM business_opportunities ORDER BY avg_opportunity_score DESC', conn)
        
        # 痛点分类统计
        pain_stats = pd.read_sql_query('''
            SELECT pain_point_category, COUNT(*) as count, AVG(opportunity_score) as avg_score
            FROM process_complaints 
            GROUP BY pain_point_category 
            ORDER BY count DESC
        ''', conn)
        
        # 业务领域统计
        sector_stats = pd.read_sql_query('''
            SELECT business_sector, COUNT(*) as count, AVG(opportunity_score) as avg_score
            FROM process_complaints 
            GROUP BY business_sector 
            ORDER BY count DESC
        ''', conn)
        
        conn.close()
        
        # 生成报告
        report = f"""# 流程优化商机发现分析报告

## 报告生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览
- **总抓取数量**: {total_complaints} 条流程相关抱怨
- **识别商机数量**: {len(opportunities)} 个
- **平均商机分数**: {opportunities['avg_opportunity_score'].mean():.2f}/10

## 痛点分类分析
"""
        
        for _, row in pain_stats.iterrows():
            report += f"- **{row['pain_point_category']}**: {row['count']} 条 (平均分数: {row['avg_score']:.2f})\n"
        
        report += f"""
## 业务领域分析
"""
        
        for _, row in sector_stats.iterrows():
            report += f"- **{row['business_sector']}**: {row['count']} 条 (平均分数: {row['avg_score']:.2f})\n"
        
        report += f"""
## 🎯 重点商业机会

"""
        
        for i, (_, opp) in enumerate(opportunities.head(10).iterrows(), 1):
            report += f"""### {i}. {opp['description']}
- **痛点类别**: {opp['category']}
- **出现频次**: {opp['frequency']} 次
- **机会分数**: {opp['avg_opportunity_score']:.2f}/10
- **市场规模**: {opp['market_size_estimate']}
- **解决方案**: {opp['potential_solution']}

"""
        
        report += f"""
## 💡 行动建议

### 优先级排序
1. **高频高分痛点** - 重点关注出现频次>10且分数>7的机会
2. **技术可行性** - 评估解决方案的技术实现难度
3. **市场规模** - 优先选择中大型市场机会

### 下一步行动
1. **深度调研** - 对TOP3商机进行详细市场调研
2. **原型开发** - 快速开发MVP验证解决方案
3. **用户验证** - 与目标用户深度访谈验证需求

## 📊 数据文件
- `process_complaints.csv` - 原始抱怨数据
- `business_opportunities.csv` - 商机分析数据

---
*本报告由流程优化商机发现工具自动生成*
"""
        
        # 保存报告
        output_dir = 'process_optimization_output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(f'{output_dir}/opportunity_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("分析报告生成完成")
        return report
    
    def run_full_analysis(self, search_terms, max_tweets_per_term=20):
        """运行完整分析流程"""
        try:
            # 设置浏览器
            if not self.setup_chrome_driver(headless=True):
                logger.error("浏览器设置失败")
                return
            
            # 搜索抱怨
            complaints = self.search_process_complaints(search_terms, max_tweets_per_term)
            
            if complaints:
                # 保存数据
                self.save_complaints(complaints)
                
                # 分析商机
                opportunities = self.analyze_business_opportunities()
                
                # 导出结果
                self.export_results()
                
                # 生成报告
                report = self.generate_report()
                
                print(f"\n🎉 分析完成！")
                print(f"📊 共抓取 {len(complaints)} 条流程相关抱怨")
                print(f"🎯 识别出 {len(opportunities)} 个商业机会")
                print(f"📁 结果保存在 process_optimization_output 目录")
                
                return opportunities
            else:
                logger.warning("未找到相关数据")
                return []
                
        except Exception as e:
            logger.error(f"分析过程出错: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """主函数"""
    print("🔧 流程优化商机发现工具")
    print("=" * 50)
    
    # 流程优化相关搜索词
    search_terms = [
        "银行办事太麻烦",
        "政务服务流程复杂",
        "医院挂号太复杂",
        "快递收发流程",
        "退货流程繁琐",
        "客服流程体验差",
        "banking process complicated",
        "government service process",
        "hospital appointment process",
        "return process frustrating"
    ]
    
    scraper = ProcessOptimizationScraper()
    opportunities = scraper.run_full_analysis(search_terms, max_tweets_per_term=15)
    
    if opportunities:
        print("\n🏆 TOP 5 商业机会:")
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. {opp['description']} (分数: {opp['avg_opportunity_score']:.1f})")

if __name__ == "__main__":
    main()