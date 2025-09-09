"""
文本分析和分类模块
支持中英文文本的情感分析、问题分类和难度评估
"""

import re
import jieba
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from langdetect import detect
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging
from typing import List, Dict, Tuple

# 下载必要的NLTK数据
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
except:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextAnalyzer:
    def __init__(self):
        # 初始化情感分析器
        self.sia = SentimentIntensityAnalyzer()
        
        # 初始化中文情感分析（使用预训练模型）
        try:
            self.zh_sentiment = pipeline(
                "sentiment-analysis", 
                model="uer/roberta-base-finetuned-jd-binary-chinese",
                device=-1  # 使用CPU
            )
        except:
            logger.warning("Failed to load Chinese sentiment model, using rule-based approach")
            self.zh_sentiment = None
        
        # 问题类别关键词
        self.problem_categories = {
            'technical': {
                'en': ['bug', 'error', 'crash', 'freeze', 'slow', 'lag', 'broken', 'fail', 'glitch', 'issue'],
                'zh': ['错误', '崩溃', '卡死', '很慢', '延迟', '故障', '失败', 'bug', '问题', '闪退']
            },
            'usability': {
                'en': ['confusing', 'difficult', 'hard to use', 'complicated', 'unclear', 'unintuitive'],
                'zh': ['难用', '复杂', '不清楚', '困惑', '不直观', '麻烦', '繁琐']
            },
            'feature_request': {
                'en': ['need', 'want', 'wish', 'should have', 'missing', 'add', 'feature', 'improve'],
                'zh': ['需要', '希望', '想要', '应该有', '缺少', '添加', '功能', '改进']
            },
            'performance': {
                'en': ['slow', 'lag', 'memory', 'cpu', 'battery', 'performance', 'resource'],
                'zh': ['很慢', '卡顿', '内存', '处理器', '电池', '性能', '资源', '占用']
            },
            'compatibility': {
                'en': ['not compatible', 'doesn\'t work with', 'support', 'version', 'update'],
                'zh': ['不兼容', '不支持', '版本', '更新', '适配']
            },
            'service': {
                'en': ['customer service', 'support', 'response', 'help', 'contact'],
                'zh': ['客服', '服务', '支持', '回复', '帮助', '联系']
            }
        }
        
        # 难度评估关键词
        self.difficulty_indicators = {
            'easy': {
                'en': ['simple', 'basic', 'minor', 'small', 'quick fix', 'typo'],
                'zh': ['简单', '基础', '小', '快速修复', '错别字', '微调']
            },
            'medium': {
                'en': ['moderate', 'some', 'several', 'multiple', 'occasionally'],
                'zh': ['一般', '有些', '几个', '多个', '偶尔', '中等']
            },
            'hard': {
                'en': ['complex', 'major', 'critical', 'severe', 'always', 'completely', 'urgent'],
                'zh': ['复杂', '严重', '关键', '紧急', '总是', '完全', '重大']
            }
        }
    
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        try:
            lang = detect(text)
            return 'zh' if lang in ['zh-cn', 'zh-tw'] else 'en'
        except:
            # 通过字符判断
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            return 'zh' if chinese_chars > len(text) * 0.3 else 'en'
    
    def analyze_sentiment(self, text: str, lang: str = None) -> Dict:
        """分析文本情感"""
        if not lang:
            lang = self.detect_language(text)
        
        if lang == 'zh':
            return self._analyze_chinese_sentiment(text)
        else:
            return self._analyze_english_sentiment(text)
    
    def _analyze_english_sentiment(self, text: str) -> Dict:
        """分析英文情感"""
        # 使用VADER进行情感分析
        scores = self.sia.polarity_scores(text)
        
        # 使用TextBlob作为补充
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # 综合评分
        sentiment_score = (scores['compound'] + polarity) / 2
        
        if sentiment_score >= 0.1:
            sentiment = 'positive'
        elif sentiment_score <= -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'confidence': abs(sentiment_score)
        }
    
    def _analyze_chinese_sentiment(self, text: str) -> Dict:
        """分析中文情感"""
        if self.zh_sentiment:
            try:
                result = self.zh_sentiment(text)[0]
                label = result['label']
                score = result['score']
                
                # 转换标签
                if label == 'POSITIVE':
                    sentiment = 'positive'
                    sentiment_score = score
                else:
                    sentiment = 'negative'
                    sentiment_score = -score
                
                return {
                    'sentiment': sentiment,
                    'score': sentiment_score,
                    'confidence': score
                }
            except:
                pass
        
        # 基于规则的中文情感分析
        positive_words = ['好', '棒', '优秀', '喜欢', '满意', '方便', '快速', '稳定']
        negative_words = ['差', '烂', '糟糕', '垃圾', '失望', '麻烦', '慢', '卡']
        
        # 分词
        words = list(jieba.cut(text))
        
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        if neg_count > pos_count:
            sentiment = 'negative'
            score = -min(neg_count / len(words), 1.0)
        elif pos_count > neg_count:
            sentiment = 'positive'
            score = min(pos_count / len(words), 1.0)
        else:
            sentiment = 'neutral'
            score = 0.0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': abs(score)
        }
    
    def categorize_problem(self, text: str, lang: str = None) -> List[str]:
        """对问题进行分类"""
        if not lang:
            lang = self.detect_language(text)
        
        text_lower = text.lower()
        categories = []
        
        for category, keywords in self.problem_categories.items():
            keyword_list = keywords.get(lang, keywords['en'])
            if any(keyword in text_lower for keyword in keyword_list):
                categories.append(category)
        
        # 如果没有匹配到任何类别，返回'general'
        if not categories:
            categories = ['general']
        
        return categories
    
    def assess_difficulty(self, text: str, lang: str = None) -> Tuple[str, float]:
        """评估问题难度"""
        if not lang:
            lang = self.detect_language(text)
        
        text_lower = text.lower()
        scores = {'easy': 0, 'medium': 0, 'hard': 0}
        
        # 基于关键词评分
        for level, keywords in self.difficulty_indicators.items():
            keyword_list = keywords.get(lang, keywords['en'])
            matches = sum(1 for keyword in keyword_list if keyword in text_lower)
            scores[level] += matches
        
        # 基于文本长度调整（长文本可能意味着复杂问题）
        text_length = len(text)
        if text_length > 200:
            scores['hard'] += 1
        elif text_length < 50:
            scores['easy'] += 1
        
        # 基于情感强度调整（强烈负面情感可能意味着严重问题）
        sentiment = self.analyze_sentiment(text, lang)
        if sentiment['sentiment'] == 'negative' and sentiment['confidence'] > 0.7:
            scores['hard'] += 1
        
        # 确定最终难度
        total_score = sum(scores.values())
        if total_score == 0:
            return 'medium', 0.5
        
        # 计算加权分数
        weighted_score = (scores['easy'] * 1 + scores['medium'] * 2 + scores['hard'] * 3) / total_score
        
        if weighted_score <= 1.5:
            difficulty = 'easy'
            confidence = scores['easy'] / total_score
        elif weighted_score <= 2.5:
            difficulty = 'medium'
            confidence = scores['medium'] / total_score
        else:
            difficulty = 'hard'
            confidence = scores['hard'] / total_score
        
        return difficulty, confidence
    
    def extract_keywords(self, texts: List[str], lang: str = None, top_n: int = 10) -> List[str]:
        """提取关键词"""
        if not texts:
            return []
        
        if not lang:
            lang = self.detect_language(texts[0])
        
        if lang == 'zh':
            # 中文分词
            all_words = []
            for text in texts:
                words = jieba.cut(text)
                all_words.extend([w for w in words if len(w) > 1])
            
            # 统计词频
            word_freq = pd.Series(all_words).value_counts()
            
            # 过滤停用词
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
            keywords = [word for word in word_freq.index if word not in stop_words][:top_n]
            
        else:
            # 英文使用TF-IDF
            try:
                vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(texts)
                keywords = vectorizer.get_feature_names_out().tolist()
            except:
                # 简单的词频统计
                all_words = ' '.join(texts).lower().split()
                word_freq = pd.Series(all_words).value_counts()
                keywords = word_freq.index[:top_n].tolist()
        
        return keywords
    
    def analyze_tweet(self, tweet: Dict) -> Dict:
        """综合分析一条推文"""
        text = tweet.get('text', '')
        lang = self.detect_language(text)
        
        # 情感分析
        sentiment = self.analyze_sentiment(text, lang)
        
        # 问题分类
        categories = self.categorize_problem(text, lang)
        
        # 难度评估
        difficulty, difficulty_confidence = self.assess_difficulty(text, lang)
        
        # 构建分析结果
        analysis = {
            'original_tweet': tweet,
            'language': lang,
            'sentiment': sentiment,
            'categories': categories,
            'difficulty': {
                'level': difficulty,
                'confidence': difficulty_confidence
            },
            'is_complaint': sentiment['sentiment'] == 'negative' and sentiment['confidence'] > 0.5
        }
        
        return analysis


if __name__ == "__main__":
    # 测试代码
    analyzer = TextAnalyzer()
    
    # 测试英文
    en_text = "This app keeps crashing! It's so slow and buggy. Really frustrated with the performance."
    en_result = analyzer.analyze_tweet({'text': en_text})
    print("English analysis:", en_result)
    
    # 测试中文
    zh_text = "这个软件总是崩溃，太慢了，体验很差，希望能改进一下性能问题。"
    zh_result = analyzer.analyze_tweet({'text': zh_text})
    print("\nChinese analysis:", zh_result)