#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载配置文件和创建服务实例
"""

import os
import logging
import yaml
from pathlib import Path
from typing import Optional

from modules.article_generator import ArticleGenerator
from modules.weather_service import WeatherService
from modules.image_generator import ImageGenerator
from modules.wechat_publisher import WeChatPublisher
from modules.file_manager import FileManager
from modules.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class BotConfig:
    """配置管理器 - 负责加载配置文件"""

    def __init__(self, config_path: str, secrets_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 主配置文件路径
            secrets_path: Secrets 配置文件路径（可选）
        """
        self.config_path = config_path
        self.secrets_path = secrets_path or str(Path(config_path).parent / 'secrets.yaml')

        self.config = self._load_config()
        self.secrets = self._load_secrets()

    def _load_config(self) -> dict:
        """加载主配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_secrets(self) -> dict:
        """加载 secrets 配置文件"""
        secrets_path = Path(self.secrets_path)
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

    def get_api_config(self) -> dict:
        """获取 API 配置"""
        return self.secrets.get('api', {})

    def get_wechat_config(self) -> dict:
        """获取微信配置"""
        return {
            'appid': self.secrets.get('wechat', {}).get('appid'),
            'secret': self.secrets.get('wechat', {}).get('secret'),
            'theme': self.config.get('wechat', {}).get('theme', 'warm'),
            'author': self.config.get('wechat', {}).get('author', ''),
            'enable_comment': self.config.get('wechat', {}).get('enable_comment', False),
            'only_fans_comment': self.config.get('wechat', {}).get('only_fans_comment', False)
        }


class ServiceFactory:
    """服务工厂 - 负责创建和管理所有服务实例"""

    def __init__(self, bot_config: BotConfig, mock_mode: bool = False):
        """
        初始化服务工厂

        Args:
            bot_config: 配置管理器实例
            mock_mode: 是否为 Mock 模式
        """
        self.config = bot_config.config
        self.secrets = bot_config.secrets
        self.mock_mode = mock_mode

        # 获取 API 配置
        api_config = bot_config.get_api_config()
        self.deepseek_key = api_config.get('deepseek_key')
        self.deepseek_base_url = api_config.get('deepseek_base_url', 'https://api.deepseek.com')
        self.deepseek_model = api_config.get('deepseek_model', 'deepseek-chat')
        self.exa_api_key = api_config.get('exa_api_key')

        # 创建所有服务实例
        self.article_generator = self._create_article_generator()
        self.weather_service = self._create_weather_service()
        self.image_generator = self._create_image_generator()
        self.wechat_publisher = self._create_wechat_publisher(bot_config)
        self.file_manager = self._create_file_manager()
        self.cache_manager = self._create_cache_manager()

    def _create_article_generator(self) -> ArticleGenerator:
        """创建文章生成器"""
        article_config = self.config['article'].copy()

        # 优先使用 DeepSeek，fallback 到 Anthropic
        if self.deepseek_key:
            logger.info("使用 DeepSeek API 生成文章")
            return ArticleGenerator(
                article_config,
                api_key=self.deepseek_key,
                ai_provider="openai",
                api_base_url=self.deepseek_base_url,
                model_name=self.deepseek_model,
                mock_mode=self.mock_mode
            )
        else:
            logger.info("DeepSeek 未配置，使用 Anthropic API")
            anthropic_key = self.secrets.get('api', {}).get('anthropic_key') or os.getenv('ANTHROPIC_API_KEY')
            return ArticleGenerator(
                article_config,
                api_key=anthropic_key,
                ai_provider="anthropic",
                model_name="claude-3-5-sonnet-20241022",
                mock_mode=self.mock_mode
            )

    def _create_weather_service(self) -> WeatherService:
        """创建天气服务"""
        weather_config = self.config.get('weather', {})
        location = weather_config.get('location', 'Nanjing')
        return WeatherService(
            location=location,
            ai_api_key=self.deepseek_key,
            ai_base_url=self.deepseek_base_url,
            ai_model=self.deepseek_model
        )

    def _create_image_generator(self) -> ImageGenerator:
        """创建图片生成器"""
        image_config = {
            'provider': self.secrets.get('api', {}).get('image_provider', 'tuzi'),
            'api_key': self.secrets.get('api', {}).get('image_key') or os.getenv('IMAGE_API_KEY'),
            'api_base': self.secrets.get('api', {}).get('image_base_url', 'https://api.tu-zi.com/v1'),
            'model': self.secrets.get('api', {}).get('image_model', 'doubao-seedream-4-5-251128')
        }
        return ImageGenerator(self.config['image'], image_config)

    def _create_wechat_publisher(self, bot_config: BotConfig) -> WeChatPublisher:
        """创建微信发布器"""
        wechat_config = bot_config.get_wechat_config()
        return WeChatPublisher(wechat_config)

    def _create_file_manager(self) -> FileManager:
        """创建文件管理器"""
        # 获取项目根目录
        project_root = str(Path(__file__).parent.parent.parent)
        return FileManager(self.config['cleanup'], project_root)

    def _create_cache_manager(self) -> CacheManager:
        """创建缓存管理器"""
        return CacheManager()
