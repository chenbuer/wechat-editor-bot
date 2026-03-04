#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文章生成和 Markdown 转 HTML
只测试核心功能，不涉及新闻采集、图片生成、微信发布等
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
import yaml
from pathlib import Path
from datetime import datetime

from modules.news_gatherer import NewsGatherer, NewsItem
from modules.article_generator import ArticleGenerator
from modules.markdown_converter import convert_markdown_to_html

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_secrets(secrets_path: str) -> dict:
    """加载 secrets 配置"""
    try:
        with open(secrets_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.warning(f"加载 secrets 失败: {e}")
        return {}


def main():
    """主函数"""
    # 加载配置
    config_path = Path(__file__).parent.parent / 'config' / 'finance_news_config.yaml'
    secrets_path = Path(__file__).parent.parent / 'config' / 'secrets.yaml'

    config = load_config(str(config_path))
    secrets = load_secrets(str(secrets_path))

    date_str = datetime.now().strftime('%Y%m%d')

    # 获取 API 配置
    api_config = secrets.get('api', {})
    deepseek_key = api_config.get('deepseek_key')
    deepseek_base_url = api_config.get('deepseek_base_url', 'https://api.deepseek.com')
    deepseek_model = api_config.get('deepseek_model', 'deepseek-chat')
    exa_api_key = api_config.get('exa_api_key')

    if not deepseek_key:
        logger.error("未配置 DeepSeek API Key")
        return

    if not exa_api_key:
        logger.error("未配置 Exa API Key")
        return

    # 初始化新闻采集器 - 使用 Exa API
    logger.info("\n[步骤 1/3] 采集真实新闻（Exa API）")
    news_gatherer = NewsGatherer(
        config['news'],
        exa_api_key=exa_api_key,
        ai_api_key=deepseek_key,
        ai_base_url=deepseek_base_url,
        ai_model=deepseek_model
    )

    # 采集真实新闻
    news_items = news_gatherer.gather_news(date_str)
    logger.info(f"✅ 采集到 {len(news_items)} 条新闻")

    # 准备文章生成器配置
    article_config = config['article'].copy()

    # 初始化文章生成器
    logger.info("\n[步骤 2/4] 生成文章")
    article_generator = ArticleGenerator(
        article_config,
        api_key=deepseek_key,
        ai_provider="openai",
        api_base_url=deepseek_base_url,
        model_name=deepseek_model,
        mock_mode=False
    )

    # 生成文章
    article_md = article_generator.generate_article(news_items, date_str)

    # 保存 Markdown
    output_dir = Path(__file__).parent / 'output' / 'test'
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / f'test-article-{date_str}.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(article_md)
    logger.info(f"✅ Markdown 已保存: {md_path}")

    # 2. 转换为微信 HTML
    logger.info("\n[步骤 3/4] 转换为微信 HTML")
    html_path = output_dir / f'test-article-{date_str}.html'
    article_html = convert_markdown_to_html(
        str(md_path),
        output_file=str(html_path),
        theme='ocean'
    )
    logger.info(f"✅ HTML 已保存: {html_path}")

    # 3. 输出结果
    logger.info("\n" + "=" * 60)
    logger.info("✅ 测试完成")
    logger.info(f"采集新闻: {len(news_items)} 条")
    logger.info(f"Markdown: {md_path}")
    logger.info(f"HTML: {html_path}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
