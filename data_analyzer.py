#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X数据分析和可视化工具
提供详细的数据分析、趋势分析和可视化图表
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from collections import Counter
import json
import os
from wordcloud import WordCloud
import jieba
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class DataAnalyzer:
    def __init__(self, db_path: str = 'x_complaints.db'):
        self.db_path = db_path
        self.output_dir = 'analysis_output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_data(self) -> pd.DataFrame:
        """加载数据"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM complaints 
            ORDER BY created_at DESC
        ''', conn)
        conn.close()
        
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.date
            df['hour'] = df['created_at'].dt.hour
            df['weekday'] = df['created_at'].dt.day_name()
            
        return df
    
    def basic_statistics(self, df: pd.DataFrame) -> dict:
        """基础统计分析"""
        stats = {
            'total_complaints': len(df),
            'unique_users': df['user_id'].nunique() if 'user_id' in df.columns else 0,
            'date_range': {
                'start': df['created_at'].min().strftime('%Y-%m-%d') if not df.empty else None,
                'end': df['created_at'].max().strftime('%Y-%m-%d') if not df.empty else None
            },
            'language_distribution': df['language'].value_counts().to_dict() if 'language' in df.columns else {},
            'difficulty_distribution': df['difficulty_level'].value_counts().sort_index().to_dict() if 'difficulty_level' in df.columns else {},
            'category_distribution': df['category'].value_counts().to_dict() if 'category' in df.columns else {},
            'sentiment_stats': {
                'mean': df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0,
                'std': df['sentiment_score'].std() if 'sentiment_score' in df.columns else 0,
                'min': df['sentiment_score'].min() if 'sentiment_score' in df.columns else 0,
                'max': df['sentiment_score'].max() if 'sentiment_score' in df.columns else 0
            }
        }
        return stats
    
    def time_series_analysis(self, df: pd.DataFrame):
        """时间序列分析"""
        if df.empty:
            return
        
        # 按日期统计
        daily_counts = df.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        
        # 按小时统计
        hourly_counts = df.groupby('hour').size().reset_index(name='count')
        
        # 按星期统计
        weekday_counts = df.groupby('weekday').size().reset_index(name='count')
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_counts['weekday'] = pd.Categorical(weekday_counts['weekday'], categories=weekday_order, ordered=True)
        weekday_counts = weekday_counts.sort_values('weekday')
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('时间分析', fontsize=16)
        
        # 每日趋势
        axes[0, 0].plot(daily_counts['date'], daily_counts['count'], marker='o')
        axes[0, 0].set_title('每日吐槽数量趋势')
        axes[0, 0].set_xlabel('日期')
        axes[0, 0].set_ylabel('数量')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 小时分布
        axes[0, 1].bar(hourly_counts['hour'], hourly_counts['count'])
        axes[0, 1].set_title('小时分布')
        axes[0, 1].set_xlabel('小时')
        axes[0, 1].set_ylabel('数量')
        
        # 星期分布
        axes[1, 0].bar(range(len(weekday_counts)), weekday_counts['count'])
        axes[1, 0].set_title('星期分布')
        axes[1, 0].set_xlabel('星期')
        axes[1, 0].set_ylabel('数量')
        axes[1, 0].set_xticks(range(len(weekday_counts)))
        axes[1, 0].set_xticklabels([day[:3] for day in weekday_counts['weekday']], rotation=45)
        
        # 累计趋势
        daily_counts_sorted = daily_counts.sort_values('date')
        daily_counts_sorted['cumulative'] = daily_counts_sorted['count'].cumsum()
        axes[1, 1].plot(daily_counts_sorted['date'], daily_counts_sorted['cumulative'], marker='o')
        axes[1, 1].set_title('累计吐槽数量')
        axes[1, 1].set_xlabel('日期')
        axes[1, 1].set_ylabel('累计数量')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/time_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def difficulty_analysis(self, df: pd.DataFrame):
        """难度分析"""
        if df.empty or 'difficulty_level' not in df.columns:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('难度等级分析', fontsize=16)
        
        # 难度分布
        difficulty_counts = df['difficulty_level'].value_counts().sort_index()
        axes[0, 0].bar(difficulty_counts.index, difficulty_counts.values)
        axes[0, 0].set_title('难度等级分布')
        axes[0, 0].set_xlabel('难度等级')
        axes[0, 0].set_ylabel('数量')
        
        # 难度与情感的关系
        if 'sentiment_score' in df.columns:
            df.boxplot(column='sentiment_score', by='difficulty_level', ax=axes[0, 1])
            axes[0, 1].set_title('难度等级与情感分数关系')
            axes[0, 1].set_xlabel('难度等级')
            axes[0, 1].set_ylabel('情感分数')
        
        # 难度随时间变化
        daily_difficulty = df.groupby(['date', 'difficulty_level']).size().unstack(fill_value=0)
        daily_difficulty.plot(kind='area', stacked=True, ax=axes[1, 0])
        axes[1, 0].set_title('每日难度分布')
        axes[1, 0].set_xlabel('日期')
        axes[1, 0].set_ylabel('数量')
        axes[1, 0].legend(title='难度等级')
        
        # 难度与互动的关系
        if 'like_count' in df.columns:
            difficulty_engagement = df.groupby('difficulty_level')[['like_count', 'retweet_count', 'reply_count']].mean()
            difficulty_engagement.plot(kind='bar', ax=axes[1, 1])
            axes[1, 1].set_title('难度等级与互动关系')
            axes[1, 1].set_xlabel('难度等级')
            axes[1, 1].set_ylabel('平均互动数')
            axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/difficulty_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def category_analysis(self, df: pd.DataFrame):
        """分类分析"""
        if df.empty or 'category' not in df.columns:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('分类分析', fontsize=16)
        
        # 分类分布饼图
        category_counts = df['category'].value_counts()
        axes[0, 0].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('分类分布')
        
        # 分类与难度关系
        category_difficulty = df.groupby(['category', 'difficulty_level']).size().unstack(fill_value=0)
        category_difficulty.plot(kind='bar', stacked=True, ax=axes[0, 1])
        axes[0, 1].set_title('分类与难度关系')
        axes[0, 1].set_xlabel('分类')
        axes[0, 1].set_ylabel('数量')
        axes[0, 1].legend(title='难度等级')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 分类随时间变化
        daily_category = df.groupby(['date', 'category']).size().unstack(fill_value=0)
        daily_category.plot(ax=axes[1, 0])
        axes[1, 0].set_title('分类时间趋势')
        axes[1, 0].set_xlabel('日期')
        axes[1, 0].set_ylabel('数量')
        axes[1, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 分类与情感关系
        if 'sentiment_score' in df.columns:
            category_sentiment = df.groupby('category')['sentiment_score'].mean().sort_values()
            axes[1, 1].barh(range(len(category_sentiment)), category_sentiment.values)
            axes[1, 1].set_yticks(range(len(category_sentiment)))
            axes[1, 1].set_yticklabels(category_sentiment.index)
            axes[1, 1].set_title('分类平均情感分数')
            axes[1, 1].set_xlabel('情感分数')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/category_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def language_analysis(self, df: pd.DataFrame):
        """语言分析"""
        if df.empty or 'language' not in df.columns:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('语言分析', fontsize=16)
        
        # 语言分布
        lang_counts = df['language'].value_counts()
        axes[0, 0].pie(lang_counts.values, labels=lang_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('语言分布')
        
        # 语言与难度关系
        lang_difficulty = df.groupby(['language', 'difficulty_level']).size().unstack(fill_value=0)
        lang_difficulty.plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('语言与难度关系')
        axes[0, 1].set_xlabel('语言')
        axes[0, 1].set_ylabel('数量')
        axes[0, 1].legend(title='难度等级')
        
        # 语言随时间变化
        daily_lang = df.groupby(['date', 'language']).size().unstack(fill_value=0)
        daily_lang.plot(ax=axes[1, 0])
        axes[1, 0].set_title('语言时间趋势')
        axes[1, 0].set_xlabel('日期')
        axes[1, 0].set_ylabel('数量')
        axes[1, 0].legend()
        
        # 语言与情感关系
        if 'sentiment_score' in df.columns:
            df.boxplot(column='sentiment_score', by='language', ax=axes[1, 1])
            axes[1, 1].set_title('语言与情感分数关系')
            axes[1, 1].set_xlabel('语言')
            axes[1, 1].set_ylabel('情感分数')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/language_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_wordcloud(self, df: pd.DataFrame):
        """生成词云"""
        if df.empty or 'content' not in df.columns:
            return
        
        # 中文词云
        zh_texts = df[df['language'] == 'zh']['content'].dropna()
        if not zh_texts.empty:
            zh_text = ' '.join(zh_texts)
            # 使用jieba分词
            zh_words = jieba.cut(zh_text)
            zh_text_processed = ' '.join([word for word in zh_words if len(word) > 1])
            
            wordcloud_zh = WordCloud(
                font_path='simhei.ttf',  # 需要中文字体文件
                width=800, height=600,
                background_color='white',
                max_words=100
            ).generate(zh_text_processed)
            
            plt.figure(figsize=(10, 8))
            plt.imshow(wordcloud_zh, interpolation='bilinear')
            plt.axis('off')
            plt.title('中文词云', fontsize=16)
            plt.savefig(f'{self.output_dir}/wordcloud_chinese.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 英文词云
        en_texts = df[df['language'] == 'en']['content'].dropna()
        if not en_texts.empty:
            en_text = ' '.join(en_texts)
            
            wordcloud_en = WordCloud(
                width=800, height=600,
                background_color='white',
                max_words=100
            ).generate(en_text)
            
            plt.figure(figsize=(10, 8))
            plt.imshow(wordcloud_en, interpolation='bilinear')
            plt.axis('off')
            plt.title('English Word Cloud', fontsize=16)
            plt.savefig(f'{self.output_dir}/wordcloud_english.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def sentiment_analysis(self, df: pd.DataFrame):
        """情感分析"""
        if df.empty or 'sentiment_score' not in df.columns:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('情感分析', fontsize=16)
        
        # 情感分布
        axes[0, 0].hist(df['sentiment_score'], bins=20, alpha=0.7)
        axes[0, 0].set_title('情感分数分布')
        axes[0, 0].set_xlabel('情感分数')
        axes[0, 0].set_ylabel('频次')
        axes[0, 0].axvline(df['sentiment_score'].mean(), color='red', linestyle='--', label='平均值')
        axes[0, 0].legend()
        
        # 情感随时间变化
        daily_sentiment = df.groupby('date')['sentiment_score'].mean()
        axes[0, 1].plot(daily_sentiment.index, daily_sentiment.values, marker='o')
        axes[0, 1].set_title('情感时间趋势')
        axes[0, 1].set_xlabel('日期')
        axes[0, 1].set_ylabel('平均情感分数')
        axes[0, 1].axhline(0, color='gray', linestyle='--', alpha=0.5)
        
        # 情感与互动关系
        if 'like_count' in df.columns:
            axes[1, 0].scatter(df['sentiment_score'], df['like_count'], alpha=0.6)
            axes[1, 0].set_title('情感分数与点赞数关系')
            axes[1, 0].set_xlabel('情感分数')
            axes[1, 0].set_ylabel('点赞数')
        
        # 情感分类
        df['sentiment_category'] = pd.cut(df['sentiment_score'], 
                                        bins=[-1, -0.1, 0.1, 1], 
                                        labels=['负面', '中性', '正面'])
        sentiment_cat_counts = df['sentiment_category'].value_counts()
        axes[1, 1].pie(sentiment_cat_counts.values, labels=sentiment_cat_counts.index, autopct='%1.1f%%')
        axes[1, 1].set_title('情感分类分布')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_comprehensive_report(self, df: pd.DataFrame) -> str:
        """生成综合分析报告"""
        stats = self.basic_statistics(df)
        
        report = f"""# X(Twitter) 用户吐槽深度分析报告

