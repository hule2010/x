#!/usr/bin/env python3
"""
使用 undetected-chromedriver 的反检测示例
undetected-chromedriver 是一个专门设计来绕过反爬虫检测的 ChromeDriver
"""

import time
import random
from typing import Optional

# 注意：需要先安装 undetected-chromedriver
# pip install undetected-chromedriver

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("请先安装必要的包：")
    print("pip install undetected-chromedriver selenium")
    exit(1)


class StealthBrowser:
    """隐形浏览器类，封装了反检测功能"""
    
    def __init__(self, headless: bool = False, use_proxy: Optional[str] = None):
        """
        初始化隐形浏览器
        
        Args:
            headless: 是否使用无头模式（注意：无头模式更容易被检测）
            use_proxy: 代理地址，格式: "http://user:pass@host:port"
        """
        self.headless = headless
        self.proxy = use_proxy
        self.driver = None
    
    def create_driver(self) -> uc.Chrome:
        """创建 undetected-chromedriver 实例"""
        
        # 配置选项
        options = uc.ChromeOptions()
        
        # 设置用户代理池
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        
        # 基础设置
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # 设置窗口大小
        options.add_argument("--window-size=1920,1080")
        
        # 设置语言
        options.add_argument("--lang=zh-CN,zh,en")
        
        # 如果使用代理
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        # 禁用图片加载（可选，提高速度）
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # options.add_experimental_option("prefs", prefs)
        
        # 如果使用无头模式（不推荐，容易被检测）
        if self.headless:
            options.add_argument('--headless=new')  # 使用新版无头模式
            # 无头模式下的额外设置
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
        
        # 创建驱动
        # version_main 参数可以指定 Chrome 版本，None 表示自动检测
        self.driver = uc.Chrome(
            options=options,
            version_main=None,  # 自动检测 Chrome 版本
            driver_executable_path=None  # 自动下载对应版本的 driver
        )
        
        # 设置隐式等待
        self.driver.implicitly_wait(10)
        
        # 执行额外的 JavaScript 来增强隐身性
        self.driver.execute_script("""
            // 修改 navigator.permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );
            
            // 添加 Chrome 的特定属性
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)
        
        return self.driver
    
    def random_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """随机延迟，模拟人类行为"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def human_like_scroll(self):
        """模拟人类滚动行为"""
        if not self.driver:
            return
        
        # 获取页面高度
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        
        # 随机滚动几次
        scroll_times = random.randint(3, 7)
        
        for _ in range(scroll_times):
            # 随机滚动距离
            scroll_distance = random.randint(200, 600)
            current_position = min(current_position + scroll_distance, total_height)
            
            # 平滑滚动
            self.driver.execute_script(f"""
                window.scrollTo({{
                    top: {current_position},
                    behavior: 'smooth'
                }});
            """)
            
            self.random_delay(0.5, 1.5)
    
    def human_like_mouse_move(self):
        """模拟人类鼠标移动（通过 JavaScript）"""
        if not self.driver:
            return
        
        # 生成随机鼠标轨迹
        self.driver.execute_script("""
            // 创建并触发鼠标移动事件
            function triggerMouseEvent(x, y, eventType) {
                const event = new MouseEvent(eventType, {
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: x,
                    clientY: y
                });
                document.elementFromPoint(x, y)?.dispatchEvent(event);
            }
            
            // 生成随机轨迹
            let startX = Math.random() * window.innerWidth;
            let startY = Math.random() * window.innerHeight;
            let endX = Math.random() * window.innerWidth;
            let endY = Math.random() * window.innerHeight;
            
            // 模拟鼠标移动
            for (let i = 0; i <= 10; i++) {
                let x = startX + (endX - startX) * i / 10;
                let y = startY + (endY - startY) * i / 10;
                setTimeout(() => triggerMouseEvent(x, y, 'mousemove'), i * 50);
            }
        """)
    
    def test_detection(self, test_url: str = "https://bot.sannysoft.com/"):
        """测试反检测效果"""
        try:
            if not self.driver:
                self.create_driver()
            
            print(f"访问检测网站: {test_url}")
            self.driver.get(test_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 模拟人类行为
            self.random_delay()
            self.human_like_scroll()
            self.human_like_mouse_move()
            
            # 检测结果
            webdriver_check = self.driver.execute_script("return navigator.webdriver")
            print(f"navigator.webdriver: {webdriver_check}")
            
            # 检查其他特征
            plugins_length = self.driver.execute_script("return navigator.plugins.length")
            print(f"插件数量: {plugins_length}")
            
            languages = self.driver.execute_script("return navigator.languages")
            print(f"语言设置: {languages}")
            
            user_agent = self.driver.execute_script("return navigator.userAgent")
            print(f"User-Agent: {user_agent}")
            
            # 截图保存检测结果
            self.driver.save_screenshot("detection_test_result.png")
            print("检测结果已保存到: detection_test_result.png")
            
            return webdriver_check is None or webdriver_check is False
            
        except Exception as e:
            print(f"测试过程中出错: {e}")
            return False
    
    def scrape_example(self, url: str):
        """爬取示例"""
        try:
            if not self.driver:
                self.create_driver()
            
            print(f"访问: {url}")
            self.driver.get(url)
            
            # 随机延迟
            self.random_delay(1, 3)
            
            # 模拟人类行为
            self.human_like_scroll()
            
            # 获取页面标题
            title = self.driver.title
            print(f"页面标题: {title}")
            
            # 获取页面内容（示例）
            # 根据实际需求修改选择器
            try:
                content = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                ).text
                print(f"页面内容长度: {len(content)} 字符")
            except Exception as e:
                print(f"获取内容失败: {e}")
            
            return title
            
        except Exception as e:
            print(f"爬取过程中出错: {e}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """主函数示例"""
    print("=== Undetected ChromeDriver 反检测示例 ===\n")
    
    # 创建隐形浏览器实例
    browser = StealthBrowser(headless=False)
    
    try:
        # 1. 测试反检测效果
        print("1. 测试反检测效果...")
        is_undetected = browser.test_detection()
        print(f"反检测测试{'通过' if is_undetected else '失败'}！\n")
        
        time.sleep(2)
        
        # 2. 访问 Google
        print("2. 测试访问 Google...")
        browser.scrape_example("https://www.google.com")
        
        time.sleep(2)
        
        # 3. 访问其他网站（根据需要修改）
        print("\n3. 测试访问其他网站...")
        # browser.scrape_example("https://example.com")
        
        # 保持浏览器打开，让用户查看
        input("\n按 Enter 键关闭浏览器...")
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        browser.close()
        print("浏览器已关闭")


if __name__ == "__main__":
    main()