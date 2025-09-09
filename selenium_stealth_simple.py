#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 Selenium 反爬机制绕过基础类
避免依赖问题，提供核心反检测功能
"""

import os
import sys
import time
import random
import logging
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 检查Selenium是否可用
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
    logger.info("✅ Selenium 核心模块可用")
except ImportError as e:
    SELENIUM_AVAILABLE = False
    logger.error(f"❌ Selenium 不可用: {e}")

# 检查反爬扩展
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
    logger.info("✅ undetected-chromedriver 可用")
except ImportError:
    UC_AVAILABLE = False
    logger.warning("⚠️  undetected-chromedriver 不可用")

try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
    logger.info("✅ selenium-stealth 可用")
except ImportError:
    STEALTH_AVAILABLE = False
    logger.warning("⚠️  selenium-stealth 不可用")

try:
    from fake_useragent import UserAgent
    UA_AVAILABLE = True
    logger.info("✅ fake-useragent 可用")
except ImportError:
    UA_AVAILABLE = False
    logger.warning("⚠️  fake-useragent 不可用")


class SimpleStealthSelenium:
    """
    简化版 Selenium 反爬机制绕过类
    提供基础的反检测功能
    """
    
    def __init__(self, 
                 headless: bool = True,
                 use_undetected: bool = True,
                 use_stealth: bool = True,
                 window_size: tuple = (1920, 1080)):
        """
        初始化简化版反爬Selenium驱动
        
        Args:
            headless: 是否使用无头模式
            use_undetected: 是否使用undetected-chromedriver
            use_stealth: 是否使用selenium-stealth
            window_size: 窗口大小
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium 不可用，请先安装: pip install selenium")
        
        self.headless = headless
        self.use_undetected = use_undetected and UC_AVAILABLE
        self.use_stealth = use_stealth and STEALTH_AVAILABLE
        self.window_size = window_size
        self.driver = None
        
        # 用户代理列表（备用）
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
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
            options.add_argument('--headless=new')
        
        # 随机User-Agent
        if UA_AVAILABLE:
            try:
                ua = UserAgent()
                user_agent = ua.random
            except:
                user_agent = random.choice(self.user_agents)
        else:
            user_agent = random.choice(self.user_agents)
        
        options.add_argument(f'--user-agent={user_agent}')
        logger.info(f"使用User-Agent: {user_agent[:50]}...")
        
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
                    version_main=None,
                    driver_executable_path=None,
                    headless=self.headless
                )
            else:
                # 使用标准 Selenium
                logger.info("使用标准 Selenium 创建驱动")
                options = self._get_chrome_options()
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
            
            logger.info("反检测脚本执行完成")
            
        except Exception as e:
            logger.warning(f"执行反检测脚本时出错: {e}")
    
    def get_page(self, url: str, wait_time: int = 10) -> bool:
        """访问页面"""
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
                pass
            
            # 再次随机等待
            time.sleep(random.uniform(0.5, 2))
            
        except Exception as e:
            logger.warning(f"模拟人类行为时出错: {e}")
    
    def get_page_source(self) -> str:
        """获取页面源码"""
        if self.driver:
            return self.driver.page_source
        return ""
    
    def take_screenshot(self, filename: str = None) -> str:
        """截图"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        if self.driver:
            self.driver.save_screenshot(filename)
            logger.info(f"截图已保存: {filename}")
            return filename
        
        return None
    
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


def test_simple_stealth():
    """测试简化版反爬功能"""
    print("🧪 测试简化版 Selenium 反爬功能")
    print("=" * 50)
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium 不可用，无法测试")
        return
    
    try:
        with SimpleStealthSelenium(headless=True, use_undetected=UC_AVAILABLE) as scraper:
            # 访问测试页面
            test_url = "https://httpbin.org/user-agent"
            print(f"访问测试页面: {test_url}")
            
            if scraper.get_page(test_url):
                print("✅ 页面访问成功")
                
                # 获取页面内容
                content = scraper.get_page_source()
                if "User-Agent" in content:
                    print("✅ User-Agent 设置成功")
                
                # 截图
                screenshot = scraper.take_screenshot("simple_test.png")
                if screenshot:
                    print(f"✅ 截图保存: {screenshot}")
                
                print("✅ 简化版反爬功能测试通过")
            else:
                print("❌ 页面访问失败")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_simple_stealth()