## 报告生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览
- **总数据量**: {stats['total_complaints']:,} 条
- **独立用户数**: {stats['unique_users']:,} 人
- **数据时间范围**: {stats['date_range']['start']} 至 {stats['date_range']['end']}

## 语言分布
"""
        
        for lang, count in stats['language_distribution'].items():
            percentage = (count / stats['total_complaints']) * 100
            report += f"- {lang}: {count:,} 条 ({percentage:.1f}%)\n"
        
        report += f"""
## 难度等级分析
"""
        
        difficulty_labels = {1: '简单', 2: '较简单', 3: '中等', 4: '较困难', 5: '困难'}
        for level, count in stats['difficulty_distribution'].items():
            percentage = (count / stats['total_complaints']) * 100
            label = difficulty_labels.get(level, f'等级{level}')
            report += f"- {label} (等级{level}): {count:,} 条 ({percentage:.1f}%)\n"
        
        report += f"""
## 问题分类统计
"""
        
        for category, count in stats['category_distribution'].items():
            percentage = (count / stats['total_complaints']) * 100
            report += f"- {category}: {count:,} 条 ({percentage:.1f}%)\n"
        
        report += f"""
## 情感分析结果
- **平均情感分数**: {stats['sentiment_stats']['mean']:.3f}
- **情感分数标准差**: {stats['sentiment_stats']['std']:.3f}
- **最负面分数**: {stats['sentiment_stats']['min']:.3f}
- **最正面分数**: {stats['sentiment_stats']['max']:.3f}

