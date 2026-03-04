#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exa API 新闻采集模块
使用单次综合查询获取所有财经新闻和市场数据
"""

import logging
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class ExaNewsGatherer:
    """Exa API 新闻采集器"""

    def __init__(self, config: dict, api_key: str):
        """
        初始化 Exa 新闻采集器

        Args:
            config: 新闻配置（包含 exa_search 配置）
            api_key: Exa API Key
        """
        self.api_key = api_key
        self.config = config
        self.base_url = "https://api.exa.ai"
        self.cache_file = Path("output/.exa_cache.json")

        # 确保 output 目录存在
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("ExaNewsGatherer 初始化完成")

    def gather_news(self, date_str: str) -> List[Dict]:
        """
        单次 API 调用获取所有新闻

        Args:
            date_str: 日期字符串 (YYYYMMDD)

        Returns:
            新闻列表，每条新闻包含 title, source, summary, url
        """
        logger.info(f"开始从 Exa 采集新闻: {date_str}")

        # 检查缓存
        if self._is_cache_valid():
            logger.info("使用缓存的 Exa 搜索结果")
            return self._load_cache()

        # 获取配置
        exa_config = self.config.get('exa_search', {})
        query = exa_config.get('query', '最新财经新闻 股市行情 A股港股美股指数 经济数据指标 宏观政策 国际经济动态')
        num_results = exa_config.get('num_results', 50)
        use_autoprompt = exa_config.get('use_autoprompt', True)
        # 从顶层 news 配置读取 time_range
        time_range = self.config.get('time_range', '24h')

        # 调用 Exa API
        try:
            results = self._search_exa(query, num_results, use_autoprompt, time_range)
            logger.info(f"从 Exa 获取到 {len(results)} 条原始结果")

            # 客户端过滤
            filtered = self._filter_results(results)
            logger.info(f"过滤后剩余 {len(filtered)} 条新闻")

            # 缓存结果
            self._save_cache(filtered)

            return filtered

        except Exception as e:
            logger.error(f"Exa API 调用失败: {e}")
            # 如果有旧缓存，返回旧缓存
            if self.cache_file.exists():
                logger.warning("使用过期缓存数据")
                return self._load_cache()
            raise

    def _search_exa(self, query: str, num_results: int,
                    use_autoprompt: bool, time_range: str) -> List[Dict]:
        """
        调用 Exa API 进行搜索

        Args:
            query: 搜索查询
            num_results: 返回结果数量
            use_autoprompt: 是否使用自动提示优化
            time_range: 时间范围 (24h 或 48h)

        Returns:
            Exa API 返回的结果列表
        """
        # 计算日期范围
        start_date, end_date = self._calculate_date_range(time_range)

        # 构建请求 payload
        payload = {
            "query": query,
            "num_results": num_results,
            "type": "neural",
            "use_autoprompt": use_autoprompt,
            "start_published_date": start_date,
            "end_published_date": end_date,
            "contents": {
                "text": True,
                "highlights": True,
                "summary": True
            }
        }

        # 可选：域名过滤
        include_domains = self.config.get('exa_search', {}).get('include_domains', [])
        if include_domains:
            payload['include_domains'] = include_domains
            logger.info(f"启用域名过滤: {include_domains}")

        logger.info(f"Exa 搜索查询: {query}")
        logger.info(f"日期范围: {start_date} 至 {end_date}")

        # 发送请求
        response = requests.post(
            f"{self.base_url}/search",
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            },
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        # 提取结果
        results = data.get('results', [])
        return results

    def _calculate_date_range(self, time_range: str) -> tuple:
        """
        计算搜索的日期范围

        Args:
            time_range: 时间范围 (24h 或 48h)

        Returns:
            (start_date, end_date) ISO 格式字符串
        """
        # end_date 为当前时间
        end_date = datetime.now()

        # 计算时间范围
        if time_range == '48h':
            hours = 48
        else:
            hours = 24

        start_date = end_date - timedelta(hours=hours)

        # 转换为 ISO 格式
        start_iso = start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_iso = end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        return start_iso, end_iso

    def _filter_results(self, results: List[Dict]) -> List[Dict]:
        """
        客户端过滤结果

        Args:
            results: Exa API 返回的原始结果

        Returns:
            过滤后的新闻列表
        """
        exclude_keywords = self.config.get('exclude_keywords', [])
        filtered = []

        for item in results:
            # 提取字段
            title = item.get('title', '')
            url = item.get('url', '')
            text = item.get('text', '')
            summary = item.get('summary', '')
            highlights = item.get('highlights', [])

            # 使用 summary 或 highlights 作为摘要
            if summary:
                content_summary = summary
            elif highlights:
                content_summary = ' '.join(highlights[:2])  # 取前两个高亮
            else:
                # 截取 text 前 200 字符
                content_summary = text[:200] if text else title

            # 检查排除关键词
            full_text = f"{title} {content_summary}".lower()
            if any(keyword.lower() in full_text for keyword in exclude_keywords):
                logger.debug(f"排除新闻（包含排除关键词）: {title}")
                continue

            # 提取来源（从 URL 域名）
            source = self._extract_source(url)

            # 构建新闻条目
            news_item = {
                'title': title,
                'source': source,
                'summary': content_summary,
                'url': url
            }

            filtered.append(news_item)

        return filtered

    def _extract_source(self, url: str) -> str:
        """从 URL 提取来源名称"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # 移除 www. 前缀
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return "未知来源"

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效（1 小时内）"""
        if not self.cache_file.exists():
            return False

        try:
            cache_time = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            age = datetime.now() - cache_time
            return age.total_seconds() < 3600  # 1 小时
        except Exception:
            return False

    def _load_cache(self) -> List[Dict]:
        """加载缓存的搜索结果"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('results', [])
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            return []

    def _save_cache(self, results: List[Dict]):
        """保存搜索结果到缓存"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"缓存已保存: {self.cache_file}")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
