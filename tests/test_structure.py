#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证项目结构
"""

import os
from pathlib import Path

def test_structure():
    """测试项目结构"""
    print("=" * 60)
    print("微信编辑器机器人 - 结构验证")
    print("=" * 60)

    base_dir = Path(__file__).parent

    # 检查目录
    directories = [
        'modules',
        'config',
        'output/articles',
        'output/html',
        'output/images',
        'output/archive'
    ]

    print("\n检查目录结构:")
    for directory in directories:
        path = base_dir / directory
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {directory}")

    # 检查文件
    files = [
        'wechat_editor_bot.py',
        'requirements.txt',
        'README.md',
        'config/wechat_bot_config.yaml',
        'modules/__init__.py',
        'modules/news_gatherer.py',
        'modules/article_generator.py',
        'modules/weather_service.py',
        'modules/image_generator.py',
        'modules/wechat_publisher.py',
        'modules/file_manager.py'
    ]

    print("\n检查文件:")
    for file in files:
        path = base_dir / file
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")

    print("\n" + "=" * 60)
    print("项目结构验证完成！")
    print("=" * 60)

    print("\n下一步:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 配置 API 密钥:")
    print("   - 编辑 config/secrets.yaml 配置 API 密钥")
    print("   - 设置环境变量: export ANTHROPIC_API_KEY=your_key")
    print("3. 测试运行: python wechat_editor_bot.py --mock")
    print("4. 生产运行: python wechat_editor_bot.py --article-type financial_report")

if __name__ == '__main__':
    test_structure()
