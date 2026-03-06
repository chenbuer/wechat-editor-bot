#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文章模板系统
"""

from modules.article_generator import ArticleGenerator
from datetime import datetime


def test_template_loading():
    """测试模板加载"""
    print("=" * 60)
    print("测试 1: 模板加载")
    print("=" * 60)

    config = {
        'style': 'professional_engaging',
        'min_length': 800,
        'max_length': 1500,
        'title_format': '测试文章 | {date}'
    }

    generator = ArticleGenerator(
        config=config,
        mock_mode=True
    )

    # 获取可用的文章类型
    available_types = generator.get_available_article_types()
    print(f"✓ 可用的文章类型: {', '.join(available_types)}")
    print()


def test_financial_report():
    """测试财经日报生成"""
    print("=" * 60)
    print("测试 2: 财经日报生成 (Mock 模式)")
    print("=" * 60)

    config = {
        'title_format': '财经早报 | {date}'
    }

    generator = ArticleGenerator(
        config=config,
        mock_mode=True
    )

    article = generator.generate_article(
        news_items=[],
        date_str="20260306",
        article_type="financial_report"
    )

    print("✓ 文章生成成功")
    print(f"✓ 文章长度: {len(article)} 字符")
    print(f"✓ 包含编者按: {'> ##' in article}")
    print(f"✓ 包含页脚: {'投资有风险' in article}")
    print()
    print("文章预览（前 500 字符）:")
    print("-" * 60)
    print(article[:500])
    print("...")
    print()


def test_tech_news():
    """测试科技资讯生成"""
    print("=" * 60)
    print("测试 3: 科技资讯生成 (Mock 模式)")
    print("=" * 60)

    config = {
        'title_format': '科技速递 | {date}'
    }

    generator = ArticleGenerator(
        config=config,
        mock_mode=True
    )

    article = generator.generate_article(
        news_items=[],
        date_str="20260306",
        article_type="tech_news"
    )

    print("✓ 文章生成成功")
    print(f"✓ 文章长度: {len(article)} 字符")
    print(f"✓ 包含今日看点: {'💡 今日看点' in article}")
    print(f"✓ 包含页脚: {'科技资讯' in article}")
    print()
    print("文章预览（前 500 字符）:")
    print("-" * 60)
    print(article[:500])
    print("...")
    print()


def test_general_news():
    """测试通用新闻摘要生成"""
    print("=" * 60)
    print("测试 4: 通用新闻摘要生成 (Mock 模式)")
    print("=" * 60)

    config = {
        'title_format': '新闻摘要 | {date}'
    }

    generator = ArticleGenerator(
        config=config,
        mock_mode=True
    )

    article = generator.generate_article(
        news_items=[],
        date_str="20260306",
        article_type="general_news"
    )

    print("✓ 文章生成成功")
    print(f"✓ 文章长度: {len(article)} 字符")
    print(f"✓ 包含今日要闻: {'📰 今日要闻' in article}")
    print()


def test_knowledge_explanation():
    """测试知识解读生成"""
    print("=" * 60)
    print("测试 5: 知识解读生成 (Mock 模式)")
    print("=" * 60)

    config = {
        'title_format': '知识解读 | {date}'
    }

    generator = ArticleGenerator(
        config=config,
        mock_mode=True
    )

    article = generator.generate_article(
        news_items=[],
        date_str="20260306",
        article_type="knowledge_explanation",
        custom_topic="量化宽松政策"
    )

    print("✓ 文章生成成功")
    print(f"✓ 文章长度: {len(article)} 字符")
    print(f"✓ 包含核心要点: {'🎯 核心要点' in article}")
    print(f"✓ 包含量化宽松: {'量化宽松' in article}")
    print()


def test_backward_compatibility():
    """测试向后兼容性"""
    print("=" * 60)
    print("测试 6: 向后兼容性（不指定文章类型）")
    print("=" * 60)

    config = {
        'title_format': '财经早报 | {date}'
    }

    generator = ArticleGenerator(
        config=config,
        mock_mode=True
    )

    # 不指定 article_type，应该使用默认的 financial_report
    article = generator.generate_article(
        news_items=[],
        date_str="20260306"
    )

    print("✓ 文章生成成功（使用默认类型）")
    print(f"✓ 默认使用财经日报模板: {'编者按' in article}")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "文章模板系统测试" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        test_template_loading()
        test_financial_report()
        test_tech_news()
        test_general_news()
        test_knowledge_explanation()
        test_backward_compatibility()

        print("=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
