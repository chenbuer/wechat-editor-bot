#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令分发器模块
负责将命令行参数路由到相应的命令处理器
"""

import argparse
from modules.bot.commands import BotCommands
from modules.bot.pipeline import WorkflowPipeline


class CommandDispatcher:
    """命令分发器 - 路由命令到对应的处理器"""

    def __init__(self, commands: BotCommands, pipeline: WorkflowPipeline):
        """
        初始化命令分发器

        Args:
            commands: 命令处理器实例
            pipeline: 工作流管道实例
        """
        self.commands = commands
        self.pipeline = pipeline

    def dispatch(self, args: argparse.Namespace):
        """
        分发命令到对应的处理器

        Args:
            args: 解析后的命令行参数
        """
        if args.command == 'search':
            self.commands.search(
                article_type=args.article_type,
                topic=args.topic,
                date_str=args.date,
                time_range=args.time_range,
                num_results=args.num_results,
                enable_search=args.enable_search,
                output=args.output
            )
        elif args.command == 'generate':
            self.commands.generate(
                news_file=args.news_file,
                article_type=args.article_type,
                topic=args.topic,
                date_str=args.date,
                output=args.output
            )
        elif args.command == 'convert':
            self.commands.convert(
                input_file=args.input,
                theme=args.theme,
                date_str=args.date,
                output=args.output
            )
        elif args.command == 'weather':
            self.commands.weather(
                location=args.location,
                date_str=args.date,
                output=args.output
            )
        elif args.command == 'image':
            self.commands.image(
                weather_file=args.weather_file,
                date_str=args.date,
                output_dir=args.output_dir
            )
        elif args.command == 'upload':
            self.commands.upload(
                html_file=args.html,
                image_file=args.image,
                secondary_image_file=args.secondary_image,
                title=args.title,
                markdown_file=args.markdown,
                date_str=args.date,
                create_draft=not args.no_create_draft
            )
        elif args.command == 'status':
            self.commands.status(date_str=args.date)
        elif args.command == 'clean':
            self.commands.clean(
                date_str=args.date,
                keep_days=args.keep_days,
                cache_only=args.cache_only,
                output_only=args.output_only
            )
        else:
            # 无子命令，执行完整流程
            self.pipeline.run(article_type=args.article_type, custom_topic=args.topic)
