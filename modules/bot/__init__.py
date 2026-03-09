#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot 模块
包含机器人的核心功能
"""

from .config import BotConfig, ServiceFactory
from .commands import BotCommands
from .pipeline import WorkflowPipeline
from .mock_data import (
    create_mock_news_items,
    create_mock_weather_data,
    create_mock_cover_image,
    create_mock_secondary_image
)

__all__ = [
    'BotConfig',
    'ServiceFactory',
    'BotCommands',
    'WorkflowPipeline',
    'create_mock_news_items',
    'create_mock_weather_data',
    'create_mock_cover_image',
    'create_mock_secondary_image',
]
