#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻采集模块
使用 Exa API 获取财经新闻和市场数据
"""

import logging
from typing import List, Optional

from .exa_news_gatherer import ExaNewsGatherer

logger = logging.getLogger(__name__)


class NewsItem:
    """新闻条目"""
    def __init__(self, title: str, source: str, summary: str, url: str = ''):
        self.title = title
        self.source = source
        self.summary = summary
        self.url = url


class NewsGatherer:
    """新闻采集器 - 使用 Exa API"""

    def __init__(self, config: dict, exa_api_key: Optional[str] = None,
                 ai_api_key: Optional[str] = None,
                 ai_base_url: Optional[str] = None,
                 ai_model: Optional[str] = None):
        """
        初始化新闻采集器

        Args:
            config: 新闻配置
            exa_api_key: Exa API Key
            ai_api_key: AI API Key (保留用于未来扩展)
            ai_base_url: AI API Base URL
            ai_model: AI 模型名称
        """
        self.config = config

        if not exa_api_key:
            raise ValueError("Exa API Key 未配置，请在 secrets.yaml 中添加 exa_api_key")

        # 初始化 Exa 新闻采集器
        self.exa_gatherer = ExaNewsGatherer(config, exa_api_key)

        logger.info("NewsGatherer 初始化完成 (Exa API)")

    def gather_news(self, date_str: str) -> List[NewsItem]:
        """
        采集新闻和市场数据

        Args:
            date_str: 日期字符串 (YYYYMMDD)

        Returns:
            新闻条目列表（包含财经新闻和市场数据）
        """
        logger.info(f"开始采集新闻: {date_str}")

        # 使用 Exa API 获取所有新闻
        try:
            exa_results = self.exa_gatherer.gather_news(date_str)
            logger.info(f"从 Exa 获取到 {len(exa_results)} 条新闻")

            # 转换为 NewsItem 对象
            news_items = []
            for item in exa_results:
                news_item = NewsItem(
                    title=item['title'],
                    source=item['source'],
                    summary=item['summary'],
                    url=item.get('url', '')
                )
                news_items.append(news_item)

            logger.info(f"总共采集到 {len(news_items)} 条新闻")
            return news_items

        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            raise

