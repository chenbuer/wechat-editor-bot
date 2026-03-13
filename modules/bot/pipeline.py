#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流程编排模块
负责完整工作流的执行
"""

import logging
from datetime import datetime
from typing import Optional

from modules.bot.config import ServiceFactory
from modules.bot.commands import BotCommands
from modules.bot import mock_data

logger = logging.getLogger(__name__)


class WorkflowPipeline:
    """工作流管道 - 编排完整的 7 步流程"""

    def __init__(self, services: ServiceFactory, commands: BotCommands):
        """
        初始化工作流管道

        Args:
            services: 服务工厂实例
            commands: 命令处理器实例
        """
        self.services = services
        self.commands = commands
        self.config = services.config
        self.mock_mode = services.mock_mode

    def run(self, article_type: Optional[str] = None, custom_topic: Optional[str] = None, time_range: Optional[int] = None):
        """
        运行完整流程

        Args:
            article_type: 文章类型（如不指定则使用配置中的默认值）
            custom_topic: 自定义主题（用于知识解读类文章）
            time_range: 新闻搜索时间范围（小时），覆盖配置文件中的设置
        """
        # 确定文章类型
        article_type = article_type or self.config['article'].get('article_type', 'financial_report')

        logger.info("=" * 60)
        logger.info("微信编辑器机器人启动")
        logger.info(f"模式: {'Mock' if self.mock_mode else 'Production'}")
        logger.info(f"文章类型: {article_type}")
        if custom_topic:
            logger.info(f"自定义主题: {custom_topic}")
        if time_range is not None:
            logger.info(f"时间范围: {time_range} 小时（命令行覆盖）")
        logger.info("=" * 60)

        date_str = datetime.now().strftime('%Y%m%d')

        try:
            # 1. 获取新闻搜索配置
            search_config = self.services.article_generator.get_news_search_config(article_type, custom_topic)

            # 如果命令行指定了 time_range，覆盖配置文件中的值
            if search_config and time_range is not None:
                search_config['time_range'] = time_range
                logger.info(f"时间范围已覆盖为: {time_range} 小时")

            # 2. 如果需要搜索新闻，则采集新闻
            news_items = []
            if search_config:
                logger.info(f"\n[步骤 1/7] 采集新闻（类型: {article_type}）")
                news_items = self.commands._gather_news(date_str, search_config)
                self.services.cache_manager.save_news(date_str, news_items)
            else:
                logger.info(f"\n[步骤 1/7] 跳过新闻采集（文章类型 {article_type} 不需要新闻）")

            # 3. 生成文章
            logger.info("\n[步骤 2/7] 生成文章")
            article_md = self.services.article_generator.generate_article(
                news_items=news_items,
                date_str=date_str,
                article_type=article_type,
                custom_topic=custom_topic
            )
            md_path = self.services.file_manager.save_article(article_md, date_str, 'md', article_type)
            title = self.commands._extract_title(article_md)
            self.services.cache_manager.save_article_meta(date_str, article_type, str(md_path), title, custom_topic)

            # 4. 转换为微信 HTML
            logger.info("\n[步骤 3/7] 转换为微信 HTML")
            theme = self.config.get('wechat', {}).get('theme', 'warm')
            article_html = self.services.wechat_publisher.convert_to_wechat_html(
                article_md, theme=theme
            )
            html_path = self.services.file_manager.save_article(article_html, date_str, 'html', article_type)
            self.services.cache_manager.save_html_meta(date_str, str(html_path))

            # 5. 获取天气信息
            logger.info("\n[步骤 4/7] 获取天气信息")
            if self.mock_mode:
                weather_data = mock_data.create_mock_weather_data()
                logger.info("Mock 模式: 使用默认天气数据")
            else:
                weather_data = self.services.weather_service.get_current_weather()
            self.services.cache_manager.save_weather(date_str, weather_data)

            # 6. 生成封面图片
            logger.info("\n[步骤 5/7] 生成封面图片")
            if self.mock_mode:
                cover_image = mock_data.create_mock_cover_image(
                    date_str, weather_data, self.config['image']['primary_size']
                )
            else:
                cover_image = self.services.image_generator.generate_cover_image(
                    weather_data, size=self.config['image']['primary_size']
                )

            image_path = self.services.file_manager.save_image(cover_image, date_str, 'primary')
            self.services.cache_manager.save_images_meta(date_str, str(image_path), None)

            # 7. 上传到微信
            if not self.mock_mode and self.config['wechat']['create_draft']:
                logger.info("\n[步骤 6/7] 上传到微信")
                media_id = self.services.wechat_publisher.upload_image(image_path)

                # 更新缓存
                self.services.cache_manager.save_images_meta(
                    date_str, str(image_path), None,
                    media_id, None
                )

                # 8. 创建草稿
                logger.info("\n[步骤 7/7] 创建草稿")
                draft_media_id = self.services.wechat_publisher.create_draft(
                    title, article_html, media_id
                )

                logger.info("\n" + "=" * 60)
                logger.info(f"✅ 草稿创建成功: {draft_media_id}")
                logger.info("请在微信公众号后台审核并发布")
                logger.info("=" * 60)
            else:
                logger.info("\n[步骤 6-7/7] 跳过微信上传（Mock 模式）")
                logger.info("\n" + "=" * 60)
                logger.info("✅ Mock 模式运行成功")
                logger.debug(f"文章: {md_path}")
                logger.debug(f"HTML: {html_path}")
                logger.debug(f"封面图: {image_path}")
                logger.info("=" * 60)

            # 9. 清理旧文件
            logger.info("\n[清理] 清理旧文件")
            self.services.file_manager.cleanup_old_files()

        except Exception as e:
            logger.error(f"\n❌ 运行失败: {e}", exc_info=True)
            raise
