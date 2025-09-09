#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装和设置脚本
自动安装依赖和配置环境
"""

import os
import subprocess
import sys
import json

def install_requirements():
    """安装Python依赖包"""
    print("正在安装Python依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Python依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Python依赖包安装失败: {e}")
        return False

def download_nltk_data():
    """下载NLTK数据"""
    print("正在下载NLTK数据...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("✓ NLTK数据下载成功")
        return True
    except Exception as e:
        print(f"✗ NLTK数据下载失败: {e}")
        return False

def create_config_file():
    """创建配置文件"""
    config_file = "config.json"
    if os.path.exists(config_file):
        print(f"✓ 配置文件 {config_file} 已存在")
        return True
    
    template_file = "config.json.template"
    if os.path.exists(template_file):
        print(f"正在从模板创建配置文件...")
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 配置文件 {config_file} 创建成功")
            print(f"⚠️  请编辑 {config_file} 文件，填入您的Twitter API凭证")
            return True
        except Exception as e:
            print(f"✗ 配置文件创建失败: {e}")
            return False
    else:
        print(f"✗ 模板文件 {template_file} 不存在")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ['output', 'analysis_output', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}")
        else:
            print(f"✓ 目录已存在: {directory}")
    return True

def check_twitter_credentials():
    """检查Twitter API凭证"""
    config_file = "config.json"
    if not os.path.exists(config_file):
        print("⚠️  配置文件不存在，请先运行配置")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_keys = ['bearer_token', 'consumer_key', 'consumer_secret', 
                        'access_token', 'access_token_secret']
        
        missing_keys = []
        for key in required_keys:
            if not config.get(key) or config[key].startswith('YOUR_'):
                missing_keys.append(key)
        
        if missing_keys:
            print("⚠️  以下Twitter API凭证尚未配置:")
            for key in missing_keys:
                print(f"   - {key}")
            print(f"   请编辑 {config_file} 文件添加正确的凭证")
            return False
        else:
            print("✓ Twitter API凭证配置完整")
            return True
            
    except Exception as e:
        print(f"✗ 检查配置文件失败: {e}")
        return False

def main():
    """主安装函数"""
    print("=" * 60)
    print("X(Twitter) 用户吐槽抓取分析工具 - 安装程序")
    print("=" * 60)
    
    steps = [
        ("安装Python依赖包", install_requirements),
        ("下载NLTK数据", download_nltk_data),
        ("创建配置文件", create_config_file),
        ("创建必要目录", create_directories),
        ("检查Twitter API凭证", check_twitter_credentials)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n步骤: {step_name}")
        if step_func():
            success_count += 1
        else:
            print(f"步骤失败: {step_name}")
    
    print("\n" + "=" * 60)
    print(f"安装完成: {success_count}/{len(steps)} 步骤成功")
    
    if success_count == len(steps):
        print("🎉 所有步骤完成！您可以开始使用工具了")
        print("\n下一步:")
        print("1. 运行数据抓取: python x_scraper.py")
        print("2. 运行数据分析: python data_analyzer.py")
    else:
        print("⚠️  部分步骤未完成，请检查上述错误信息")
        if success_count >= 3:
            print("基本功能应该可以使用，但建议解决所有问题")
    
    print("=" * 60)

if __name__ == "__main__":
    main()