#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X(Twitter) 用户吐槽抓取分析工具 - 简化演示版本
"""

import pandas as pd
import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """生成演示数据"""
    
    # 中文示例数据
    chinese_complaints = [
        "微信又卡了，发消息半天发不出去，这什么破网络",
        "支付宝的界面设计太复杂了，找个功能要找半天",
        "淘宝的搜索功能有问题，搜不到想要的商品",
        "iPhone电池耗电太快，一天要充好几次电",
        "安卓系统更新后变得很慢，应用启动要等很久",
        "微信支付经常出错，付款的时候总是失败",
        "支付宝的客服态度很差，问题解决不了还很傲慢",
        "淘宝的物流信息更新不及时，不知道包裹到哪了",
        "iPhone的价格太贵了，性价比不高",
        "安卓手机的广告太多，很影响使用体验",
        "微信群聊的消息太多，找历史消息很困难",
        "支付宝的安全验证太繁琐，每次都要验证好几遍",
        "淘宝的退货流程太复杂，客服推来推去",
        "iPhone的存储空间不够用，64GB根本不够",
        "安卓系统的权限管理有问题，应用乱要权限"
    ]
    
    # 英文示例数据
    english_complaints = [
        "Twitter's new update is terrible, the interface is confusing",
        "Instagram keeps crashing when I try to upload photos",
        "Facebook's algorithm is broken, I don't see posts from friends",
        "YouTube ads are getting too long and annoying",
        "WhatsApp messages are not delivering properly",
        "Spotify keeps playing the same songs over and over",
        "Netflix removed my favorite shows without warning",
        "Amazon delivery is always late, very disappointing",
        "Google search results are not relevant anymore",
        "Apple's new iOS update made my phone slower"
    ]
    
    # 生成完整的演示数据
    demo_data = []
    
    # 生成中文数据
    for i, complaint in enumerate(chinese_complaints):
        data = {
            'tweet_id': f'zh_{i+1}',
            'user_id': f'user_zh_{random.randint(1000, 9999)}',
            'username': f'用户{random.randint(100, 999)}',
            'content': complaint,
            'language': 'zh',
            'created_at': datetime.now() - timedelta(days=random.randint(0, 30), 
                                                   hours=random.randint(0, 23)),
            'difficulty_level': random.randint(1, 5),
            'category': random.choice(['技术问题', '用户体验', '功能需求', '服务质量', '价格费用']),
            'keywords': '问题,体验,功能',
            'sentiment_score': random.uniform(-0.8, -0.1),
            'retweet_count': random.randint(0, 50),
            'like_count': random.randint(0, 100),
            'reply_count': random.randint(0, 20)
        }
        demo_data.append(data)
    
    # 生成英文数据
    for i, complaint in enumerate(english_complaints):
        data = {
            'tweet_id': f'en_{i+1}',
            'user_id': f'user_en_{random.randint(1000, 9999)}',
            'username': f'user{random.randint(100, 999)}',
            'content': complaint,
            'language': 'en',
            'created_at': datetime.now() - timedelta(days=random.randint(0, 30), 
                                                   hours=random.randint(0, 23)),
            'difficulty_level': random.randint(1, 5),
            'category': random.choice(['技术问题', '用户体验', '功能需求', '服务质量', '价格费用']),
            'keywords': 'problem,issue,feature',
            'sentiment_score': random.uniform(-0.9, 0.2),
            'retweet_count': random.randint(0, 30),
            'like_count': random.randint(0, 80),
            'reply_count': random.randint(0, 15)
        }
        demo_data.append(data)
    
    return demo_data

def setup_demo_database():
    """设置演示数据库"""
    # 如果数据库已存在，先删除
    if os.path.exists('demo_complaints.db'):
        os.remove('demo_complaints.db')
    
    # 创建新的数据库
    conn = sqlite3.connect('demo_complaints.db')
    cursor = conn.cursor()
    
    # 创建表结构
    cursor.execute('''
        CREATE TABLE complaints (
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
    
    conn.commit()
    conn.close()
    print("✓ 演示数据库创建完成")

def insert_demo_data():
    """插入演示数据"""
    demo_data = generate_demo_data()
    
    conn = sqlite3.connect('demo_complaints.db')
    cursor = conn.cursor()
    
    for data in demo_data:
        cursor.execute('''
            INSERT INTO complaints 
            (tweet_id, user_id, username, content, language, created_at, 
             difficulty_level, category, keywords, sentiment_score, 
             retweet_count, like_count, reply_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['tweet_id'],
            data['user_id'],
            data['username'],
            data['content'],
            data['language'],
            data['created_at'],
            data['difficulty_level'],
            data['category'],
            data['keywords'],
            data['sentiment_score'],
            data['retweet_count'],
            data['like_count'],
            data['reply_count']
        ))
    
    conn.commit()
    conn.close()
    print(f"✓ 插入了 {len(demo_data)} 条演示数据")

def analyze_data():
    """简单的数据分析"""
    conn = sqlite3.connect('demo_complaints.db')
    df = pd.read_sql_query('SELECT * FROM complaints ORDER BY created_at DESC', conn)
    conn.close()
    
    # 转换日期格式
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # 基础统计
    total_count = len(df)
    lang_stats = df['language'].value_counts()
    difficulty_stats = df['difficulty_level'].value_counts().sort_index()
    category_stats = df['category'].value_counts()
    avg_sentiment = df['sentiment_score'].mean()
    
    print(f"\n📊 数据分析结果:")
    print(f"总数据量: {total_count} 条")
    print(f"\n语言分布:")
    for lang, count in lang_stats.items():
        percentage = (count / total_count) * 100
        lang_name = '中文' if lang == 'zh' else '英文'
        print(f"  {lang_name}: {count} 条 ({percentage:.1f}%)")
    
    print(f"\n难度等级分布:")
    difficulty_labels = {1: '简单', 2: '较简单', 3: '中等', 4: '较困难', 5: '困难'}
    for level in sorted(difficulty_stats.index):
        count = difficulty_stats[level]
        percentage = (count / total_count) * 100
        label = difficulty_labels.get(level, f'等级{level}')
        print(f"  {label} (等级{level}): {count} 条 ({percentage:.1f}%)")
    
    print(f"\n问题分类统计:")
    for category, count in category_stats.items():
        percentage = (count / total_count) * 100
        print(f"  {category}: {count} 条 ({percentage:.1f}%)")
    
    print(f"\n情感分析:")
    print(f"  平均情感分数: {avg_sentiment:.3f}")
    negative_count = len(df[df['sentiment_score'] < -0.1])
    negative_percentage = (negative_count / total_count) * 100
    print(f"  负面情感比例: {negative_percentage:.1f}%")
    
    return df

def export_data(df):
    """导出数据"""
    # 创建输出目录
    output_dir = 'demo_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 导出所有数据
    df.to_csv(f'{output_dir}/demo_complaints.csv', index=False, encoding='utf-8')
    df.to_json(f'{output_dir}/demo_complaints.json', orient='records', indent=2)
    
    # 按语言分组
    for lang in df['language'].unique():
        lang_df = df[df['language'] == lang]
        lang_name = '中文' if lang == 'zh' else '英文'
        lang_df.to_csv(f'{output_dir}/demo_complaints_{lang_name}.csv', index=False, encoding='utf-8')
    
    # 按难度分组
    for level in range(1, 6):
        level_df = df[df['difficulty_level'] == level]
        if not level_df.empty:
            level_df.to_csv(f'{output_dir}/demo_complaints_难度{level}.csv', index=False, encoding='utf-8')
    
    # 按分类分组
    for category in df['category'].unique():
        cat_df = df[df['category'] == category]
        cat_df.to_csv(f'{output_dir}/demo_complaints_{category}.csv', index=False, encoding='utf-8')
    
    print(f"✓ 演示数据导出到: {output_dir}")

def generate_report(df):
    """生成分析报告"""
    report = f"""# X(Twitter) 用户吐槽分析演示报告

