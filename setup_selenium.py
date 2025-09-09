#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流程优化商机发现工具 - 安装和设置脚本 (Selenium版本)
支持Mac和Windows系统自动配置
"""

import os
import sys
import subprocess
import platform
import requests
import zipfile
import json
from pathlib import Path

def detect_system():
    """检测操作系统"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"检测到系统: {system} ({arch})")
    
    if system == 'darwin':
        return 'mac'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    else:
        print(f"⚠️  不支持的系统: {system}")
        return None

def install_python_requirements():
    """安装Python依赖包"""
    print("正在安装Python依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_selenium.txt"])
        print("✓ Python依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Python依赖包安装失败: {e}")
        return False

def check_chrome_installation():
    """检查Chrome浏览器是否已安装"""
    system = detect_system()
    
    if system == 'mac':
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        return os.path.exists(chrome_path)
    elif system == 'windows':
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        return any(os.path.exists(path) for path in chrome_paths)
    elif system == 'linux':
        try:
            subprocess.run(['which', 'google-chrome'], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    return False

def get_chrome_version():
    """获取Chrome版本"""
    system = detect_system()
    
    try:
        if system == 'mac':
            result = subprocess.run([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"
            ], capture_output=True, text=True)
        elif system == 'windows':
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    result = subprocess.run([path, "--version"], capture_output=True, text=True)
                    break
        elif system == 'linux':
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            return version
    except Exception as e:
        print(f"获取Chrome版本失败: {e}")
    
    return None

def download_chromedriver():
    """下载ChromeDriver"""
    system = detect_system()
    if not system:
        return False
    
    # 创建drivers目录
    drivers_dir = Path("drivers") / system
    drivers_dir.mkdir(parents=True, exist_ok=True)
    
    # 确定下载URL和文件名
    if system == 'mac':
        if platform.machine().lower() == 'arm64':  # Apple Silicon
            driver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_mac_arm64.zip"
        else:  # Intel Mac
            driver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_mac64.zip"
        driver_name = "chromedriver"
    elif system == 'windows':
        driver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip"
        driver_name = "chromedriver.exe"
    elif system == 'linux':
        driver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
        driver_name = "chromedriver"
    
    driver_path = drivers_dir / driver_name
    
    # 如果已存在，跳过下载
    if driver_path.exists():
        print(f"✓ ChromeDriver已存在: {driver_path}")
        return True
    
    try:
        print(f"正在下载 {system} 版本的ChromeDriver...")
        response = requests.get(driver_url, stream=True)
        response.raise_for_status()
        
        zip_path = drivers_dir / "chromedriver.zip"
        
        # 下载文件
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(drivers_dir)
        
        # 删除zip文件
        zip_path.unlink()
        
        # 给驱动文件执行权限 (Mac/Linux)
        if system in ['mac', 'linux']:
            os.chmod(driver_path, 0o755)
        
        print(f"✓ ChromeDriver下载完成: {driver_path}")
        return True
        
    except Exception as e:
        print(f"✗ ChromeDriver下载失败: {e}")
        return False

def create_config_file():
    """创建配置文件"""
    config = {
        "system": detect_system(),
        "chrome_driver_path": f"./drivers/{detect_system()}/chromedriver{'.exe' if detect_system() == 'windows' else ''}",
        "database_path": "process_opportunities.db",
        "output_directory": "process_optimization_output",
        "scraping_settings": {
            "headless": True,
            "max_tweets_per_search": 20,
            "scroll_pause_time": 2,
            "random_delay_range": [2, 5]
        },
        "search_terms": [
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
    }
    
    config_file = "process_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 配置文件创建完成: {config_file}")
    return True

def create_directories():
    """创建必要的目录"""
    directories = [
        'process_optimization_output',
        'process_demo_output',
        'logs',
        'drivers'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    return True

def test_selenium_setup():
    """测试Selenium设置"""
    try:
        print("正在测试Selenium设置...")
        
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 获取驱动路径
        system = detect_system()
        driver_name = "chromedriver.exe" if system == "windows" else "chromedriver"
        driver_path = f"./drivers/{system}/{driver_name}"
        
        # 创建服务和驱动
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 简单测试
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✓ Selenium设置测试成功 (访问页面标题: {title})")
        return True
        
    except Exception as e:
        print(f"✗ Selenium设置测试失败: {e}")
        return False

def main():
    """主安装函数"""
    print("🚀 流程优化商机发现工具 - 安装程序 (Selenium版本)")
    print("=" * 60)
    
    system = detect_system()
    if not system:
        return
    
    steps = [
        ("检查Chrome浏览器", check_chrome_installation),
        ("安装Python依赖包", install_python_requirements),
        ("下载ChromeDriver", download_chromedriver),
        ("创建配置文件", create_config_file),
        ("创建必要目录", create_directories),
        ("测试Selenium设置", test_selenium_setup)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n步骤: {step_name}")
        
        if step_name == "检查Chrome浏览器":
            if step_func():
                print("✓ Chrome浏览器已安装")
                chrome_version = get_chrome_version()
                if chrome_version:
                    print(f"  版本: {chrome_version}")
                success_count += 1
            else:
                print("✗ Chrome浏览器未安装")
                print("  请先安装Chrome浏览器:")
                print("  - Mac: https://www.google.com/chrome/")
                print("  - Windows: https://www.google.com/chrome/")
        else:
            if step_func():
                success_count += 1
    
    print("\n" + "=" * 60)
    print(f"安装完成: {success_count}/{len(steps)} 步骤成功")
    
    if success_count == len(steps):
        print("🎉 所有步骤完成！您可以开始使用工具了")
        print("\n下一步:")
        print("1. 运行演示: python3 process_demo.py")
        print("2. 运行真实抓取: python3 process_optimization_scraper.py")
        print("3. 查看配置: process_config.json")
    else:
        print("⚠️  部分步骤未完成，请检查上述错误信息")
    
    print("\n📋 使用说明:")
    print("- process_demo.py: 演示模式，使用模拟数据")
    print("- process_optimization_scraper.py: 真实抓取模式")
    print("- process_config.json: 配置文件")
    
    print("=" * 60)

if __name__ == "__main__":
    main()