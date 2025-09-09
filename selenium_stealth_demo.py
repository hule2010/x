#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium 反爬机制演示脚本
展示如何使用反爬功能绕过网站检测
"""

import sys
import time
import random
from selenium_stealth_base import StealthSeleniumBase

def test_detection_websites():
    """测试反爬功能的效果"""
    print("🔍 Selenium 反爬机制演示")
    print("=" * 50)
    
    # 测试网站列表
    test_sites = [
        {
            'name': 'Bot Detection Test',
            'url': 'https://bot.sannysoft.com/',
            'description': '全面的机器人检测测试'
        },
        {
            'name': 'Headless Chrome Test', 
            'url': 'https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html',
            'description': '无头浏览器检测测试'
        },
        {
            'name': 'Are You Headless?',
            'url': 'https://arh.antoinevastel.com/bots/areyouheadless',
            'description': '检测是否为无头浏览器'
        }
    ]
    
    print("将测试以下检测网站:")
    for i, site in enumerate(test_sites, 1):
        print(f"{i}. {site['name']} - {site['description']}")
    print()
    
    # 测试不同配置
    configurations = [
        {
            'name': '标准Selenium（容易被检测）',
            'use_undetected': False,
            'use_stealth': False,
            'headless': True
        },
        {
            'name': 'undetected-chromedriver',
            'use_undetected': True,
            'use_stealth': False,
            'headless': True
        },
        {
            'name': 'undetected + selenium-stealth',
            'use_undetected': True,
            'use_stealth': True,
            'headless': True
        }
    ]
    
    for config in configurations:
        print(f"\n🧪 测试配置: {config['name']}")
        print("-" * 40)
        
        try:
            with StealthSeleniumBase(
                headless=config['headless'],
                use_undetected=config['use_undetected'],
                use_stealth=config['use_stealth']
            ) as scraper:
                
                for site in test_sites:
                    print(f"访问: {site['name']}")
                    
                    if scraper.get_page(site['url'], wait_time=10):
                        # 等待页面完全加载
                        time.sleep(3)
                        
                        # 截图保存结果
                        screenshot_name = f"test_{config['name'].replace(' ', '_')}_{site['name'].replace(' ', '_')}.png"
                        scraper.take_screenshot(screenshot_name)
                        
                        print(f"  ✓ 成功访问，截图保存: {screenshot_name}")
                        
                        # 检查页面内容中的检测结果
                        page_source = scraper.get_page_source()
                        if 'bot' in page_source.lower() or 'automation' in page_source.lower():
                            print(f"  ⚠️  可能被检测为机器人")
                        else:
                            print(f"  ✅ 未被检测为机器人")
                    else:
                        print(f"  ✗ 访问失败")
                    
                    # 随机延迟
                    delay = random.uniform(2, 5)
                    print(f"  等待 {delay:.1f} 秒...")
                    time.sleep(delay)
                
        except Exception as e:
            print(f"  ✗ 配置测试失败: {e}")
            continue
    
    print("\n🎯 测试完成！")
    print("请查看生成的截图文件来对比不同配置的效果")

def demo_twitter_scraping():
    """演示Twitter抓取"""
    print("\n🐦 Twitter 抓取演示")
    print("=" * 30)
    
    try:
        with StealthSeleniumBase(
            headless=False,  # 显示浏览器以便观察
            use_undetected=True,
            use_stealth=True
        ) as scraper:
            
            # 访问Twitter搜索页面
            search_query = "Python编程问题"
            search_url = f"https://twitter.com/search?q={search_query}&src=typed_query"
            
            print(f"搜索: {search_query}")
            
            if scraper.get_page(search_url):
                print("✓ 成功访问Twitter搜索页面")
                
                # 滚动加载更多内容
                print("正在滚动加载更多推文...")
                for i in range(3):
                    scraper.simulate_human_behavior()
                    time.sleep(2)
                
                # 截图
                scraper.take_screenshot("twitter_search_demo.png")
                print("✓ 截图已保存: twitter_search_demo.png")
                
                # 保持页面打开一会儿以便观察
                print("页面将保持打开10秒以便观察...")
                time.sleep(10)
                
            else:
                print("✗ 访问Twitter失败")
                
    except Exception as e:
        print(f"Twitter抓取演示失败: {e}")

def demo_advanced_features():
    """演示高级反爬功能"""
    print("\n⚙️  高级反爬功能演示")
    print("=" * 30)
    
    try:
        with StealthSeleniumBase(
            headless=True,
            use_undetected=True,
            use_stealth=True,
            window_size=(1366, 768)  # 不同的窗口大小
        ) as scraper:
            
            # 测试User-Agent切换
            print("1. 测试User-Agent切换")
            scraper.get_page("https://httpbin.org/user-agent")
            time.sleep(2)
            
            original_ua = scraper.get_page_source()
            print(f"  原始UA: {original_ua.split('user-agent')[1][:50] if 'user-agent' in original_ua else 'N/A'}")
            
            # 更换User-Agent
            scraper.change_user_agent()
            scraper.get_page("https://httpbin.org/user-agent")
            time.sleep(2)
            
            new_ua = scraper.get_page_source()
            print(f"  新UA: {new_ua.split('user-agent')[1][:50] if 'user-agent' in new_ua else 'N/A'}")
            
            # 测试Cookie清除
            print("\n2. 测试Cookie管理")
            scraper.get_page("https://httpbin.org/cookies/set/test/value123")
            time.sleep(1)
            scraper.get_page("https://httpbin.org/cookies")
            
            cookies_before = scraper.get_page_source()
            print(f"  清除前: {'test' in cookies_before}")
            
            scraper.clear_cookies()
            scraper.get_page("https://httpbin.org/cookies")
            
            cookies_after = scraper.get_page_source()
            print(f"  清除后: {'test' in cookies_after}")
            
            # 测试JavaScript执行
            print("\n3. 测试JavaScript执行")
            scraper.get_page("https://httpbin.org/html")
            
            # 执行自定义JavaScript
            result = scraper.execute_script("return document.title;")
            print(f"  页面标题: {result}")
            
            # 修改页面元素
            scraper.execute_script("document.body.style.backgroundColor = 'lightblue';")
            scraper.take_screenshot("modified_page.png")
            print("  ✓ 页面背景已修改并截图")
            
        print("\n✅ 高级功能演示完成")
        
    except Exception as e:
        print(f"高级功能演示失败: {e}")

def main():
    """主函数"""
    print("🚀 Selenium 反爬机制完整演示")
    print("=" * 60)
    
    try:
        # 检测网站测试
        test_detection_websites()
        
        # Twitter抓取演示
        demo_twitter_scraping()
        
        # 高级功能演示
        demo_advanced_features()
        
        print("\n🎉 所有演示完成！")
        print("\n📋 生成的文件:")
        print("- 各种测试截图 (test_*.png)")
        print("- twitter_search_demo.png")
        print("- modified_page.png")
        
        print("\n💡 使用建议:")
        print("1. 对比不同配置的截图效果")
        print("2. 根据目标网站选择合适的反爬配置")
        print("3. 适当调整延迟和行为模拟参数")
        print("4. 考虑使用代理IP进一步提高隐蔽性")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程出错: {e}")

if __name__ == "__main__":
    main()