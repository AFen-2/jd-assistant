#!/usr/bin/env python3
"""
日志工具
"""

import logging
import sys
from config import Config

def setup_logger():
    """设置日志"""
    config = Config()
    
    logger = logging.getLogger('jd_purchase_bot')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件handler
    try:
        file_handler = logging.FileHandler('purchase_bot.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建日志文件: {str(e)}")
    
    return logger