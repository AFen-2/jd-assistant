#!/usr/bin/env python3
"""
京东抢购机器人
Author: GitHub User
Description: 自动抢购京东商品的Python脚本
"""

import time
import datetime
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import Config
from utils.logger import setup_logger
from utils.notifier import send_notification

class JDPurchaseBot:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger()
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            self.logger.info("正在初始化浏览器驱动...")
            
            options = webdriver.ChromeOptions()
            
            # 配置选项
            if self.config.HEADLESS:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 用户代理设置
            if self.config.USER_AGENT:
                options.add_argument(f'--user-agent={self.config.USER_AGENT}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 隐藏自动化特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self.config.USER_AGENT or self.driver.execute_script("return navigator.userAgent;")
            })
            
            self.wait = WebDriverWait(self.driver, self.config.TIMEOUT)
            self.logger.info("浏览器驱动初始化成功")
            
        except Exception as e:
            self.logger.error(f"浏览器驱动初始化失败: {str(e)}")
            raise
    
    def login_jd(self):
        """登录京东"""
        try:
            self.logger.info("正在打开登录页面...")
            self.driver.get("https://passport.jd.com/new/login.aspx")
            
            # 切换到扫码登录
            try:
                qr_login = self.wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "login-tab-r"))
                )
                qr_login.click()
                self.logger.info("已切换到扫码登录")
            except TimeoutException:
                self.logger.info("扫码登录按钮未找到，继续当前页面")
            
            self.logger.info("请使用京东APP扫描二维码登录...")
            self.logger.info("等待用户登录...")
            
            # 等待登录成功（检查是否跳转到首页或用户中心）
            login_success = False
            for i in range(self.config.LOGIN_TIMEOUT):
                current_url = self.driver.current_url
                if "passport.jd.com" not in current_url or "user.jd.com" in current_url:
                    login_success = True
                    break
                
                # 检查是否有用户信息显示
                try:
                    user_element = self.driver.find_element(By.CLASS_NAME, "nickname")
                    if user_element.text:
                        login_success = True
                        break
                except:
                    pass
                
                time.sleep(1)
            
            if login_success:
                self.is_logged_in = True
                self.logger.info("登录成功！")
                send_notification("京东登录成功", "已成功登录京东账号")
            else:
                self.logger.warning("登录状态未确认，请检查是否登录成功")
                
        except Exception as e:
            self.logger.error(f"登录过程出错: {str(e)}")
            raise
    
    def check_availability(self):
        """检查商品是否可购买"""
        try:
            # 检查是否有货
            try:
                stock_element = self.driver.find_element(By.CLASS_NAME, "store-prompt")
                if "无货" in stock_element.text:
                    return False, "商品无货"
            except NoSuchElementException:
                pass
            
            # 检查预约状态
            try:
                reserve_element = self.driver.find_element(By.ID, "btn-reservation")
                if reserve_element.is_displayed():
                    return True, "可预约"
            except NoSuchElementException:
                pass
            
            # 检查立即购买按钮
            try:
                buy_button = self.driver.find_element(By.CLASS_NAME, "btn-addcart")
                if buy_button.is_enabled():
                    return True, "可立即购买"
            except NoSuchElementException:
                pass
            
            return False, "无法确定商品状态"
            
        except Exception as e:
            self.logger.error(f"检查商品状态失败: {str(e)}")
            return False, f"检查失败: {str(e)}"
    
    def click_buy_now(self):
        """点击购买按钮"""
        buy_selectors = [
            (By.CLASS_NAME, "btn-addcart"),  # 立即购买
            (By.ID, "btn-reservation"),      # 预约购买
            (By.CLASS_NAME, "buy-btn"),      # 购买按钮
            (By.XPATH, "//a[contains(text(), '立即购买')]"),
            (By.XPATH, "//button[contains(text(), '立即购买')]")
        ]
        
        for selector in buy_selectors:
            try:
                buy_button = self.wait.until(EC.element_to_be_clickable(selector))
                buy_button.click()
                self.logger.info(f"成功点击购买按钮: {selector[1]}")
                return True
            except (TimeoutException, NoSuchElementException):
                continue
        
        raise Exception("找不到可点击的购买按钮")
    
    def submit_order(self):
        """提交订单"""
        try:
            # 切换到新窗口（订单页面）
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 等待订单页面加载
            time.sleep(2)
            
            # 尝试多种提交订单的选择器
            submit_selectors = [
                (By.CLASS_NAME, "checkout-submit"),
                (By.XPATH, "//button[contains(text(), '提交订单')]"),
                (By.ID, "order-submit"),
                (By.CLASS_NAME, "btn-checkout")
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.wait.until(EC.element_to_be_clickable(selector))
                    submit_button.click()
                    self.logger.info("订单提交成功！")
                    send_notification("抢购成功", "商品抢购成功，请及时付款")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            raise Exception("找不到提交订单按钮")
            
        except Exception as e:
            self.logger.error(f"提交订单失败: {str(e)}")
            raise
    
    def purchase_item(self, url):
        """抢购商品"""
        self.logger.info(f"正在抢购商品: {url}")
        
        try:
            # 打开商品页面
            self.driver.get(url)
            time.sleep(3)
            
            # 检查商品状态
            available, status = self.check_availability()
            if not available:
                raise Exception(f"商品不可购买: {status}")
            
            self.logger.info(f"商品状态: {status}")
            
            # 重试机制
            for attempt in range(self.config.MAX_RETRY):
                try:
                    self.logger.info(f"第 {attempt + 1} 次尝试抢购")
                    
                    # 点击购买
                    self.click_buy_now()
                    
                    # 提交订单
                    self.submit_order()
                    
                    self.logger.info("抢购流程完成！")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                    if attempt < self.config.MAX_RETRY - 1:
                        self.logger.info(f"{self.config.RETRY_DELAY}秒后重试...")
                        time.sleep(self.config.RETRY_DELAY)
                        # 刷新页面
                        self.driver.refresh()
                        time.sleep(1)
                    else:
                        raise
            
        except Exception as e:
            self.logger.error(f"抢购失败: {str(e)}")
            send_notification("抢购失败", f"抢购失败: {str(e)}")
            return False
    
    def wait_until_purchase_time(self):
        """等待到抢购时间"""
        target_time = datetime.datetime.strptime(self.config.PURCHASE_TIME, "%Y-%m-%d %H:%M:%S")
        self.logger.info(f"等待抢购时间: {self.config.PURCHASE_TIME}")
        
        while True:
            now = datetime.datetime.now()
            if now >= target_time:
                self.logger.info("抢购时间到！开始抢购！")
                break
            
            # 计算剩余时间
            remaining = target_time - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if remaining.seconds % 10 == 0:  # 每10秒打印一次
                self.logger.info(f"距离抢购还有: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            time.sleep(0.1)
    
    def run(self):
        """运行抢购程序"""
        try:
            self.logger.info("京东抢购机器人启动...")
            
            # 设置浏览器
            self.setup_driver()
            
            # 登录
            if not self.is_logged_in:
                self.login_jd()
            
            # 等待抢购时间
            if self.config.PURCHASE_TIME:
                self.wait_until_purchase_time()
            
            # 开始抢购
            success = self.purchase_item(self.config.ITEM_URL)
            
            if success:
                self.logger.info("🎉 抢购程序执行成功！")
            else:
                self.logger.error("❌ 抢购程序执行失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"程序运行出错: {str(e)}")
            send_notification("程序异常", f"抢购程序异常: {str(e)}")
            return False
        
        finally:
            if self.driver:
                if self.config.KEEP_BROWSER_OPEN:
                    self.logger.info("浏览器保持打开状态，按Ctrl+C退出")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        pass
                self.driver.quit()
                self.logger.info("浏览器已关闭")

def main():
    """主函数"""
    bot = JDPurchaseBot()
    
    # 检查配置
    if not bot.config.validate():
        sys.exit(1)
    
    # 运行抢购
    success = bot.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()