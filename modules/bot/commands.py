#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令模块
包含所有命令的实现逻辑
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

from modules.news_gatherer import NewsItem
from modules.bot.config import ServiceFactory
from modules.bot import mock_data

logger = logging.getLogger(__name__)


class BotCommands:
    """机器人命令处理器 - 实现所有命令逻辑"""

    def __init__(self, services: ServiceFactory):
        """
        初始化命令处理器

        Args:
            services: 服务工厂实例
        """
        self.services = services
        self.config = services.config
        self.mock_mode = services.mock_mode

        # 快捷访问服务
        self.article_generator = services.article_generator
        self.weather_service = services.weather_service
        self.image_generator = services.image_generator
        self.wechat_publisher = services.wechat_publisher
        self.file_manager = services.file_manager
        self.cache_manager = services.cache_manager
        self.exa_api_key = services.exa_api_key

    def search(self, article_type: str = None, topic: str = None, date_str: str = None,
               time_range: int = None, num_results: int = None, enable_search: bool = False,
               output: str = None) -> str:
        """
        搜索新闻命令

        Args:
            article_type: 文章类型
            topic: 搜索主题（替换模板中的 {topic} 占位符）
            date_str: 日期字符串
            time_range: 时间范围（小时）
            num_results: 结果数量
            enable_search: 强制启用搜索
            output: 输出文件路径

        Returns:
            缓存文件路径
        """
        logger.info("=" * 60)
        logger.info("[命令] 搜索新闻")
        logger.info("=" * 60)

        # 确定参数
        article_type = article_type or self.config['article'].get('article_type', 'financial_report')
        date_str = date_str or datetime.now().strftime('%Y%m%d')

        # 获取搜索配置
        search_config = self.article_generator.get_news_search_config(article_type, topic)

        # 检查是否需要搜索
        if not search_config and not enable_search:
            logger.info(f"文章类型 '{article_type}' 默认不需要搜索新闻")
            logger.info("如需强制搜索，请使用 --enable-search 参数")
            return None

        if not search_config:
            logger.error("无法获取搜索配置，请检查文章类型或模板配置")
            return None

        # 覆盖配置参数
        if time_range is not None:
            search_config['time_range'] = time_range
        if num_results is not None:
            search_config['num_results'] = num_results

        logger.info(f"文章类型: {article_type}")
        if topic:
            logger.info(f"搜索主题: {topic}")
        logger.info(f"日期: {date_str}")
        logger.info(f"时间范围: {search_config.get('time_range')} 小时")
        logger.info(f"结果数量: {search_config.get('num_results')}")

        # 采集新闻
        news_items = self._gather_news(date_str, search_config)

        # 保存到缓存
        cache_path = self.cache_manager.save_news(date_str, news_items)

        logger.info("=" * 60)
        logger.info(f"✅ 新闻搜索完成: {len(news_items)} 条")
        logger.info(f"缓存文件: {cache_path}")
        logger.info("=" * 60)

        return str(cache_path)

    def generate(self, news_file: str = None, article_type: str = None, topic: str = None,
                 date_str: str = None, output: str = None) -> str:
        """
        生成文章命令

        Args:
            news_file: 新闻数据文件
            article_type: 文章类型
            topic: 自定义主题
            date_str: 日期字符串
            output: 输出文件路径

        Returns:
            文章文件路径
        """
        logger.info("=" * 60)
        logger.info("[命令] 生成文章")
        logger.info("=" * 60)

        # 确定参数
        article_type = article_type or self.config['article'].get('article_type', 'financial_report')
        date_str = date_str or datetime.now().strftime('%Y%m%d')

        # 加载新闻数据
        news_items = []
        if news_file:
            logger.info(f"从文件加载新闻: {news_file}")
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                news_items = [NewsItem(**item) for item in data.get('news', [])]
        else:
            # 从缓存加载（load_news 现在返回 NewsItem 对象列表）
            news_items = self.cache_manager.load_news(date_str) or []
            if not news_items:
                logger.info("未找到新闻缓存，将生成不依赖新闻的文章")

        logger.info(f"文章类型: {article_type}")
        if topic:
            logger.info(f"自定义主题: {topic}")
        logger.info(f"新闻数量: {len(news_items)}")

        # 生成文章
        article_md = self.article_generator.generate_article(
            news_items=news_items,
            date_str=date_str,
            article_type=article_type,
            custom_topic=topic
        )

        # 保存文章
        md_path = self.file_manager.save_article(article_md, date_str, 'md', article_type)

        # 提取标题
        title = self._extract_title(article_md)

        # 保存元数据到缓存
        self.cache_manager.save_article_meta(date_str, article_type, str(md_path), title, topic)

        logger.info("=" * 60)
        logger.info(f"✅ 文章生成完成")
        logger.info(f"标题: {title}")
        logger.info(f"文件: {md_path}")
        logger.info("=" * 60)

        return str(md_path)

    def convert(self, input_file: str = None, theme: str = None, date_str: str = None,
                output: str = None) -> str:
        """
        转换为微信 HTML 命令

        Args:
            input_file: 输入 Markdown 文件
            theme: 主题样式
            date_str: 日期字符串
            output: 输出文件路径

        Returns:
            HTML 文件路径
        """
        logger.info("=" * 60)
        logger.info("[命令] 转换为微信 HTML")
        logger.info("=" * 60)

        # 确定参数
        date_str = date_str or datetime.now().strftime('%Y%m%d')
        theme = theme or self.config.get('wechat', {}).get('theme', 'warm')

        # 确定输入文件
        if input_file:
            md_path = Path(input_file)
        else:
            # 从缓存获取
            article_meta = self.cache_manager.load_article_meta(date_str)
            if article_meta and article_meta.get('md_path'):
                md_path = Path(article_meta['md_path'])
            else:
                # 尝试默认路径
                article_type = self.config['article'].get('article_type', 'financial_report')
                md_path = Path('output') / f'{date_str}_{article_type}.md'

        if not md_path.exists():
            logger.error(f"Markdown 文件不存在: {md_path}")
            raise FileNotFoundError(f"Markdown 文件不存在: {md_path}")

        logger.info(f"输入文件: {md_path}")
        logger.info(f"主题: {theme}")

        # 读取 Markdown
        with open(md_path, 'r', encoding='utf-8') as f:
            article_md = f.read()

        # 转换为 HTML
        article_html = self.wechat_publisher.convert_to_wechat_html(article_md, theme=theme)

        # 保存 HTML
        # 从缓存读取 article_type，确保与生成的文章类型一致
        article_meta = self.cache_manager.load_article_meta(date_str)
        article_type = article_meta.get('article_type') if article_meta else self.config['article'].get('article_type', 'financial_report')
        html_path = self.file_manager.save_article(article_html, date_str, 'html', article_type)

        # 保存元数据到缓存
        self.cache_manager.save_html_meta(date_str, str(html_path))

        logger.info("=" * 60)
        logger.info(f"✅ HTML 转换完成")
        logger.info(f"文件: {html_path}")
        logger.info("=" * 60)

        return str(html_path)

    def weather(self, location: str = None, date_str: str = None, output: str = None) -> Dict:
        """
        获取天气信息命令

        Args:
            location: 位置
            date_str: 日期字符串
            output: 输出文件路径

        Returns:
            天气数据
        """
        logger.info("=" * 60)
        logger.info("[命令] 获取天气信息")
        logger.info("=" * 60)

        # 确定参数
        date_str = date_str or datetime.now().strftime('%Y%m%d')
        location = location or self.config.get('weather', {}).get('location', 'Nanjing')

        logger.info(f"位置: {location}")

        # 获取天气
        if self.mock_mode:
            weather_data = mock_data.create_mock_weather_data(location)
            logger.info("Mock 模式: 使用默认天气数据")
        else:
            # 临时更新位置
            original_location = self.weather_service.location
            self.weather_service.location = location
            weather_data = self.weather_service.get_current_weather()
            self.weather_service.location = original_location

        # 保存到缓存
        self.cache_manager.save_weather(date_str, weather_data)

        logger.info("=" * 60)
        logger.info(f"✅ 天气信息获取完成")
        logger.info(f"天气: {weather_data.get('condition')} {weather_data.get('temperature')}°C")
        logger.info("=" * 60)

        return weather_data

    def image(self, weather_file: str = None, date_str: str = None, output_dir: str = None) -> Dict:
        """
        生成封面图片命令

        Args:
            weather_file: 天气数据文件
            date_str: 日期字符串
            output_dir: 输出目录

        Returns:
            图片路径字典
        """
        logger.info("=" * 60)
        logger.info("[命令] 生成封面图片")
        logger.info("=" * 60)

        # 确定参数
        date_str = date_str or datetime.now().strftime('%Y%m%d')

        # 加载天气数据
        if weather_file:
            logger.info(f"从文件加载天气: {weather_file}")
            with open(weather_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                weather_data = data.get('weather', {})
        else:
            # 从缓存加载
            weather_data = self.cache_manager.load_weather(date_str)
            if not weather_data:
                logger.error("未找到天气数据，请先运行 weather 命令")
                raise ValueError("未找到天气数据")

        logger.info(f"天气: {weather_data.get('condition')} {weather_data.get('temperature')}°C")

        # 生成图片
        if self.mock_mode:
            cover_image = mock_data.create_mock_cover_image(
                date_str, weather_data, self.config['image']['primary_size']
            )
            logger.info("Mock 模式: 使用默认图片")
        else:
            cover_image = self.image_generator.generate_cover_image(
                weather_data, size=self.config['image']['primary_size']
            )

        # 保存图片
        image_path = self.file_manager.save_image(cover_image, date_str, 'primary')

        # 保存元数据到缓存
        self.cache_manager.save_images_meta(date_str, str(image_path), None)

        logger.info("=" * 60)
        logger.info(f"✅ 图片生成完成")
        logger.info(f"封面图: {image_path}")
        logger.info("=" * 60)

        return {
            'primary': str(image_path)
        }

    def upload(self, html_file: str = None, image_file: str = None,
               title: str = None, markdown_file: str = None, date_str: str = None,
               create_draft: bool = True) -> str:
        """
        上传到微信命令

        Args:
            html_file: HTML 文件
            image_file: 封面图文件
            title: 文章标题
            markdown_file: Markdown 文件（用于提取标题）
            date_str: 日期字符串
            create_draft: 是否创建草稿

        Returns:
            草稿 media_id
        """
        logger.info("=" * 60)
        logger.info("[命令] 上传到微信")
        logger.info("=" * 60)

        if self.mock_mode:
            logger.info("Mock 模式: 跳过微信上传")
            return None

        # 确定参数
        date_str = date_str or datetime.now().strftime('%Y%m%d')

        # 确定文件路径
        if not html_file:
            html_meta = self.cache_manager.load_html_meta(date_str)
            if html_meta:
                html_file = html_meta.get('html_path')

        if not image_file:
            images_meta = self.cache_manager.load_images_meta(date_str)
            if images_meta:
                image_file = image_file or images_meta.get('primary_path')

        # 检查文件
        if not html_file or not Path(html_file).exists():
            logger.error(f"HTML 文件不存在: {html_file}")
            raise FileNotFoundError(f"HTML 文件不存在: {html_file}")

        if not image_file or not Path(image_file).exists():
            logger.error(f"封面图文件不存在: {image_file}")
            raise FileNotFoundError(f"封面图文件不存在: {image_file}")

        # 读取 HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            article_html = f.read()

        # 确定标题
        if not title:
            if markdown_file and Path(markdown_file).exists():
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    title = self._extract_title(f.read())
            else:
                article_meta = self.cache_manager.load_article_meta(date_str)
                if article_meta:
                    title = article_meta.get('title')
                else:
                    title = f"文章 - {datetime.now().strftime('%Y年%m月%d日')}"

        logger.info(f"标题: {title}")
        logger.info(f"HTML: {html_file}")
        logger.info(f"封面图: {image_file}")

        # 上传图片
        logger.info("上传封面图...")
        media_id = self.wechat_publisher.upload_image(image_file)

        # 更新缓存
        images_meta = self.cache_manager.load_images_meta(date_str) or {}
        self.cache_manager.save_images_meta(
            date_str,
            images_meta.get('primary_path', image_file),
            None,
            media_id,
            None
        )

        # 创建草稿
        draft_media_id = None
        if create_draft:
            logger.info("创建草稿...")
            draft_media_id = self.wechat_publisher.create_draft(
                title, article_html, media_id
            )

            logger.info("=" * 60)
            logger.info(f"✅ 草稿创建成功: {draft_media_id}")
            logger.info("请在微信公众号后台审核并发布")
            logger.info("=" * 60)
        else:
            logger.info("=" * 60)
            logger.info(f"✅ 图片上传完成")
            logger.info(f"封面图 media_id: {media_id}")
            logger.info("=" * 60)

        return draft_media_id

    def status(self, date_str: str = None):
        """
        查看状态命令

        Args:
            date_str: 日期字符串
        """
        date_str = date_str or datetime.now().strftime('%Y%m%d')

        logger.info("=" * 60)
        logger.info(f"[状态] {date_str}")
        logger.info("=" * 60)

        status = self.cache_manager.get_status(date_str)

        # 显示各步骤状态
        steps = [
            ('news', '新闻搜索', 'search'),
            ('article', '文章生成', 'generate'),
            ('html', 'HTML 转换', 'convert'),
            ('weather', '天气获取', 'weather'),
            ('images', '图片生成', 'image')
        ]

        completed_steps = []
        pending_steps = []

        for key, name, cmd in steps:
            if status['steps'][key]:
                completed_steps.append((key, name, cmd))
                icon = "✅"
            else:
                pending_steps.append((key, name, cmd))
                icon = "⏳"

            logger.info(f"{icon} {name}: {'已完成' if status['steps'][key] else '未完成'}")

            # 显示详细信息
            if key == 'news' and status['steps'][key]:
                logger.info(f"   └─ 新闻数量: {status.get('news_count', 0)} 条")
            elif key == 'article' and status['steps'][key]:
                logger.info(f"   └─ 标题: {status.get('article_title', 'N/A')}")
                logger.info(f"   └─ 文件: {status.get('article_path', 'N/A')}")
            elif key == 'html' and status['steps'][key]:
                logger.info(f"   └─ 文件: {status.get('html_path', 'N/A')}")
            elif key == 'images' and status['steps'][key]:
                logger.info(f"   └─ 封面图: {status.get('primary_image', 'N/A')}")
                if status.get('uploaded'):
                    logger.info(f"   └─ 已上传到微信")

        # 建议下一步
        logger.info("")
        if pending_steps:
            next_step = pending_steps[0]
            logger.info(f"💡 下一步: python wechat_editor_bot.py {next_step[2]}")
        else:
            logger.info("✅ 所有步骤已完成！")
            if not status.get('uploaded'):
                logger.info("💡 提示: 运行 upload 命令上传到微信")

        logger.info("=" * 60)

    def clean(self, date_str: str = None, keep_days: int = None,
              cache_only: bool = False, output_only: bool = False):
        """
        清理缓存命令

        Args:
            date_str: 指定日期
            keep_days: 保留天数
            cache_only: 只清理缓存
            output_only: 只清理输出
        """
        logger.info("=" * 60)
        logger.info("[命令] 清理文件")
        logger.info("=" * 60)

        if not output_only:
            logger.info("清理缓存...")
            self.cache_manager.clean_cache(date_str, keep_days)

        if not cache_only:
            logger.info("清理输出文件...")
            self.file_manager.cleanup_old_files()

        logger.info("=" * 60)
        logger.info("✅ 清理完成")
        logger.info("=" * 60)

    # ==================== 辅助方法 ====================

    def _gather_news(self, date_str: str, search_config: dict) -> List[NewsItem]:
        """
        采集新闻

        Args:
            date_str: 日期字符串
            search_config: 新闻搜索配置

        Returns:
            新闻列表
        """
        if self.mock_mode:
            return mock_data.create_mock_news_items()
        else:
            # 使用动态配置创建 NewsGatherer
            from modules.exa_news_gatherer import ExaNewsGatherer
            news_gatherer = ExaNewsGatherer(
                api_key=self.exa_api_key,
                search_config=search_config
            )
            return news_gatherer.gather_news(date_str)

    def _extract_title(self, markdown_content: str) -> str:
        """从 Markdown 中提取标题"""
        lines = markdown_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return f"文章 - {datetime.now().strftime('%Y年%m月%d日')}"
