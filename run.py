#!/usr/bin/env python3
"""
简化运行脚本
直接运行此文件即可开始抢购
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    print("=" * 50)
    print("       京东抢购机器人 - 简化运行版")
    print("=" * 50)
    print()
    
    # 检查环境变量文件
    if os.path.exists(".env"):
        print("✅ 检测到 .env 配置文件")
    else:
        print("⚠️  未检测到 .env 文件，将使用默认配置")
        print("   建议复制 .env.example 为 .env 并修改配置")
    
    print()
    print("开始执行抢购程序...")
    print()
    
    main()