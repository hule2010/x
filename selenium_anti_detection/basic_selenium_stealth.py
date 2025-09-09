#!/usr/bin/env python3
"""
基础 Selenium 反检测配置示例
演示如何配置 Selenium 以绕过常见的反爬虫检测
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


def create_stealth_driver():
    """创建一个配置了反检测功能的 Chrome 浏览器驱动"""
    
    # 创建 Chrome 选项
    chrome_options = Options()
    
    # 1. 禁用自动化控制特征
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 2. 禁用自动化扩展
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 3. 设置真实的 User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # 4. 设置窗口大小（避免无头模式被检测）
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    # 5. 禁用 WebRTC 防止真实 IP 泄露
    chrome_options.add_argument("--disable-webrtc")
    
    # 6. 禁用 GPU 加速（某些情况下可以避免检测）
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 7. 设置语言和时区
    chrome_options.add_argument("--lang=zh-CN")
    
    # 8. 忽略证书错误
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # 9. 禁用图片加载（可选，提高速度）
    # chrome_prefs = {"profile.default_content_setting_values.images": 2}
    # chrome_options.add_experimental_option("prefs", chrome_prefs)
    
    # 创建驱动
    driver = webdriver.Chrome(options=chrome_options)
    
    # 10. 执行 JavaScript 来隐藏 webdriver 特征
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // 重写 navigator.webdriver 属性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 重写 navigator.plugins 以显示真实的插件列表
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin}, 
                     description: "Portable Document Format", 
                     filename: "internal-pdf-viewer", 
                     length: 1, 
                     name: "Chrome PDF Plugin"},
                    {0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin}, 
                     description: "", 
                     filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", 
                     length: 1, 
                     name: "Chrome PDF Viewer"}
                ]
            });
            
            // 重写 navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
            
            // 重写权限查询
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );
        """
    })
    
    return driver


def human_like_behavior(driver, element=None):
    """模拟人类行为"""
    # 随机延迟
    time.sleep(random.uniform(0.5, 2.0))
    
    # 随机滚动
    scroll_distance = random.randint(100, 500)
    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    time.sleep(random.uniform(0.3, 1.0))
    
    # 如果有元素，缓慢移动到元素
    if element:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(random.uniform(0.5, 1.0))


def test_anti_detection(url="https://bot.sannysoft.com/"):
    """
    测试反检测配置是否有效
    使用 bot.sannysoft.com 来检测浏览器特征
    """
    driver = None
    try:
        print("正在创建反检测浏览器驱动...")
        driver = create_stealth_driver()
        
        print(f"访问测试网站: {url}")
        driver.get(url)
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 模拟人类行为
        human_like_behavior(driver)
        
        # 检查 webdriver 检测结果
        webdriver_result = driver.execute_script("return navigator.webdriver")
        print(f"navigator.webdriver 检测结果: {webdriver_result}")
        
        # 获取页面标题
        print(f"页面标题: {driver.title}")
        
        # 等待用户查看结果
        input("按 Enter 键继续...")
        
        # 访问其他网站测试
        print("\n测试访问其他网站...")
        driver.get("https://www.google.com")
        human_like_behavior(driver)
        
        # 搜索测试
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # 模拟人类输入
        search_term = "Selenium automation"
        for char in search_term:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        print("测试完成！")
        input("按 Enter 键关闭浏览器...")
        
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if driver:
            driver.quit()


def main():
    """主函数"""
    print("=== Selenium 反检测示例 ===")
    print("这个示例展示了如何配置 Selenium 以绕过常见的反爬虫检测\n")
    
    test_anti_detection()


if __name__ == "__main__":
    main()