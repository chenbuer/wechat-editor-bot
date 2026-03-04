#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信发布模块
处理微信 API 交互
"""

import logging
import requests
import json
import time
import os
import sys
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class WeChatPublisher:
    """微信发布器"""

    def __init__(self, wechat_config: dict):
        self.appid = wechat_config.get('appid')
        self.secret = wechat_config.get('secret')
        self.theme = wechat_config.get('theme', 'ocean')
        self.author = wechat_config.get('author', '')
        self.enable_comment = wechat_config.get('enable_comment', False)
        self.only_fans_comment = wechat_config.get('only_fans_comment', False)
        self.access_token = None
        self.token_expires_at = 0

        if not self.appid or not self.secret:
            raise ValueError("未配置微信 AppID 和 Secret")

    def get_access_token(self) -> str:
        """
        获取 access_token（带缓存和自动刷新）

        Returns:
            access_token
        """
        # 检查缓存是否有效（提前 5 分钟刷新）
        if self.access_token and time.time() < (self.token_expires_at - 300):
            return self.access_token

        logger.info("获取新的 access_token")

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if 'access_token' not in data:
            raise Exception(f"获取 access_token 失败: {data}")

        self.access_token = data['access_token']
        self.token_expires_at = time.time() + data.get('expires_in', 7200)

        logger.info("access_token 获取成功")
        return self.access_token

    def upload_image(self, image_path: str) -> str:
        """
        上传图片到微信

        Args:
            image_path: 图片文件路径

        Returns:
            media_id
        """
        logger.info(f"上传图片: {image_path}")

        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"

        with open(image_path, 'rb') as f:
            files = {'media': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(url, files=files, timeout=30)

        response.raise_for_status()
        data = response.json()

        if 'media_id' not in data:
            raise Exception(f"上传图片失败: {data}")

        media_id = data['media_id']
        logger.info(f"图片上传成功: {self._mask_media_id(media_id)}")

        return media_id

    def create_draft(self, title: str, content_html: str, cover_media_id: str,
                     secondary_media_id: str = None) -> str:
        """
        创建草稿

        Args:
            title: 文章标题
            content_html: 文章 HTML 内容
            cover_media_id: 封面图片 media_id
            secondary_media_id: 次图 media_id（可选）

        Returns:
            draft_media_id
        """
        logger.info(f"创建草稿: {title}")

        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

        # content_html 已经是微信格式（仅 body 内容）
        # 生成摘要
        digest = self._generate_digest(content_html)
        logger.info(f"摘要长度: {len(digest)} 字符")
        logger.debug(f"摘要内容: {digest}")

        articles = [{
            "title": title,
            "digest": digest,
            "content": content_html,
            "content_source_url": "",
            "thumb_media_id": cover_media_id,
            "need_open_comment": 1 if self.enable_comment else 0,
            "only_fans_can_comment": 1 if self.only_fans_comment else 0
        }]

        # 如果配置了 author，则添加
        if self.author:
            articles[0]["author"] = self.author

        # 如果有次图，则添加
        if secondary_media_id:
            articles[0]["thumb_media_id"] = secondary_media_id
            logger.info(f"使用次图: {self._mask_media_id(secondary_media_id)}")

        payload = {"articles": articles}

        # 手动序列化 JSON，确保中文不被转义
        import json
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.post(url, data=json_data, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get('errcode', 0) != 0:
            raise Exception(f"创建草稿失败: {data}")

        media_id = data['media_id']
        logger.info(f"草稿创建成功: {self._mask_media_id(media_id)}")

        return media_id

    def convert_to_wechat_html(self, markdown_content: str, theme: str = 'ocean') -> str:
        """
        将 Markdown 转换为微信 HTML

        Args:
            markdown_content: Markdown 内容
            theme: 主题名称

        Returns:
            微信公众号格式的 HTML 内容（仅 body 内容，样式内联）
        """
        # 保存临时 Markdown 文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(markdown_content)
            temp_md_path = f.name

        try:
            # 调用 markdown_converter 模块转换
            from .markdown_converter import convert_markdown_to_html

            html_content = convert_markdown_to_html(temp_md_path, output_file=None, theme=theme)

            # 使用 premailer 将 CSS 内联化
            from premailer import Premailer

            p = Premailer(
                html_content,
                strip_important=False,
                keep_style_tags=False,
                remove_classes=False
            )

            inlined_html = p.transform()

            # 提取 body 内容（微信不支持完整 HTML 文档）
            body_content = self._extract_body_content(inlined_html)

            return body_content

        finally:
            # 清理临时文件
            if os.path.exists(temp_md_path):
                os.remove(temp_md_path)

    def _extract_body_content(self, html: str) -> str:
        """
        提取 body 内容并去除外层容器和标题

        微信公众号不支持某些容器样式，需要简化结构
        标题已经在 draft 的 title 字段中，正文不需要重复
        """
        import re
        from bs4 import BeautifulSoup

        # 提取 body 标签内的内容
        match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        if not match:
            return html

        body_html = match.group(1)

        # 使用 BeautifulSoup 解析
        soup = BeautifulSoup(body_html, 'html.parser')

        # 查找 content-card 容器
        content_card = soup.find('div', class_='content-card')
        if content_card:
            # 去掉第一个 h1 标题（标题已经在 draft title 中）
            h1 = content_card.find('h1')
            if h1:
                h1.decompose()

            # 返回 content-card 的内部 HTML（不包含 content-card 本身）
            return content_card.decode_contents()

        # 如果没找到，返回原始内容
        return body_html

    def _generate_digest(self, content: str, max_bytes: int = 54) -> str:
        """
        生成摘要

        微信公众号 digest 字段限制：
        - 最大长度：54 字节（UTF-8 编码）
        - 中文字符占 3 字节，英文占 1 字节
        - 超过会返回 errcode 45004
        """
        # 移除 HTML 标签
        import re
        text = re.sub(r'<[^>]+>', '', content)
        text = text.strip()

        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)

        return self._truncate_by_bytes(text, max_bytes)

    def _truncate_by_bytes(self, text: str, max_bytes: int) -> str:
        """按字节数截断文本"""
        # 按字节截断
        encoded = text.encode('utf-8')
        if len(encoded) <= max_bytes:
            return text

        # 逐字符截断，确保不超过字节限制
        result = ""
        for char in text:
            test_str = result + char
            if len(test_str.encode('utf-8')) > max_bytes:
                break
            result = test_str

        return result

    def _mask_media_id(self, media_id: str) -> str:
        """遮蔽 media_id 用于日志"""
        if not media_id or len(media_id) < 8:
            return "***"
        return media_id[:4] + "***" + media_id[-4:]
