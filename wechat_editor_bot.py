#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信编辑器机器人
支持多种文章类型的通用内容生成平台
"""

import logging
import sys
import os
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.news_gatherer import NewsGatherer, NewsItem
from modules.article_generator import ArticleGenerator
from modules.weather_service import WeatherService
from modules.image_generator import ImageGenerator
from modules.wechat_publisher import WeChatPublisher
from modules.file_manager import FileManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('wechat_editor_bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


class WeChatEditorBot:
    """微信编辑器机器人 - 支持多种文章类型"""

    def __init__(self, config_path: str, secrets_path: str = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.config = self._load_config(config_path)

        # 加载 secrets 配置
        if secrets_path is None:
            secrets_path = Path(__file__).parent / 'config' / 'secrets.yaml'
        self.secrets = self._load_secrets(secrets_path)

        # 获取 API 配置
        api_config = self.secrets.get('api', {})
        self.deepseek_key = api_config.get('deepseek_key')
        self.deepseek_base_url = api_config.get('deepseek_base_url', 'https://api.deepseek.com')
        self.deepseek_model = api_config.get('deepseek_model', 'deepseek-chat')
        self.exa_api_key = api_config.get('exa_api_key')

        # 准备文章生成器配置
        article_config = self.config['article'].copy()

        # 文章生成器 - 优先使用 DeepSeek，fallback 到 Anthropic
        if self.deepseek_key:
            logger.info("使用 DeepSeek API 生成文章")
            self.article_generator = ArticleGenerator(
                article_config,
                api_key=self.deepseek_key,
                ai_provider="openai",
                api_base_url=self.deepseek_base_url,
                model_name=self.deepseek_model,
                mock_mode=mock_mode
            )
        else:
            logger.info("DeepSeek 未配置，使用 Anthropic API")
            anthropic_key = api_config.get('anthropic_key') or os.getenv('ANTHROPIC_API_KEY')
            self.article_generator = ArticleGenerator(
                article_config,
                api_key=anthropic_key,
                ai_provider="anthropic",
                model_name="claude-3-5-sonnet-20241022",
                mock_mode=mock_mode
            )

        # 天气服务
        weather_config = self.config.get('weather', {})
        location = weather_config.get('location', 'Nanjing')
        self.weather_service = WeatherService(
            location=location,
            ai_api_key=self.deepseek_key,
            ai_base_url=self.deepseek_base_url,
            ai_model=self.deepseek_model
        )

        # 图片生成器
        image_config = {
            'provider': self.secrets.get('api', {}).get('image_provider', 'tuzi'),
            'api_key': self.secrets.get('api', {}).get('image_key') or os.getenv('IMAGE_API_KEY'),
            'api_base': self.secrets.get('api', {}).get('image_base_url', 'https://api.tu-zi.com/v1'),
            'model': self.secrets.get('api', {}).get('image_model', 'doubao-seedream-4-5-251128')
        }
        self.image_generator = ImageGenerator(self.config['image'], image_config)

        # 微信发布器
        wechat_config = {
            'appid': self.secrets.get('wechat', {}).get('appid'),
            'secret': self.secrets.get('wechat', {}).get('secret'),
            'theme': self.config.get('wechat', {}).get('theme', 'warm'),
            'author': self.config.get('wechat', {}).get('author', ''),
            'enable_comment': self.config.get('wechat', {}).get('enable_comment', False),
            'only_fans_comment': self.config.get('wechat', {}).get('only_fans_comment', False)
        }
        self.wechat_publisher = WeChatPublisher(wechat_config)

        self.file_manager = FileManager(
            self.config['cleanup'],
            str(Path(__file__).parent)
        )

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_secrets(self, secrets_path) -> dict:
        """加载 secrets 配置文件"""
        secrets_path = Path(secrets_path)
        if not secrets_path.exists():
            logger.warning(f"Secrets 配置文件不存在: {secrets_path}")
            logger.warning("将使用环境变量或默认值")
            return {}

        try:
            with open(secrets_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    logger.warning("Secrets 配置文件为空")
                    return {}
                secrets = yaml.safe_load(content) or {}
                logger.info("✅ Secrets 配置加载成功")
                return secrets
        except Exception as e:
            logger.error(f"加载 secrets 配置失败: {e}")
            return {}

    def run(self, article_type: str = None, custom_topic: str = None):
        """
        运行主流程

        Args:
            article_type: 文章类型（如不指定则使用配置中的默认值）
            custom_topic: 自定义主题（用于知识解读类文章）
        """
        # 确定文章类型
        article_type = article_type or self.config['article'].get('article_type', 'financial_report')

        logger.info("=" * 60)
        logger.info("微信编辑器机器人启动")
        logger.info(f"模式: {'Mock' if self.mock_mode else 'Production'}")
        logger.info(f"文章类型: {article_type}")
        if custom_topic:
            logger.info(f"自定义主题: {custom_topic}")
        logger.info("=" * 60)

        date_str = datetime.now().strftime('%Y%m%d')

        try:
            # 1. 获取新闻搜索配置
            search_config = self.article_generator.get_news_search_config(article_type, custom_topic)

            # 2. 如果需要搜索新闻，则采集新闻
            news_items = []
            if search_config:
                logger.info(f"\n[步骤 1/7] 采集新闻（类型: {article_type}）")
                news_items = self._gather_news(date_str, search_config)
            else:
                logger.info(f"\n[步骤 1/7] 跳过新闻采集（文章类型 {article_type} 不需要新闻）")

            # 3. 生成文章
            logger.info("\n[步骤 2/7] 生成文章")
            article_md = self.article_generator.generate_article(
                news_items=news_items,
                date_str=date_str,
                article_type=article_type,
                custom_topic=custom_topic
            )
            md_path = self.file_manager.save_article(article_md, date_str, 'md', article_type)

            # 4. 转换为微信 HTML
            logger.info("\n[步骤 3/7] 转换为微信 HTML")
            theme = self.config.get('wechat', {}).get('theme', 'warm')
            article_html = self.wechat_publisher.convert_to_wechat_html(
                article_md, theme=theme
            )
            html_path = self.file_manager.save_article(article_html, date_str, 'html', article_type)

            # 5. 获取天气信息
            logger.info("\n[步骤 4/7] 获取天气信息")
            if self.mock_mode:
                weather_data = {
                    'condition': 'Clear',
                    'temperature': '20',
                    'time_of_day': 'morning',
                    'location': 'Nanjing'
                }
                logger.info("Mock 模式: 使用默认天气数据")
            else:
                weather_data = self.weather_service.get_current_weather()

            # 6. 生成封面图片
            logger.info("\n[步骤 5/7] 生成封面图片")
            if self.mock_mode:
                from PIL import Image, ImageDraw
                from io import BytesIO

                # 主图
                img = Image.new('RGB', (900, 383), color=(73, 109, 137))
                d = ImageDraw.Draw(img)
                text = f"Mock Cover Image\n{date_str}\n{weather_data.get('condition', 'Clear')} {weather_data.get('temperature', '20')}°C"
                d.text((450, 191), text, fill=(255, 255, 255), anchor="mm")
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                cover_image = buffer.getvalue()

                # 次图
                img_secondary = Image.new('RGB', (500, 500), color=(109, 137, 73))
                d_secondary = ImageDraw.Draw(img_secondary)
                text_secondary = f"Mock Secondary\n{date_str}"
                d_secondary.text((250, 250), text_secondary, fill=(255, 255, 255), anchor="mm")
                buffer_secondary = BytesIO()
                img_secondary.save(buffer_secondary, format='JPEG', quality=85)
                secondary_image = buffer_secondary.getvalue()
            else:
                cover_image = self.image_generator.generate_cover_image(
                    weather_data, size=self.config['image']['primary_size']
                )
                secondary_image = self.image_generator.generate_cover_image(
                    weather_data, size=self.config['image']['secondary_size']
                )

            image_path = self.file_manager.save_image(cover_image, date_str, 'primary')
            secondary_image_path = self.file_manager.save_image(secondary_image, date_str, 'secondary')

            # 7. 上传到微信
            if not self.mock_mode and self.config['wechat']['create_draft']:
                logger.info("\n[步骤 6/7] 上传到微信")
                media_id = self.wechat_publisher.upload_image(image_path)
                secondary_media_id = self.wechat_publisher.upload_image(secondary_image_path)

                # 8. 创建草稿
                logger.info("\n[步骤 7/7] 创建草稿")
                title = self._extract_title(article_md)
                draft_media_id = self.wechat_publisher.create_draft(
                    title, article_html, media_id, secondary_media_id
                )

                logger.info("\n" + "=" * 60)
                logger.info(f"✅ 草稿创建成功: {draft_media_id}")
                logger.info("请在微信公众号后台审核并发布")
                logger.info("=" * 60)
            else:
                logger.info("\n[步骤 6-7/7] 跳过微信上传（Mock 模式）")
                logger.info("\n" + "=" * 60)
                logger.info("✅ Mock 模式运行成功")
                logger.info(f"文章: {md_path}")
                logger.info(f"HTML: {html_path}")
                logger.info(f"主图: {image_path}")
                logger.info(f"次图: {secondary_image_path}")
                logger.info("=" * 60)

            # 9. 清理旧文件
            logger.info("\n[清理] 清理旧文件")
            self.file_manager.cleanup_old_files()

        except Exception as e:
            logger.error(f"\n❌ 运行失败: {e}", exc_info=True)
            raise

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
            # Mock 数据
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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='微信编辑器机器人 - 支持多种文章类型',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python wechat_editor_bot.py                                    # 生产模式（默认文章类型）
  python wechat_editor_bot.py --mock                             # Mock 模式（测试）
  python wechat_editor_bot.py --article-type tech_news           # 生成科技资讯
  python wechat_editor_bot.py --article-type knowledge_explanation --topic "量化宽松"  # 知识解读
  python wechat_editor_bot.py --config custom.yaml               # 自定义配置
        """
    )

    parser.add_argument(
        '--config',
        default='config/wechat_bot_config.yaml',
        help='配置文件路径（默认: config/wechat_bot_config.yaml）'
    )
    parser.add_argument(
        '--secrets',
        default='config/secrets.yaml',
        help='Secrets 配置文件路径（默认: config/secrets.yaml）'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Mock 模式（不调用真实 API）'
    )
    parser.add_argument(
        '--article-type',
        help='文章类型（financial_report, tech_news, general_news, knowledge_explanation）'
    )
    parser.add_argument(
        '--topic',
        help='自定义主题（用于知识解读类文章）'
    )

    args = parser.parse_args()

    # 检查配置文件
    config_path = Path(__file__).parent / args.config
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        sys.exit(1)

    secrets_path = Path(__file__).parent / args.secrets
    if not secrets_path.exists() and not args.mock:
        logger.warning(f"⚠️  Secrets 配置文件不存在: {secrets_path}")
        logger.warning("将使用环境变量或 Mock 模式")
        logger.warning("提示: 复制 config/secrets.yaml.template 为 config/secrets.yaml 并填入真实值")

    # 运行机器人
    bot = WeChatEditorBot(str(config_path), str(secrets_path), mock_mode=args.mock)
    bot.run(article_type=args.article_type, custom_topic=args.topic)


if __name__ == '__main__':
    main()
