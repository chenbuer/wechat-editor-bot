#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock 数据生成模块
用于测试模式下生成模拟数据
"""

from typing import List, Dict
from io import BytesIO
from PIL import Image, ImageDraw

from modules.news_gatherer import NewsItem


def create_mock_news_items() -> List[NewsItem]:
    """
    创建 Mock 新闻数据

    Returns:
        新闻列表
    """
    return [
        NewsItem(
            title="示例新闻标题 1",
            source="示例来源",
            summary="这是一条示例新闻的摘要内容。",
            url="https://example.com/news1"
        ),
        NewsItem(
            title="示例新闻标题 2",
            source="示例来源",
            summary="这是另一条示例新闻的摘要内容。",
            url="https://example.com/news2"
        )
    ]


def create_mock_weather_data(location: str = "Nanjing") -> Dict:
    """
    创建 Mock 天气数据

    Args:
        location: 位置

    Returns:
        天气数据字典
    """
    return {
        'condition': 'Clear',
        'temperature': '20',
        'time_of_day': 'morning',
        'location': location
    }


def create_mock_cover_image(date_str: str, weather_data: Dict, size: str = "900x383") -> bytes:
    """
    创建 Mock 封面图片

    Args:
        date_str: 日期字符串
        weather_data: 天气数据
        size: 图片尺寸（格式：宽x高）

    Returns:
        图片二进制数据
    """
    # 解析尺寸
    width, height = map(int, size.split('x'))

    # 创建图片
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    d = ImageDraw.Draw(img)

    # 添加文本
    text = f"Mock Cover Image\n{date_str}\n{weather_data.get('condition', 'Clear')} {weather_data.get('temperature', '20')}°C"
    d.text((width // 2, height // 2), text, fill=(255, 255, 255), anchor="mm")

    # 转换为字节
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()


def create_mock_secondary_image(date_str: str, size: str = "500x500") -> bytes:
    """
    创建 Mock 次图

    Args:
        date_str: 日期字符串
        size: 图片尺寸（格式：宽x高）

    Returns:
        图片二进制数据
    """
    # 解析尺寸
    width, height = map(int, size.split('x'))

    # 创建图片
    img = Image.new('RGB', (width, height), color=(109, 137, 73))
    d = ImageDraw.Draw(img)

    # 添加文本
    text = f"Mock Secondary\n{date_str}"
    d.text((width // 2, height // 2), text, fill=(255, 255, 255), anchor="mm")

    # 转换为字节
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()
