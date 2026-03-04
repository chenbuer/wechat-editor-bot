#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理模块
处理文件保存、清理和归档
"""

import logging
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class FileManager:
    """文件管理器"""

    def __init__(self, config: dict, base_dir: str):
        self.config = config
        self.base_dir = Path(base_dir)
        self.keep_days = config.get('keep_days', 30)
        self.archive_enabled = config.get('archive_enabled', True)

        # 创建目录
        self.articles_dir = self.base_dir / 'output' / 'articles'
        self.html_dir = self.base_dir / 'output' / 'html'
        self.images_dir = self.base_dir / 'output' / 'images'
        self.archive_dir = self.base_dir / 'output' / 'archive'

        self._ensure_directories()

    def _ensure_directories(self):
        """确保目录存在"""
        for directory in [self.articles_dir, self.html_dir, self.images_dir, self.archive_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def save_article(self, content: str, date_str: str, format_type: str) -> str:
        """
        保存文章

        Args:
            content: 文章内容
            date_str: 日期字符串 (YYYYMMDD)
            format_type: 格式类型 ('md' 或 'html')

        Returns:
            保存的文件路径
        """
        if format_type == 'md':
            file_path = self.articles_dir / f"finance-news-{date_str}.md"
        elif format_type == 'html':
            file_path = self.html_dir / f"finance-news-{date_str}.html"
        else:
            raise ValueError(f"不支持的格式: {format_type}")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"文章已保存: {file_path}")
        return str(file_path)

    def save_image(self, image_data: bytes, date_str: str, image_type: str = 'primary') -> str:
        """
        保存图片

        Args:
            image_data: 图片字节数据
            date_str: 日期字符串 (YYYYMMDD)
            image_type: 图片类型 ('primary' 或 'secondary')

        Returns:
            保存的文件路径
        """
        file_path = self.images_dir / f"cover-{date_str}-{image_type}.jpg"

        with open(file_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"图片已保存: {file_path}")
        return str(file_path)

    def cleanup_old_files(self):
        """清理旧文件"""
        logger.info(f"开始清理 {self.keep_days} 天前的文件")

        cutoff_date = datetime.now() - timedelta(days=self.keep_days)
        cleaned_count = 0

        for directory in [self.articles_dir, self.html_dir, self.images_dir]:
            for file_path in directory.glob('*'):
                if not file_path.is_file():
                    continue

                # 检查文件修改时间
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    if self.archive_enabled:
                        self._archive_file(file_path)
                    else:
                        file_path.unlink()
                    cleaned_count += 1

        logger.info(f"清理完成，处理了 {cleaned_count} 个文件")

    def _archive_file(self, file_path: Path):
        """归档文件"""
        # 创建归档子目录（按年月）
        archive_subdir = self.archive_dir / datetime.now().strftime('%Y-%m')
        archive_subdir.mkdir(parents=True, exist_ok=True)

        # 移动文件
        dest_path = archive_subdir / file_path.name
        shutil.move(str(file_path), str(dest_path))
        logger.debug(f"文件已归档: {file_path.name} -> {dest_path}")

    def get_latest_article(self, format_type: str = 'md') -> Optional[str]:
        """
        获取最新文章路径

        Args:
            format_type: 格式类型 ('md' 或 'html')

        Returns:
            文件路径或 None
        """
        if format_type == 'md':
            directory = self.articles_dir
            pattern = 'finance-news-*.md'
        else:
            directory = self.html_dir
            pattern = 'finance-news-*.html'

        files = sorted(directory.glob(pattern), reverse=True)
        if files:
            return str(files[0])
        return None