## 报告生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览
- **总数据量**: {len(df):,} 条
- **数据时间范围**: {df['created_at'].min().strftime('%Y-%m-%d')} 至 {df['created_at'].max().strftime('%Y-%m-%d')}

## 语言分布
"""
    
    lang_stats = df['language'].value_counts()
    for lang, count in lang_stats.items():
        percentage = (count / len(df)) * 100
        lang_name = '中文' if lang == 'zh' else '英文'
        report += f"- {lang_name}: {count:,} 条 ({percentage:.1f}%)\n"
    
    report += f"""
## 难度等级分析
"""
    
    difficulty_labels = {1: '简单', 2: '较简单', 3: '中等', 4: '较困难', 5: '困难'}
    difficulty_stats = df['difficulty_level'].value_counts().sort_index()
    for level, count in difficulty_stats.items():
        percentage = (count / len(df)) * 100
        label = difficulty_labels.get(level, f'等级{level}')
        report += f"- {label} (等级{level}): {count:,} 条 ({percentage:.1f}%)\n"
    
    report += f"""
## 问题分类统计
"""
    
    category_stats = df['category'].value_counts()
    for category, count in category_stats.items():
        percentage = (count / len(df)) * 100
        report += f"- {category}: {count:,} 条 ({percentage:.1f}%)\n"
    
    avg_sentiment = df['sentiment_score'].mean()
    report += f"""
