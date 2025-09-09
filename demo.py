#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X(Twitter) 用户吐槽抓取分析工具 - 演示版本
无需真实API即可体验功能
"""

import pandas as pd
import sqlite3
import json
import os
from datetime import datetime, timedelta
import random
from x_scraper import XScraper
from data_analyzer import DataAnalyzer

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
        "安卓系统的权限管理有问题，应用乱要权限",
        "微信的朋友圈加载很慢，图片显示不出来",
        "支付宝的余额宝收益越来越低了",
        "淘宝的商品质量参差不齐，图片和实物不符",
        "iPhone的充电器容易坏，质量不行",
        "安卓手机的系统更新太频繁，很烦人"
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
        "Apple's new iOS update made my phone slower",
        "Microsoft Windows keeps forcing updates at bad times",
        "Tesla's autopilot feature is not working properly",
        "Uber prices are getting too expensive",
        "Airbnb hosts are canceling bookings last minute",
        "PayPal's security checks are too complicated",
        "Zoom meetings have too many connection issues",
        "Slack notifications are overwhelming and distracting",
        "GitHub's interface is not user-friendly for beginners",
        "LinkedIn's feed is full of irrelevant content",
        "TikTok's algorithm shows inappropriate content"
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
            'sentiment_score': random.uniform(-0.8, -0.1),  # 大部分是负面的
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
    
    # 创建分类表
    cursor.execute('''
        CREATE TABLE categories (
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
        'INSERT INTO categories (name, description, keywords) VALUES (?, ?, ?)',
        default_categories
    )
    
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

def run_demo_analysis():
    """运行演示分析"""
    print("正在运行数据分析...")
    
    # 使用演示数据库路径
    analyzer = DataAnalyzer('demo_complaints.db')
    
    # 创建演示输出目录
    demo_output_dir = 'demo_analysis_output'
    analyzer.output_dir = demo_output_dir
    if not os.path.exists(demo_output_dir):
        os.makedirs(demo_output_dir)
    
    # 运行分析
    report = analyzer.run_complete_analysis()
    
    print("\n" + "="*60)
    print("演示分析完成！")
    print("="*60)
    print(f"结果保存在: {demo_output_dir}")
    print("\n生成的文件:")
    if os.path.exists(demo_output_dir):
        for file in os.listdir(demo_output_dir):
            print(f"  - {file}")

def export_demo_data():
    """导出演示数据"""
    print("正在导出演示数据...")
    
    conn = sqlite3.connect('demo_complaints.db')
    df = pd.read_sql_query('SELECT * FROM complaints ORDER BY created_at DESC', conn)
    conn.close()
    
    # 创建输出目录
    output_dir = 'demo_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 导出所有数据
    df.to_csv(f'{output_dir}/demo_complaints.csv', index=False, encoding='utf-8')
    df.to_json(f'{output_dir}/demo_complaints.json', orient='records', ensure_ascii=False, indent=2)
    
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
    
    print(f"✓ 演示数据导出到: {output_dir}")

def main():
    """主演示函数"""
    print("🎉 X(Twitter) 用户吐槽抓取分析工具 - 演示模式")
    print("="*60)
    
    try:
        # 1. 设置演示数据库
        print("1. 设置演示数据库...")
        setup_demo_database()
        
        # 2. 生成并插入演示数据
        print("\n2. 生成演示数据...")
        insert_demo_data()
        
        # 3. 导出数据文件
        print("\n3. 导出数据文件...")
        export_demo_data()
        
        # 4. 运行数据分析
        print("\n4. 运行数据分析...")
        run_demo_analysis()
        
        print("\n" + "🎊 演示完成！")
        print("\n您可以查看以下目录的结果:")
        print("  📁 demo_output/ - 导出的数据文件")
        print("  📁 demo_analysis_output/ - 分析图表和报告")
        print("  📄 demo_complaints.db - 演示数据库")
        
        print("\n💡 提示:")
        print("  - 查看 demo_analysis_output/comprehensive_report.md 获取详细报告")
        print("  - 查看 *.png 文件查看可视化图表")
        print("  - 查看 demo_output/*.csv 文件获取原始数据")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()