*注：情感分数范围为 -1.0 (极度负面) 到 1.0 (极度正面)*

## 关键发现

### 1. 用户吐槽热点
"""
        
        if not df.empty and 'category' in df.columns:
            top_categories = df['category'].value_counts().head(3)
            for i, (category, count) in enumerate(top_categories.items(), 1):
                percentage = (count / len(df)) * 100
                report += f"{i}. **{category}** - 占比 {percentage:.1f}%\n"
        
        report += f"""
### 2. 问题难度分析
"""
        
        if stats['difficulty_distribution']:
            high_difficulty = sum(count for level, count in stats['difficulty_distribution'].items() if level >= 4)
            high_percentage = (high_difficulty / stats['total_complaints']) * 100
            report += f"- 高难度问题（等级4-5）占比: {high_percentage:.1f}%\n"
            
            low_difficulty = sum(count for level, count in stats['difficulty_distribution'].items() if level <= 2)
            low_percentage = (low_difficulty / stats['total_complaints']) * 100
            report += f"- 低难度问题（等级1-2）占比: {low_percentage:.1f}%\n"
        
        report += f"""
### 3. 用户情感状态
"""
        
        if stats['sentiment_stats']['mean'] < -0.2:
            sentiment_desc = "整体情感偏向负面"
        elif stats['sentiment_stats']['mean'] > 0.2:
            sentiment_desc = "整体情感偏向正面"
        else:
            sentiment_desc = "整体情感相对中性"
        
        report += f"- {sentiment_desc}（平均分数: {stats['sentiment_stats']['mean']:.3f}）\n"
        
        if not df.empty and 'sentiment_score' in df.columns:
            negative_count = len(df[df['sentiment_score'] < -0.1])
            negative_percentage = (negative_count / len(df)) * 100
            report += f"- 负面情感比例: {negative_percentage:.1f}%\n"
        
        report += f"""
