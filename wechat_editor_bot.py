#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信编辑器机器人 - 主入口
支持多种文章类型的通用内容生成平台
支持模块化执行：可以单独执行各个步骤，也可以一键运行完整流程
"""

import sys
import logging
from pathlib import Path

from modules.bot.config import BotConfig, ServiceFactory
from modules.bot.commands import BotCommands
from modules.bot.pipeline import WorkflowPipeline
from modules.cli.parser import create_parser
from modules.cli.dispatcher import CommandDispatcher

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


def main():
    """主函数"""
    # 解析命令行参数
    parser = create_parser()
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

    # 初始化配置和服务
    config = BotConfig(str(config_path), str(secrets_path))
    services = ServiceFactory(config, mock_mode=args.mock)

    # 创建命令处理器和工作流管道
    commands = BotCommands(services)
    pipeline = WorkflowPipeline(services, commands)

    # 分发命令
    dispatcher = CommandDispatcher(commands, pipeline)
    try:
        dispatcher.dispatch(args)
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