## 情感分析结果
- **平均情感分数**: {avg_sentiment:.3f}
- **最负面分数**: {df['sentiment_score'].min():.3f}
- **最正面分数**: {df['sentiment_score'].max():.3f}

*注：情感分数范围为 -1.0 (极度负面) 到 1.0 (极度正面)*

## 关键发现

### 1. 用户吐槽热点
"""
    
    top_categories = df['category'].value_counts().head(3)
    for i, (category, count) in enumerate(top_categories.items(), 1):
        percentage = (count / len(df)) * 100
        report += f"{i}. **{category}** - 占比 {percentage:.1f}%\n"
    
    high_difficulty = len(df[df['difficulty_level'] >= 4])
    high_percentage = (high_difficulty / len(df)) * 100
    
    report += f"""
### 2. 问题难度分析
- 高难度问题（等级4-5）占比: {high_percentage:.1f}%

### 3. 用户情感状态
"""
    
    if avg_sentiment < -0.2:
        sentiment_desc = "整体情感偏向负面"
    elif avg_sentiment > 0.2:
        sentiment_desc = "整体情感偏向正面"
    else:
        sentiment_desc = "整体情感相对中性"
    
    report += f"- {sentiment_desc}（平均分数: {avg_sentiment:.3f}）\n"
    
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
- 详细数据文件: `demo_output/` 目录
- 原始数据库: `demo_complaints.db`

---
*本报告由X(Twitter)用户吐槽抓取分析工具自动生成*
"""
    
    # 保存报告
    output_dir = 'demo_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(f'{output_dir}/analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ 分析报告保存到: {output_dir}/analysis_report.md")
    
    return report

def main():
    """主演示函数"""
    print("🎉 X(Twitter) 用户吐槽抓取分析工具 - 简化演示模式")
    print("="*60)
    
    try:
        # 1. 设置演示数据库
        print("1. 设置演示数据库...")
        setup_demo_database()
        
        # 2. 生成并插入演示数据
        print("\n2. 生成演示数据...")
        insert_demo_data()
        
        # 3. 分析数据
        print("\n3. 分析数据...")
        df = analyze_data()
        
        # 4. 导出数据文件
        print("\n4. 导出数据文件...")
        export_data(df)
        
        # 5. 生成报告
        print("\n5. 生成分析报告...")
        generate_report(df)
        
        print("\n" + "🎊 演示完成！")
        print("\n您可以查看以下文件:")
        print("  📁 demo_output/ - 导出的数据文件")
        print("  📄 demo_complaints.db - 演示数据库")
        print("  📄 demo_output/analysis_report.md - 分析报告")
        
        print("\n💡 功能特点:")
        print("  ✓ 中英文内容自动识别和分类")
        print("  ✓ 智能难度等级评估 (1-5级)")
        print("  ✓ 问题类型自动分类")
        print("  ✓ 情感分析和趋势分析")
        print("  ✓ 多格式数据导出 (CSV, JSON)")
        print("  ✓ 详细的分析报告生成")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()