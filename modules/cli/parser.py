#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI 解析器模块
负责命令行参数解析
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器

    Returns:
        配置好的 ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        description='微信编辑器机器人 - 支持多种文章类型和模块化执行',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

完整流程（默认）：
  python wechat_editor_bot.py                                    # 生产模式（默认文章类型）
  python wechat_editor_bot.py --mock                             # Mock 模式（测试）
  python wechat_editor_bot.py --article-type tech_news           # 生成科技资讯

模块化执行：
  python wechat_editor_bot.py search --article-type financial_report --time-range 48
  python wechat_editor_bot.py generate
  python wechat_editor_bot.py convert --theme warm
  python wechat_editor_bot.py weather --location Beijing
  python wechat_editor_bot.py image
  python wechat_editor_bot.py upload
  python wechat_editor_bot.py status
  python wechat_editor_bot.py clean --keep-days 7
        """
    )

    # 添加通用参数
    _add_common_arguments(parser)

    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # 添加各个子命令
    _add_search_subcommand(subparsers)
    _add_generate_subcommand(subparsers)
    _add_convert_subcommand(subparsers)
    _add_weather_subcommand(subparsers)
    _add_image_subcommand(subparsers)
    _add_upload_subcommand(subparsers)
    _add_status_subcommand(subparsers)
    _add_clean_subcommand(subparsers)

    return parser


def _add_common_arguments(parser: argparse.ArgumentParser):
    """添加通用参数（用于完整流程）"""
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


def _add_search_subcommand(subparsers):
    """添加 search 子命令"""
    parser_search = subparsers.add_parser('search', help='搜索新闻')
    parser_search.add_argument('--article-type', help='文章类型')
    parser_search.add_argument('--topic', help='搜索主题（替换模板中的 {topic} 占位符）')
    parser_search.add_argument('--date', help='日期（格式：20260309）')
    parser_search.add_argument('--time-range', type=int, help='时间范围（小时）')
    parser_search.add_argument('--num-results', type=int, help='结果数量')
    parser_search.add_argument('--enable-search', action='store_true', help='强制启用搜索')
    parser_search.add_argument('--output', help='输出文件路径')


def _add_generate_subcommand(subparsers):
    """添加 generate 子命令"""
    parser_generate = subparsers.add_parser('generate', help='生成文章')
    parser_generate.add_argument('--news-file', help='新闻数据文件')
    parser_generate.add_argument('--article-type', help='文章类型')
    parser_generate.add_argument('--topic', help='自定义主题')
    parser_generate.add_argument('--date', help='日期（格式：20260309）')
    parser_generate.add_argument('--output', help='输出文件路径')


def _add_convert_subcommand(subparsers):
    """添加 convert 子命令"""
    parser_convert = subparsers.add_parser('convert', help='转换为微信 HTML')
    parser_convert.add_argument('--input', help='输入 Markdown 文件')
    parser_convert.add_argument('--theme', help='主题样式（warm/cool/professional）')
    parser_convert.add_argument('--date', help='日期（格式：20260309）')
    parser_convert.add_argument('--output', help='输出文件路径')


def _add_weather_subcommand(subparsers):
    """添加 weather 子命令"""
    parser_weather = subparsers.add_parser('weather', help='获取天气信息')
    parser_weather.add_argument('--location', help='位置')
    parser_weather.add_argument('--date', help='日期（格式：20260309）')
    parser_weather.add_argument('--output', help='输出文件路径')


def _add_image_subcommand(subparsers):
    """添加 image 子命令"""
    parser_image = subparsers.add_parser('image', help='生成封面图片')
    parser_image.add_argument('--weather-file', help='天气数据文件')
    parser_image.add_argument('--date', help='日期（格式：20260309）')
    parser_image.add_argument('--output-dir', help='输出目录')


def _add_upload_subcommand(subparsers):
    """添加 upload 子命令"""
    parser_upload = subparsers.add_parser('upload', help='上传到微信')
    parser_upload.add_argument('--html', help='HTML 文件')
    parser_upload.add_argument('--image', help='主图文件')
    parser_upload.add_argument('--secondary-image', help='次图文件')
    parser_upload.add_argument('--title', help='文章标题')
    parser_upload.add_argument('--markdown', help='Markdown 文件（用于提取标题）')
    parser_upload.add_argument('--date', help='日期（格式：20260309）')
    parser_upload.add_argument('--no-create-draft', action='store_true', help='不创建草稿')


def _add_status_subcommand(subparsers):
    """添加 status 子命令"""
    parser_status = subparsers.add_parser('status', help='查看状态')
    parser_status.add_argument('--date', help='日期（格式：20260309）')


def _add_clean_subcommand(subparsers):
    """添加 clean 子命令"""
    parser_clean = subparsers.add_parser('clean', help='清理缓存')
    parser_clean.add_argument('--date', help='清理指定日期的缓存')
    parser_clean.add_argument('--keep-days', type=int, help='保留最近 N 天的文件')
    parser_clean.add_argument('--cache-only', action='store_true', help='只清理缓存')
    parser_clean.add_argument('--output-only', action='store_true', help='只清理输出文件')
