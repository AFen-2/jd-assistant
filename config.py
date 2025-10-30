#!/usr/bin/env python3
"""
配置文件
"""

import os
from datetime import datetime

class Config:
    def __init__(self):
        # 商品URL
        self.ITEM_URL = os.getenv("ITEM_URL", "https://item.jd.com/100209543701.html")
        
        # 抢购时间 (格式: YYYY-MM-DD HH:MM:SS)
        self.PURCHASE_TIME = os.getenv("PURCHASE_TIME", "2024-01-01 10:00:00")
        
        # 浏览器设置
        self.HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
        self.USER_AGENT = os.getenv("USER_AGENT", "")
        self.KEEP_BROWSER_OPEN = os.getenv("KEEP_BROWSER_OPEN", "False").lower() == "true"
        
        # 超时设置
        self.TIMEOUT = int(os.getenv("TIMEOUT", "10"))
        self.LOGIN_TIMEOUT = int(os.getenv("LOGIN_TIMEOUT", "120"))
        
        # 重试设置
        self.MAX_RETRY = int(os.getenv("MAX_RETRY", "3"))
        self.RETRY_DELAY = float(os.getenv("RETRY_DELAY", "0.5"))
        
        # 通知设置
        self.ENABLE_NOTIFICATION = os.getenv("ENABLE_NOTIFICATION", "True").lower() == "true"
        
        # 日志设置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self):
        """验证配置"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 检查URL格式
        if not self.ITEM_URL.startswith("https://item.jd.com/"):
            logger.error("商品URL格式不正确，应为京东商品链接")
            return False
        
        # 检查时间格式
        try:
            datetime.strptime(self.PURCHASE_TIME, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.error("抢购时间格式不正确，应为: YYYY-MM-DD HH:MM:SS")
            return False
        
        logger.info("配置验证通过")
        return True
    
    def __str__(self):
        """返回配置信息"""
        return f"""
配置信息:
  商品URL: {self.ITEM_URL}
  抢购时间: {self.PURCHASE_TIME}
  无头模式: {self.HEADLESS}
  超时时间: {self.TIMEOUT}秒
  登录超时: {self.LOGIN_TIMEOUT}秒
  最大重试: {self.MAX_RETRY}次
  重试延迟: {self.RETRY_DELAY}秒
  保持浏览器打开: {self.KEEP_BROWSER_OPEN}
  日志级别: {self.LOG_LEVEL}
        """