#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium 反爬机制绕过基础类
支持多种反检测技术，包括 undetected-chromedriver、selenium-stealth 等
"""

import os
import sys
import time
import random
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

try:
    import undetected_chromedriver as uc
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium_stealth import stealth
    from fake_useragent import UserAgent
    SELENIUM_AVAILABLE = True
    
    # webdriver_manager可能在某些环境下有问题，设为可选
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
        print("警告: webdriver_manager 不可用，将使用 undetected-chromedriver 的自动管理功能")
        
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请运行: pip install undetected-chromedriver selenium-stealth fake-useragent selenium")
    SELENIUM_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StealthSeleniumBase:
    """
    Selenium 反爬机制绕过基础类
    集成多种反检测技术
    """
    
    def __init__(self, 
                 headless: bool = True,
                 use_undetected: bool = True,
                 use_stealth: bool = True,
                 use_proxy: Optional[str] = None,
                 window_size: tuple = (1920, 1080),
                 user_data_dir: Optional[str] = None):
        """
        初始化反爬Selenium驱动
        
        Args:
            headless: 是否使用无头模式
            use_undetected: 是否使用undetected-chromedriver
            use_stealth: 是否使用selenium-stealth
            use_proxy: 代理服务器地址 (格式: host:port 或 user:pass@host:port)
            window_size: 窗口大小
            user_data_dir: Chrome用户数据目录
        """
        self.headless = headless
        self.use_undetected = use_undetected
        self.use_stealth = use_stealth
        self.use_proxy = use_proxy
        self.window_size = window_size
        self.user_data_dir = user_data_dir
        self.driver = None
        self.ua = UserAgent()
        
        # 创建驱动
        self._create_driver()
    
    def _get_chrome_options(self) -> Options:
        """获取Chrome选项配置"""
        options = Options()
        
        # 基础反检测设置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 窗口大小
        options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')
        
        # 无头模式
        if self.headless:
            options.add_argument('--headless=new')  # 使用新的无头模式
        
        # 用户数据目录
        if self.user_data_dir:
            options.add_argument(f'--user-data-dir={self.user_data_dir}')
        
        # 代理设置
        if self.use_proxy:
            options.add_argument(f'--proxy-server={self.use_proxy}')
        
        # 随机User-Agent
        user_agent = self.ua.random
        options.add_argument(f'--user-agent={user_agent}')
        logger.info(f"使用User-Agent: {user_agent}")
        
        # 其他反检测选项
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-default-apps')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-gpu-logging')
        options.add_argument('--silent')
        
        # 禁用图像加载以提高速度（可选）
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # options.add_experimental_option("prefs", prefs)
        
        return options
    
    def _create_driver(self):
        """创建WebDriver实例"""
        try:
            if self.use_undetected:
                # 使用 undetected-chromedriver
                logger.info("使用 undetected-chromedriver 创建驱动")
                options = self._get_chrome_options()
                
                self.driver = uc.Chrome(
                    options=options,
                    version_main=None,  # 自动检测Chrome版本
                    driver_executable_path=None,  # 自动下载驱动
                    headless=self.headless
                )
            else:
                # 使用标准 Selenium
                logger.info("使用标准 Selenium 创建驱动")
                options = self._get_chrome_options()
                
                if WEBDRIVER_MANAGER_AVAILABLE:
                    # 自动管理ChromeDriver
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                else:
                    # 使用系统PATH中的ChromeDriver
                    self.driver = webdriver.Chrome(options=options)
            
            # 应用 selenium-stealth
            if self.use_stealth and not self.use_undetected:
                logger.info("应用 selenium-stealth 反检测")
                stealth(self.driver,
                       languages=["zh-CN", "zh", "en-US", "en"],
                       vendor="Google Inc.",
                       platform="Win32",
                       webgl_vendor="Intel Inc.",
                       renderer="Intel Iris OpenGL Engine",
                       fix_hairline=True)
            
            # 执行额外的反检测脚本
            self._execute_stealth_scripts()
            
            logger.info("WebDriver 创建成功")
            
        except Exception as e:
            logger.error(f"创建WebDriver失败: {e}")
            raise
    
    def _execute_stealth_scripts(self):
        """执行反检测JavaScript脚本"""
        if not self.driver:
            return
        
        try:
            # 隐藏 webdriver 属性
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # 修改 plugins 属性
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            # 修改 languages 属性
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en-US', 'en'],
                });
            """)
            
            # 覆盖 permissions 查询
            self.driver.execute_script("""
                const originalQuery = window.navigator.permissions.query;
                return window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            logger.info("反检测脚本执行完成")
            
        except Exception as e:
            logger.warning(f"执行反检测脚本时出错: {e}")
    
    def get_page(self, url: str, wait_time: int = 10) -> bool:
        """
        访问页面
        
        Args:
            url: 目标URL
            wait_time: 等待时间
            
        Returns:
            bool: 是否成功访问
        """
        try:
            logger.info(f"访问页面: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 模拟人类行为
            self.simulate_human_behavior()
            
            return True
            
        except Exception as e:
            logger.error(f"访问页面失败: {e}")
            return False
    
    def simulate_human_behavior(self):
        """模拟人类行为"""
        try:
            # 随机等待
            time.sleep(random.uniform(1, 3))
            
            # 随机滚动
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            if scroll_height > 0:
                random_scroll = random.randint(100, min(800, scroll_height // 2))
                self.driver.execute_script(f"window.scrollTo(0, {random_scroll});")
                time.sleep(random.uniform(0.5, 1.5))
            
            # 随机鼠标移动
            try:
                actions = ActionChains(self.driver)
                actions.move_by_offset(
                    random.randint(-100, 100), 
                    random.randint(-100, 100)
                ).perform()
            except:
                pass  # 忽略鼠标移动错误
            
            # 再次随机等待
            time.sleep(random.uniform(0.5, 2))
            
        except Exception as e:
            logger.warning(f"模拟人类行为时出错: {e}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """等待元素出现"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        """等待元素可点击"""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def safe_click(self, element):
        """安全点击元素（带重试）"""
        max_retries = 3
        for i in range(max_retries):
            try:
                # 滚动到元素可见
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # 点击元素
                element.click()
                return True
                
            except Exception as e:
                if i == max_retries - 1:
                    logger.error(f"点击元素失败: {e}")
                    return False
                time.sleep(1)
        
        return False
    
    def get_random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> float:
        """获取随机延迟时间"""
        return random.uniform(min_delay, max_delay)
    
    def change_user_agent(self):
        """更换User-Agent"""
        if self.driver:
            new_ua = self.ua.random
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": new_ua
            })
            logger.info(f"更换User-Agent: {new_ua}")
    
    def clear_cookies(self):
        """清除cookies"""
        if self.driver:
            self.driver.delete_all_cookies()
            logger.info("已清除所有cookies")
    
    def take_screenshot(self, filename: str = None) -> str:
        """截图"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        if self.driver:
            self.driver.save_screenshot(filename)
            logger.info(f"截图已保存: {filename}")
            return filename
        
        return None
    
    def get_page_source(self) -> str:
        """获取页面源码"""
        if self.driver:
            return self.driver.page_source
        return ""
    
    def execute_script(self, script: str, *args):
        """执行JavaScript脚本"""
        if self.driver:
            return self.driver.execute_script(script, *args)
        return None
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器时出错: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.quit()


def test_stealth_selenium():
    """测试反爬功能"""
    print("测试 Selenium 反爬功能...")
    
    # 测试基本功能
    with StealthSeleniumBase(headless=False, use_undetected=True) as scraper:
        # 访问检测网站
        test_urls = [
            "https://bot.sannysoft.com/",
            "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html",
            "https://arh.antoinevastel.com/bots/areyouheadless"
        ]
        
        for url in test_urls:
            print(f"\n测试网站: {url}")
            if scraper.get_page(url):
                time.sleep(5)  # 等待页面完全加载
                print("✓ 页面访问成功")
                
                # 截图
                screenshot = scraper.take_screenshot(f"test_{url.split('/')[-1]}.png")
                if screenshot:
                    print(f"✓ 截图保存: {screenshot}")
            else:
                print("✗ 页面访问失败")
    
    print("\n反爬功能测试完成！")


if __name__ == "__main__":
    test_stealth_selenium()