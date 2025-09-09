#!/usr/bin/env python3
"""
使用 selenium-stealth 插件的反检测示例
selenium-stealth 是一个专门用于隐藏 Selenium 特征的 Python 库
"""

import time
import random
from typing import Optional

# 注意：需要先安装 selenium-stealth
# pip install selenium-stealth

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium_stealth import stealth
except ImportError:
    print("请先安装必要的包：")
    print("pip install selenium selenium-stealth")
    exit(1)


class StealthSelenium:
    """使用 selenium-stealth 的隐形浏览器"""
    
    def __init__(self, headless: bool = False):
        """
        初始化
        
        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.driver = None
    
    def create_driver(self) -> webdriver.Chrome:
        """创建配置了 selenium-stealth 的浏览器"""
        
        # Chrome 选项
        options = Options()
        
        # 基础反检测设置
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 窗口设置
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        # 其他优化
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # 如果需要无头模式
        if self.headless:
            options.add_argument("--headless=new")
        
        # 创建驱动
        self.driver = webdriver.Chrome(options=options)
        
        # 应用 selenium-stealth
        stealth(
            self.driver,
            languages=["zh-CN", "zh", "en-US", "en"],  # 语言设置
            vendor="Google Inc.",  # 浏览器厂商
            platform="Win32",  # 平台
            webgl_vendor="Intel Inc.",  # WebGL 厂商
            renderer="Intel Iris OpenGL Engine",  # 渲染器
            fix_hairline=True,  # 修复 hairline 特征
            run_on_insecure_origins=True,  # 允许在不安全的源上运行
        )
        
        return self.driver
    
    def advanced_stealth_setup(self):
        """高级反检测设置"""
        if not self.driver:
            return
        
        # 注入高级 JavaScript 代码
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // 1. 重写 navigator.webdriver
                delete Object.getPrototypeOf(navigator).webdriver;
                
                // 2. 修改 navigator.plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        const plugins = [
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
                            },
                            {
                                0: {type: "application/x-nacl", suffixes: ""},
                                1: {type: "application/x-pnacl", suffixes: ""},
                                description: "Native Client",
                                filename: "internal-nacl-plugin",
                                length: 2,
                                name: "Native Client"
                            }
                        ];
                        return plugins;
                    }
                });
                
                // 3. 修改 Chrome 对象
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {
                        return {
                            commitLoadTime: Date.now() / 1000,
                            connectionInfo: "ethernet",
                            finishDocumentLoadTime: Date.now() / 1000,
                            finishLoadTime: Date.now() / 1000,
                            firstPaintAfterLoadTime: 0,
                            firstPaintTime: Date.now() / 1000,
                            navigationType: "Reload",
                            npnNegotiatedProtocol: "h2",
                            requestTime: Date.now() / 1000,
                            startLoadTime: Date.now() / 1000,
                            wasAlternateProtocolAvailable: false,
                            wasFetchedViaSpdy: true,
                            wasNpnNegotiated: true
                        };
                    },
                    csi: function() {
                        return {
                            onloadT: Date.now(),
                            pageT: Date.now(),
                            startE: Date.now() - 1000,
                            tran: 15
                        };
                    },
                    app: {
                        isInstalled: false,
                        InstallState: {
                            DISABLED: "disabled",
                            INSTALLED: "installed",
                            NOT_INSTALLED: "not_installed"
                        },
                        RunningState: {
                            CANNOT_RUN: "cannot_run",
                            READY_TO_RUN: "ready_to_run",
                            RUNNING: "running"
                        }
                    }
                };
                
                // 4. 修改权限 API
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({state: Notification.permission});
                    }
                    return originalQuery(parameters);
                };
                
                // 5. 修改 WebGL 参数
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };
                
                // 6. 修改电池 API
                navigator.getBattery = () => {
                    return Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1,
                        onchargingchange: null,
                        onchargingtimechange: null,
                        ondischargingtimechange: null,
                        onlevelchange: null
                    });
                };
                
                // 7. 修改音频指纹
                const context = {
                    createOscillator: () => ({
                        frequency: {
                            setValueAtTime: () => {}
                        },
                        connect: () => {},
                        start: () => {},
                        type: 'triangle'
                    }),
                    createDynamicsCompressor: () => ({
                        threshold: {value: -50},
                        knee: {value: 40},
                        ratio: {value: 12},
                        reduction: {value: -20},
                        attack: {value: 0},
                        release: {value: 0.25},
                        connect: () => {}
                    }),
                    destination: {},
                    currentTime: 0
                };
                
                Object.defineProperty(window, 'AudioContext', {
                    get: () => function() { return context; }
                });
                
                Object.defineProperty(window, 'webkitAudioContext', {
                    get: () => function() { return context; }
                });
            '''
        })
    
    def test_stealth_features(self, url: str = "https://bot.sannysoft.com/"):
        """测试隐形特性"""
        try:
            if not self.driver:
                self.create_driver()
            
            # 应用高级设置
            self.advanced_stealth_setup()
            
            print(f"访问测试网站: {url}")
            self.driver.get(url)
            
            # 等待加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(2)
            
            # 检测各项指标
            checks = {
                "webdriver": "return navigator.webdriver",
                "plugins.length": "return navigator.plugins.length",
                "languages": "return navigator.languages",
                "chrome": "return window.chrome !== undefined",
                "permissions": "return navigator.permissions !== undefined",
                "userAgent": "return navigator.userAgent"
            }
            
            print("\n检测结果：")
            for name, script in checks.items():
                result = self.driver.execute_script(script)
                print(f"{name}: {result}")
            
            # 截图
            self.driver.save_screenshot("stealth_test_result.png")
            print("\n检测结果截图已保存: stealth_test_result.png")
            
        except Exception as e:
            print(f"测试出错: {e}")
    
    def scrape_with_stealth(self, url: str):
        """使用隐形模式爬取网页"""
        try:
            if not self.driver:
                self.create_driver()
                self.advanced_stealth_setup()
            
            print(f"正在访问: {url}")
            self.driver.get(url)
            
            # 随机延迟
            time.sleep(random.uniform(2, 4))
            
            # 模拟滚动
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            for i in range(1, 5):
                scroll_height = total_height * i / 5
                self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(random.uniform(0.5, 1))
            
            # 获取页面信息
            title = self.driver.title
            print(f"页面标题: {title}")
            
            # 根据需要提取其他内容
            # elements = self.driver.find_elements(By.CLASS_NAME, "your-class")
            # for element in elements:
            #     print(element.text)
            
            return True
            
        except Exception as e:
            print(f"爬取出错: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def demonstrate_advanced_techniques():
    """演示高级反检测技术"""
    print("\n=== 高级反检测技术演示 ===\n")
    
    browser = StealthSelenium(headless=False)
    
    try:
        # 创建浏览器
        browser.create_driver()
        browser.advanced_stealth_setup()
        
        # 1. 测试 Canvas 指纹
        print("1. 测试 Canvas 指纹随机化...")
        browser.driver.execute_script("""
            // Canvas 指纹随机化
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (type === 'image/png' && this.width === 280 && this.height === 60) {
                    // 检测到可能是指纹测试
                    const canvas = document.createElement('canvas');
                    canvas.width = this.width;
                    canvas.height = this.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(this, 0, 0);
                    
                    // 添加随机噪声
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] = imageData.data[i] + Math.random() * 2 - 1;
                        imageData.data[i + 1] = imageData.data[i + 1] + Math.random() * 2 - 1;
                        imageData.data[i + 2] = imageData.data[i + 2] + Math.random() * 2 - 1;
                    }
                    ctx.putImageData(imageData, 0, 0);
                    
                    return originalToDataURL.apply(canvas, arguments);
                }
                return originalToDataURL.apply(this, arguments);
            };
            console.log('Canvas 指纹随机化已启用');
        """)
        
        # 2. 测试 WebRTC 泄露防护
        print("2. 测试 WebRTC 泄露防护...")
        browser.driver.execute_script("""
            // 禁用 WebRTC
            const pc = RTCPeerConnection.prototype;
            pc.createDataChannel = () => ({});
            pc.createOffer = () => Promise.resolve({});
            pc.setRemoteDescription = () => Promise.resolve();
            console.log('WebRTC 防护已启用');
        """)
        
        # 3. 访问指纹测试网站
        print("3. 访问浏览器指纹测试网站...")
        browser.driver.get("https://www.browserscan.net/")
        time.sleep(5)
        
        input("\n查看测试结果，按 Enter 继续...")
        
    except Exception as e:
        print(f"演示出错: {e}")
    finally:
        browser.close()


def main():
    """主函数"""
    print("=== Selenium-Stealth 反检测示例 ===\n")
    
    # 创建隐形浏览器
    browser = StealthSelenium(headless=False)
    
    try:
        # 1. 基础测试
        print("1. 执行基础反检测测试...")
        browser.test_stealth_features()
        
        input("\n按 Enter 继续到下一个测试...")
        
        # 2. 访问实际网站
        print("\n2. 测试访问实际网站...")
        browser.scrape_with_stealth("https://www.google.com")
        
        input("\n按 Enter 查看高级技术演示...")
        
        # 关闭当前浏览器
        browser.close()
        
        # 3. 高级技术演示
        demonstrate_advanced_techniques()
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        browser.close()
        print("\n程序结束")


if __name__ == "__main__":
    main()