## 建议和行动方案

### 优先处理建议
1. **关注高频问题类别** - 重点解决占比最高的问题类型
2. **优先处理高难度问题** - 高难度问题往往影响面更广
3. **改善用户体验** - 针对负面情感较多的领域进行优化

### 数据监控建议
1. **建立定期监控机制** - 每日/每周跟踪关键指标变化
2. **设置预警阈值** - 当某类问题激增时及时响应
3. **跨平台数据整合** - 结合其他社交平台数据获得全面视图

## 附件说明
- 详细数据文件: `output/` 目录
- 可视化图表: `analysis_output/` 目录
- 原始数据库: `x_complaints.db`
"""
        
        return report
    
    def run_complete_analysis(self):
        """运行完整分析"""
        print("开始加载数据...")
        df = self.load_data()
        
        if df.empty:
            print("未找到数据，请先运行数据抓取程序")
            return
        
        print(f"成功加载 {len(df)} 条数据")
        
        print("生成基础统计...")
        stats = self.basic_statistics(df)
        
        print("进行时间序列分析...")
        self.time_series_analysis(df)
        
        print("进行难度分析...")
        self.difficulty_analysis(df)
        
        print("进行分类分析...")
        self.category_analysis(df)
        
        print("进行语言分析...")
        self.language_analysis(df)
        
        print("生成词云...")
        try:
            self.generate_wordcloud(df)
        except Exception as e:
            print(f"词云生成失败: {e}")
        
        print("进行情感分析...")
        self.sentiment_analysis(df)
        
        print("生成综合报告...")
        report = self.generate_comprehensive_report(df)
        
        # 保存报告
        with open(f'{self.output_dir}/comprehensive_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存统计数据
        with open(f'{self.output_dir}/statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"分析完成！结果保存在 {self.output_dir} 目录")
        print("\n" + "="*50)
        print("分析摘要:")
        print(f"总数据量: {stats['total_complaints']} 条")
        print(f"平均情感分数: {stats['sentiment_stats']['mean']:.3f}")
        print("="*50)
        
        return report

def main():
    analyzer = DataAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()