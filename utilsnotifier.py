#!/usr/bin/env python3
"""
通知工具
"""

import logging
from config import Config

logger = logging.getLogger(__name__)

def send_notification(title, message):
    """
    发送通知
    TODO: 可以集成邮件、微信、钉钉等通知方式
    """
    config = Config()
    
    if not config.ENABLE_NOTIFICATION:
        return
    
    # 目前只记录日志，可以扩展其他通知方式
    logger.info(f"通知 - {title}: {message}")
    
    # 示例：可以添加邮件通知
    # send_email_notification(title, message)
    
    # 示例：可以添加桌面通知
    # try:
    #     from plyer import notification
    #     notification.notify(
    #         title=title,
    #         message=message,
    #         timeout=10
    #     )
    # except ImportError:
    #     pass