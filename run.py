#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X(Twitter) 用户吐槽抓取分析工具 - 快速启动脚本
"""

import os
import sys
import argparse
from datetime import datetime

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = ['pandas', 'sqlite3', 'matplotlib', 'seaborn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行: python setup.py 安装依赖")
        return False
    return True

def check_config():
    """检查配置文件"""
    if not os.path.exists('config.json'):
        print("⚠️  配置文件不存在")
        if os.path.exists('config.json.template'):
            print("请复制 config.json.template 为 config.json 并填入API凭证")
        return False
    return True

def run_demo():
    """运行演示模式"""
    print("🚀 启动演示模式...")
    try:
        from demo import main as demo_main
        demo_main()
    except Exception as e:
        print(f"❌ 演示模式运行失败: {e}")

def run_scraper(keywords=None, max_results=50):
    """运行数据抓取"""
    if not check_config():
        print("请先配置 config.json 文件")
        return
    
    print("🚀 启动数据抓取...")
    try:
        from x_scraper import XScraper
        
        scraper = XScraper()
        
        if keywords:
            all_complaints = []
            for keyword in keywords:
                print(f"搜索关键词: {keyword}")
                complaints = scraper.search_complaints(keyword, max_results=max_results)
                all_complaints.extend(complaints)
            
            if all_complaints:
                scraper.save_complaints(all_complaints)
                scraper.export_to_files()
                print(f"✓ 成功抓取 {len(all_complaints)} 条数据")
            else:
                print("⚠️  未找到相关数据")
        else:
            # 使用默认关键词
            from x_scraper import main as scraper_main
            scraper_main()
            
    except Exception as e:
        print(f"❌ 数据抓取失败: {e}")

def run_analyzer():
    """运行数据分析"""
    print("🚀 启动数据分析...")
    try:
        from data_analyzer import DataAnalyzer
        
        analyzer = DataAnalyzer()
        report = analyzer.run_complete_analysis()
        print("✓ 分析完成")
        
    except Exception as e:
        print(f"❌ 数据分析失败: {e}")

def show_status():
    """显示系统状态"""
    print("📊 系统状态检查")
    print("="*40)
    
    # 检查文件
    files_to_check = [
        ('config.json', '配置文件'),
        ('x_complaints.db', '数据库文件'),
        ('output/', '输出目录'),
        ('analysis_output/', '分析输出目录')
    ]
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"✓ {description}: {file_path} ({size} bytes)")
            else:
                file_count = len(os.listdir(file_path)) if os.path.isdir(file_path) else 0
                print(f"✓ {description}: {file_path} ({file_count} files)")
        else:
            print(f"❌ {description}: {file_path} (不存在)")
    
    # 检查数据库内容
    if os.path.exists('x_complaints.db'):
        try:
            import sqlite3
            conn = sqlite3.connect('x_complaints.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM complaints')
            count = cursor.fetchone()[0]
            conn.close()
            print(f"📄 数据库记录数: {count}")
        except Exception as e:
            print(f"❌ 数据库检查失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='X(Twitter) 用户吐槽抓取分析工具')
    parser.add_argument('action', choices=['demo', 'scrape', 'analyze', 'status', 'setup'], 
                       help='要执行的操作')
    parser.add_argument('--keywords', '-k', nargs='+', 
                       help='抓取时使用的关键词列表')
    parser.add_argument('--max-results', '-m', type=int, default=50,
                       help='每个关键词的最大抓取数量')
    
    args = parser.parse_args()
    
    print(f"🔧 X(Twitter) 用户吐槽抓取分析工具")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    if args.action == 'setup':
        print("🔧 运行安装程序...")
        try:
            from setup import main as setup_main
            setup_main()
        except Exception as e:
            print(f"❌ 安装失败: {e}")
    
    elif args.action == 'demo':
        run_demo()
    
    elif args.action == 'scrape':
        if not check_dependencies():
            return
        run_scraper(args.keywords, args.max_results)
    
    elif args.action == 'analyze':
        if not check_dependencies():
            return
        run_analyzer()
    
    elif args.action == 'status':
        show_status()

def print_help():
    """打印帮助信息"""
    help_text = """
🔧 X(Twitter) 用户吐槽抓取分析工具 - 使用指南

📋 基本命令:
  python run.py setup                    # 安装和配置
  python run.py demo                     # 运行演示模式
  python run.py scrape                   # 抓取数据
  python run.py analyze                  # 分析数据
  python run.py status                   # 查看状态

🎯 高级用法:
  python run.py scrape -k 微信 支付宝     # 指定关键词抓取
  python run.py scrape -m 100           # 指定最大抓取数量

📁 文件说明:
  config.json          # 配置文件（需要填入API凭证）
  x_complaints.db      # 数据库文件
  output/             # 导出数据目录
  analysis_output/    # 分析结果目录

🚀 快速开始:
  1. python run.py setup      # 首次安装
  2. 编辑 config.json 文件    # 填入Twitter API凭证
  3. python run.py demo       # 体验功能（无需API）
  4. python run.py scrape     # 开始抓取真实数据
  5. python run.py analyze    # 分析数据

💡 提示:
  - 首次使用建议先运行 demo 模式体验功能
  - 需要Twitter Developer账号才能抓取真实数据
  - 分析功能可以在有数据的情况下独立运行
"""
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()
    else:
        main()