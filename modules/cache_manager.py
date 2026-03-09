#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理模块
用于管理各个步骤之间的中间数据
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, TYPE_CHECKING, Union

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from modules.news_gatherer import NewsItem


class CacheManager:
    """缓存管理器 - 管理工作流中间数据"""

    def __init__(self, cache_dir: str = ".cache"):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"缓存目录: {self.cache_dir.absolute()}")

    def _get_cache_path(self, date_str: str, cache_type: str) -> Path:
        """
        获取缓存文件路径

        Args:
            date_str: 日期字符串（如 20260309）
            cache_type: 缓存类型（news/article/weather/images）

        Returns:
            缓存文件路径
        """
        return self.cache_dir / f"{date_str}_{cache_type}.json"

    def save_news(self, date_str: str, news_items: List[Any]) -> Path:
        """
        保存新闻数据

        Args:
            date_str: 日期字符串
            news_items: 新闻列表（NewsItem 对象或字典）

        Returns:
            缓存文件路径
        """
        cache_path = self._get_cache_path(date_str, "news")

        # Helper function to extract fields from either NewsItem objects or dicts
        def get_field(item, field: str, default=''):
            if hasattr(item, field):
                return getattr(item, field)
            elif isinstance(item, dict):
                return item.get(field, default)
            return default

        data = {
            "date": date_str,
            "count": len(news_items),
            "timestamp": datetime.now().isoformat(),
            "news": [
                {
                    "title": get_field(item, 'title'),
                    "source": get_field(item, 'source'),
                    "summary": get_field(item, 'summary'),
                    "url": get_field(item, 'url')
                }
                for item in news_items
            ]
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 新闻缓存已保存: {cache_path} ({len(news_items)} 条)")
        return cache_path

    def load_news(self, date_str: str) -> Optional[List[Any]]:
        """
        加载新闻数据

        Args:
            date_str: 日期字符串

        Returns:
            新闻列表（NewsItem 对象），如果不存在返回 None
        """
        cache_path = self._get_cache_path(date_str, "news")
        if not cache_path.exists():
            logger.warning(f"新闻缓存不存在: {cache_path}")
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Import NewsItem and convert dicts to NewsItem objects
        from modules.news_gatherer import NewsItem

        news_items = [
            NewsItem(
                title=item['title'],
                source=item['source'],
                summary=item['summary'],
                url=item.get('url', '')
            )
            for item in data['news']
        ]

        logger.info(f"✅ 新闻缓存已加载: {cache_path} ({data['count']} 条)")
        return news_items

    def save_article_meta(self, date_str: str, article_type: str,
                         md_path: str, title: str, topic: Optional[str] = None) -> Path:
        """
        保存文章元数据

        Args:
            date_str: 日期字符串
            article_type: 文章类型
            md_path: Markdown 文件路径
            title: 文章标题
            topic: 自定义主题（可选）

        Returns:
            缓存文件路径
        """
        cache_path = self._get_cache_path(date_str, "article")
        data = {
            "date": date_str,
            "article_type": article_type,
            "title": title,
            "topic": topic,
            "md_path": md_path,
            "timestamp": datetime.now().isoformat()
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 文章元数据已保存: {cache_path}")
        return cache_path

    def load_article_meta(self, date_str: str) -> Optional[Dict]:
        """
        加载文章元数据

        Args:
            date_str: 日期字符串

        Returns:
            文章元数据，如果不存在返回 None
        """
        cache_path = self._get_cache_path(date_str, "article")
        if not cache_path.exists():
            logger.warning(f"文章元数据不存在: {cache_path}")
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ 文章元数据已加载: {cache_path}")
        return data

    def save_weather(self, date_str: str, weather_data: Dict) -> Path:
        """
        保存天气数据

        Args:
            date_str: 日期字符串
            weather_data: 天气数据

        Returns:
            缓存文件路径
        """
        cache_path = self._get_cache_path(date_str, "weather")
        data = {
            "date": date_str,
            "timestamp": datetime.now().isoformat(),
            "weather": weather_data
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 天气数据已保存: {cache_path}")
        return cache_path

    def load_weather(self, date_str: str) -> Optional[Dict]:
        """
        加载天气数据

        Args:
            date_str: 日期字符串

        Returns:
            天气数据，如果不存在返回 None
        """
        cache_path = self._get_cache_path(date_str, "weather")
        if not cache_path.exists():
            logger.warning(f"天气数据不存在: {cache_path}")
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ 天气数据已加载: {cache_path}")
        return data['weather']

    def save_images_meta(self, date_str: str, primary_path: str,
                        secondary_path: str, media_id: Optional[str] = None,
                        secondary_media_id: Optional[str] = None) -> Path:
        """
        保存图片元数据

        Args:
            date_str: 日期字符串
            primary_path: 主图路径
            secondary_path: 次图路径
            media_id: 主图 media_id（可选）
            secondary_media_id: 次图 media_id（可选）

        Returns:
            缓存文件路径
        """
        cache_path = self._get_cache_path(date_str, "images")
        data = {
            "date": date_str,
            "primary_path": primary_path,
            "secondary_path": secondary_path,
            "media_id": media_id,
            "secondary_media_id": secondary_media_id,
            "timestamp": datetime.now().isoformat()
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 图片元数据已保存: {cache_path}")
        return cache_path

    def load_images_meta(self, date_str: str) -> Optional[Dict]:
        """
        加载图片元数据

        Args:
            date_str: 日期字符串

        Returns:
            图片元数据，如果不存在返回 None
        """
        cache_path = self._get_cache_path(date_str, "images")
        if not cache_path.exists():
            logger.warning(f"图片元数据不存在: {cache_path}")
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ 图片元数据已加载: {cache_path}")
        return data

    def save_html_meta(self, date_str: str, html_path: str) -> Path:
        """
        保存 HTML 元数据

        Args:
            date_str: 日期字符串
            html_path: HTML 文件路径

        Returns:
            缓存文件路径
        """
        cache_path = self._get_cache_path(date_str, "html")
        data = {
            "date": date_str,
            "html_path": html_path,
            "timestamp": datetime.now().isoformat()
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ HTML 元数据已保存: {cache_path}")
        return cache_path

    def load_html_meta(self, date_str: str) -> Optional[Dict]:
        """
        加载 HTML 元数据

        Args:
            date_str: 日期字符串

        Returns:
            HTML 元数据，如果不存在返回 None
        """
        cache_path = self._get_cache_path(date_str, "html")
        if not cache_path.exists():
            logger.warning(f"HTML 元数据不存在: {cache_path}")
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ HTML 元数据已加载: {cache_path}")
        return data

    def get_status(self, date_str: str) -> Dict[str, Any]:
        """
        获取指定日期的工作流状态

        Args:
            date_str: 日期字符串

        Returns:
            状态字典
        """
        status = {
            "date": date_str,
            "steps": {
                "news": self._get_cache_path(date_str, "news").exists(),
                "article": self._get_cache_path(date_str, "article").exists(),
                "html": self._get_cache_path(date_str, "html").exists(),
                "weather": self._get_cache_path(date_str, "weather").exists(),
                "images": self._get_cache_path(date_str, "images").exists()
            }
        }

        # 加载详细信息
        if status["steps"]["news"]:
            news_data = self.load_news(date_str)
            status["news_count"] = len(news_data) if news_data else 0

        if status["steps"]["article"]:
            article_meta = self.load_article_meta(date_str)
            if article_meta:
                status["article_type"] = article_meta.get("article_type")
                status["article_title"] = article_meta.get("title")
                status["article_path"] = article_meta.get("md_path")

        if status["steps"]["html"]:
            html_meta = self.load_html_meta(date_str)
            if html_meta:
                status["html_path"] = html_meta.get("html_path")

        if status["steps"]["images"]:
            images_meta = self.load_images_meta(date_str)
            if images_meta:
                status["primary_image"] = images_meta.get("primary_path")
                status["secondary_image"] = images_meta.get("secondary_path")
                status["uploaded"] = images_meta.get("media_id") is not None

        return status

    def clean_cache(self, date_str: Optional[str] = None, keep_days: Optional[int] = None):
        """
        清理缓存文件

        Args:
            date_str: 指定日期（如果提供，只清理该日期的缓存）
            keep_days: 保留最近 N 天的缓存（如果提供）
        """
        if date_str:
            # 清理指定日期的缓存
            for cache_type in ["news", "article", "html", "weather", "images"]:
                cache_path = self._get_cache_path(date_str, cache_type)
                if cache_path.exists():
                    cache_path.unlink()
                    logger.info(f"已删除: {cache_path}")
        elif keep_days is not None:
            # 清理旧缓存
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.stat().st_mtime < cutoff_date.timestamp():
                    cache_file.unlink()
                    logger.info(f"已删除: {cache_file}")
        else:
            # 清理所有缓存
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                logger.info(f"已删除: {cache_file}")
