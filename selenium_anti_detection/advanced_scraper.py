#!/usr/bin/env python3
"""
高级反检测爬虫示例
整合多种反检测技术的完整爬虫实现
"""

import os
import time
import random
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    logger.error("请先安装 Selenium: pip install selenium")
    exit(1)


class AdvancedScraper:
    """高级反检测爬虫类"""
    
    def __init__(self, use_proxy: bool = False, proxy_list: Optional[List[str]] = None):
        """
        初始化爬虫
        
        Args:
            use_proxy: 是否使用代理
            proxy_list: 代理列表
        """
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        self.driver = None
        self.wait = None
        self.scraped_data = []
        
        # 用户代理池
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        
        # 窗口尺寸池
        self.window_sizes = [
            (1920, 1080), (1366, 768), (1440, 900), 
            (1536, 864), (1680, 1050), (1280, 720)
        ]
    
    def get_next_proxy(self) -> Optional[str]:
        """获取下一个代理"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy
    
    def create_driver(self) -> webdriver.Chrome:
        """创建配置完整的反检测浏览器"""
        
        # Chrome 选项
        options = Options()
        
        # 随机用户代理
        user_agent = random.choice(self.user_agents)
        options.add_argument(f'user-agent={user_agent}')
        logger.info(f"使用 User-Agent: {user_agent}")
        
        # 随机窗口大小
        width, height = random.choice(self.window_sizes)
        options.add_argument(f'window-size={width},{height}')
        
        # 核心反检测参数
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 其他优化参数
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-web-security')
        
        # 禁用图片加载（可选，提高速度）
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # options.add_experimental_option("prefs", prefs)
        
        # 设置语言
        options.add_argument('--lang=zh-CN,zh,en')
        
        # 如果使用代理
        if self.use_proxy and self.proxy_list:
            proxy = self.get_next_proxy()
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
                logger.info(f"使用代理: {proxy}")
        
        # 创建驱动
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # 执行反检测 JavaScript
        self._inject_stealth_js()
        
        return self.driver
    
    def _inject_stealth_js(self):
        """注入反检测 JavaScript 代码"""
        stealth_js = """
        // 1. 删除 webdriver 属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // 2. 修改插件数组
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf", suffixes: "pdf"},
                    description: "Portable Document Format",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                }
            ]
        });
        
        // 3. 修改语言
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        
        // 4. 修改权限查询
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
        );
        
        // 5. 添加 Chrome 对象
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // 6. 修改屏幕分辨率（随机化）
        const screenSizes = [
            {width: 1920, height: 1080},
            {width: 1366, height: 768},
            {width: 1440, height: 900}
        ];
        const randomScreen = screenSizes[Math.floor(Math.random() * screenSizes.length)];
        
        Object.defineProperty(screen, 'width', {get: () => randomScreen.width});
        Object.defineProperty(screen, 'height', {get: () => randomScreen.height});
        Object.defineProperty(screen, 'availWidth', {get: () => randomScreen.width});
        Object.defineProperty(screen, 'availHeight', {get: () => randomScreen.height - 40});
        """
        
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_js
        })
    
    def random_sleep(self, min_seconds: float = 1, max_seconds: float = 3):
        """随机延迟"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"随机延迟 {delay:.2f} 秒")
        time.sleep(delay)
    
    def human_like_mouse_move(self, element=None):
        """模拟人类鼠标移动"""
        actions = ActionChains(self.driver)
        
        if element:
            # 移动到特定元素
            actions.move_to_element(element)
            
            # 添加一些随机偏移
            offset_x = random.randint(-50, 50)
            offset_y = random.randint(-50, 50)
            actions.move_by_offset(offset_x, offset_y)
            actions.move_to_element(element)
        else:
            # 随机移动
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                actions.move_by_offset(x, y)
                self.random_sleep(0.1, 0.3)
        
        actions.perform()
    
    def human_like_scroll(self):
        """模拟人类滚动行为"""
        # 获取页面高度
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        
        # 当前位置
        current_position = 0
        
        # 随机滚动几次
        scroll_count = random.randint(3, 7)
        
        for i in range(scroll_count):
            # 随机滚动距离
            if i == 0:
                # 第一次滚动较小
                scroll_distance = random.randint(100, 300)
            else:
                scroll_distance = random.randint(200, 600)
            
            # 确保不超过页面底部
            current_position = min(current_position + scroll_distance, total_height - viewport_height)
            
            # 平滑滚动
            self.driver.execute_script(f"""
                window.scrollTo({{
                    top: {current_position},
                    behavior: 'smooth'
                }});
            """)
            
            self.random_sleep(0.5, 1.5)
            
            # 偶尔向上滚动一点
            if random.random() < 0.3 and current_position > 300:
                up_distance = random.randint(50, 150)
                current_position -= up_distance
                self.driver.execute_script(f"""
                    window.scrollTo({{
                        top: {current_position},
                        behavior: 'smooth'
                    }});
                """)
                self.random_sleep(0.3, 0.8)
    
    def safe_find_element(self, by: By, value: str, timeout: int = 10):
        """安全地查找元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"未找到元素: {by}={value}")
            return None
    
    def scrape_page(self, url: str) -> Dict[str, Any]:
        """爬取单个页面"""
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'data': {},
            'error': None
        }
        
        try:
            logger.info(f"开始爬取: {url}")
            
            # 访问页面
            self.driver.get(url)
            
            # 等待页面基本加载
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 随机延迟
            self.random_sleep(2, 4)
            
            # 模拟人类行为
            self.human_like_scroll()
            self.human_like_mouse_move()
            
            # 获取页面信息
            result['data']['title'] = self.driver.title
            result['data']['url'] = self.driver.current_url
            
            # 获取所有文本（示例）
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            result['data']['text_length'] = len(body_text)
            
            # 根据实际需求提取数据
            # 例如：提取所有链接
            links = self.driver.find_elements(By.TAG_NAME, "a")
            result['data']['links_count'] = len(links)
            result['data']['links'] = [
                {
                    'text': link.text.strip(),
                    'href': link.get_attribute('href')
                } 
                for link in links[:10]  # 只取前10个作为示例
                if link.get_attribute('href')
            ]
            
            # 截图（可选）
            screenshot_name = f"screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_name)
            result['data']['screenshot'] = screenshot_name
            
            result['success'] = True
            logger.info(f"成功爬取: {url}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"爬取失败 {url}: {e}")
        
        return result
    
    def scrape_multiple_pages(self, urls: List[str], save_results: bool = True):
        """爬取多个页面"""
        logger.info(f"开始爬取 {len(urls)} 个页面")
        
        if not self.driver:
            self.create_driver()
        
        for i, url in enumerate(urls, 1):
            logger.info(f"进度: {i}/{len(urls)}")
            
            # 爬取页面
            result = self.scrape_page(url)
            self.scraped_data.append(result)
            
            # 保存结果
            if save_results:
                self.save_results()
            
            # 页面之间的延迟
            if i < len(urls):
                delay = random.uniform(5, 10)
                logger.info(f"等待 {delay:.2f} 秒后继续...")
                time.sleep(delay)
    
    def save_results(self, filename: str = "scraped_data.json"):
        """保存爬取结果"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
            logger.info(f"结果已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("浏览器已关闭")


class SmartScraper(AdvancedScraper):
    """智能爬虫，包含更多高级功能"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_data = {}
        self.cookies_file = "cookies.json"
    
    def handle_cloudflare(self):
        """处理 Cloudflare 挑战"""
        logger.info("检测到 Cloudflare，尝试绕过...")
        
        # 等待 Cloudflare 检查
        time.sleep(5)
        
        # 检查是否还在 Cloudflare 页面
        if "Checking your browser" in self.driver.page_source:
            logger.info("等待 Cloudflare 验证完成...")
            time.sleep(10)
    
    def handle_captcha(self):
        """处理验证码（需要第三方服务）"""
        logger.warning("检测到验证码，需要手动处理或使用验证码服务")
        # 这里可以集成验证码识别服务
        # 或者等待用户手动解决
        input("请手动解决验证码后按 Enter 继续...")
    
    def save_cookies(self):
        """保存 cookies"""
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)
        logger.info("Cookies 已保存")
    
    def load_cookies(self):
        """加载 cookies"""
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            logger.info("Cookies 已加载")
            return True
        return False
    
    def smart_scrape(self, url: str):
        """智能爬取，包含错误处理和重试机制"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                result = self.scrape_page(url)
                
                # 检查是否需要处理特殊情况
                page_source = self.driver.page_source.lower()
                
                if "cloudflare" in page_source and "checking your browser" in page_source:
                    self.handle_cloudflare()
                    continue
                
                if "captcha" in page_source or "recaptcha" in page_source:
                    self.handle_captcha()
                    continue
                
                # 成功
                return result
                
            except Exception as e:
                retry_count += 1
                logger.error(f"爬取失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    # 更换代理重试
                    if self.use_proxy and self.proxy_list:
                        logger.info("更换代理重试...")
                        self.close()
                        self.create_driver()
                    else:
                        time.sleep(5)
        
        return None


def main():
    """主函数示例"""
    logger.info("=== 高级反检测爬虫示例 ===")
    
    # 配置
    urls_to_scrape = [
        "https://www.google.com/search?q=python+selenium",
        "https://httpbin.org/headers",
        "https://bot.sannysoft.com/"
    ]
    
    # 代理列表（如果有的话）
    proxy_list = [
        # "http://proxy1:port",
        # "http://proxy2:port"
    ]
    
    # 创建爬虫实例
    scraper = SmartScraper(
        use_proxy=False,  # 如果有代理则设为 True
        proxy_list=proxy_list
    )
    
    try:
        # 创建浏览器
        scraper.create_driver()
        
        # 爬取多个页面
        scraper.scrape_multiple_pages(urls_to_scrape)
        
        # 显示结果统计
        successful = sum(1 for r in scraper.scraped_data if r['success'])
        logger.info(f"\n爬取完成！成功: {successful}/{len(urls_to_scrape)}")
        
        # 保持浏览器打开以便查看
        input("\n按 Enter 键关闭浏览器...")
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()