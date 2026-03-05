#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片生成模块
根据天气生成封面图片
"""

import logging
import requests
import os
import random
from typing import Dict
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageGenerator:
    """图片生成器"""

    def __init__(self, config: dict, image_config: dict):
        self.config = config
        self.image_config = image_config
        self.style = config.get('style', 'oil_painting')
        self.mood = config.get('mood', 'relaxing')
        self.primary_size = config.get('primary_size', '900x383')
        self.secondary_size = config.get('secondary_size', '500x500')

        # 从父配置获取图片 API 配置
        self.provider = image_config.get('provider', 'openai')
        self.api_key = image_config.get('api_key') or os.getenv('IMAGE_API_KEY')
        self.api_base = image_config.get('api_base', 'https://api.openai.com/v1')
        self.model = image_config.get('model', 'dall-e-3')

    def generate_cover_image(self, weather_data: Dict, size: str = None) -> bytes:
        """
        生成封面图片

        Args:
            weather_data: 天气数据
            size: 图片尺寸 (默认使用配置)

        Returns:
            图片字节数据
        """
        size = size or self.primary_size
        logger.info(f"生成封面图片: {size}")

        # 构建提示词
        prompt = self._build_prompt(weather_data)
        logger.info(f"图片提示词: {prompt}")

        # 调用图片生成 API
        try:
            image_url = self._call_image_api(prompt, size)
            image_data = self._download_image(image_url)

            # 压缩图片（如果超过 2MB）
            image_data = self._compress_if_needed(image_data)

            logger.info(f"图片生成成功，大小: {len(image_data)} 字节")
            return image_data

        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            logger.warning("降级到本地生成占位图片")
            return self._generate_fallback_image(weather_data, size)

    def _build_prompt(self, weather_data: Dict) -> str:
        """根据天气构建提示词"""

        condition = weather_data.get('condition', 'Clear').lower()
        time_of_day = weather_data.get('time_of_day', 'morning')

        # 场景列表（保持简短，多样化）
        rain_scenes = [
            "细雨中的江南水乡", "小桥流水，烟雨朦胧", "细雨霏霏的城市街道", "淅淅沥沥的窗外",
            "雨中公园小径", "湿润的乡间小路", "雨幕中的河边", "蒙蒙细雨的街头",
            "雨滴打在屋檐上", "薄雾下的街道"
        ]
        cloud_scenes = [
            "云雾缭绕的山水画", "阴云密布的城市天际", "多云的森林小径", "灰白天空的海边",
            "薄雾环绕的湖面", "多云的草原", "云层覆盖的山峰", "阴云笼罩的乡村",
            "多云的河岸", "雾气弥漫的小路"
        ]
        snow_scenes = [
            "雪后的宁静村庄", "白雪皑皑的平原", "枯树覆盖厚雪的公园", "雪地中的湖面",
            "雪夜的街道", "山间雪林", "雪覆盖的山坡", "雪花飘落的村庄",
            "冰冻的小溪", "雪覆盖的田野"
        ]
        sunny_scenes = [
            "阳光明媚的田园风光", "金色麦田", "蓝天白云的广阔草原", "阳光下的海滩",
            "阳光洒在石桥上", "明亮的花园小径", "晴空下的森林", "阳光照耀的湖面",
            "晴天的乡村小路", "阳光下的山丘"
        ]

        # 根据天气随机选择场景
        if 'rain' in condition or 'drizzle' in condition:
            scene = random.choice(rain_scenes)
        elif 'cloud' in condition or 'overcast' in condition:
            scene = random.choice(cloud_scenes)
        elif 'snow' in condition:
            scene = random.choice(snow_scenes)
        else:
            scene = random.choice(sunny_scenes)

        # 时段光线
        lighting_map = {
            'morning': "清晨",
            'afternoon': "午后",
            'evening': "傍晚",
            'night': "深夜"
        }
        lighting = lighting_map.get(time_of_day, "清晨")

        # 风格随机选择
        styles = ["油画", "卡通", "水彩画", "数字插画"]
        style = random.choice(styles)

        # 修饰词随机选择 2 个
        adjectives = ["柔和色彩", "细腻笔触", "宁静氛围", "明亮光影", "梦幻感觉", "舒适放松"]
        adj = ", ".join(random.sample(adjectives, 2))

        prompt = f"{scene}，{lighting}，风格为{style}，{adj}，让人心胸开阔，心情愉悦，高质量，专业摄影"

        return prompt

    def _call_image_api(self, prompt: str, size: str) -> str:
        """调用图片生成 API"""

        if self.provider in ['openai', 'tuzi']:
            return self._call_openai_compatible_api(prompt, size)
        elif self.provider == 'gemini':
            return self._call_gemini_api(prompt, size)
        else:
            raise ValueError(f"不支持的图片提供者: {self.provider}")

    def _call_openai_compatible_api(self, prompt: str, size: str) -> str:
        """调用 OpenAI 兼容的 API"""

        url = f"{self.api_base}/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 转换尺寸格式
        if 'x' in size:
            width, height = size.split('x')
            size_param = f"{width}x{height}"
        else:
            size_param = "1024x1024"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": size_param
        }

        logger.info(f"调用图片 API: {url}")
        logger.debug(f"请求参数: model={self.model}, size={size_param}")

        # 禁用代理（避免代理服务器问题）
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=60,
            proxies={'http': None, 'https': None}
        )

        # 检查响应
        if response.status_code != 200:
            error_msg = f"API 返回错误: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_detail = error_data['error']
                    error_msg = f"{error_msg} - {error_detail.get('message', 'Unknown error')}"
                    error_code = error_detail.get('code', '')

                    # 特殊处理速率限制错误
                    if error_code == 'rate_limit':
                        logger.warning("遇到速率限制，建议稍后重试")
                        raise Exception(f"API 速率限制: {error_detail.get('message')}")
            except:
                pass

            logger.error(error_msg)
            raise Exception(error_msg)

        data = response.json()

        # 检查响应格式
        if 'data' not in data or len(data['data']) == 0:
            raise Exception("API 响应格式异常: 缺少 data 字段")

        # 支持 URL 和 base64 两种格式
        image_data = data['data'][0]

        if 'url' in image_data:
            image_url = image_data['url']
            logger.info(f"获取到图片 URL: {image_url[:50]}...")
            return image_url
        elif 'b64_json' in image_data:
            # 如果是 base64 格式，需要解码并上传到临时位置
            logger.info("收到 base64 格式图片，需要额外处理")
            import base64
            import tempfile
            b64_data = image_data['b64_json']
            img_bytes = base64.b64decode(b64_data)

            # 保存到临时文件并返回路径（调用方需要处理）
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(img_bytes)
                temp_path = f.name

            logger.info(f"Base64 图片已保存到临时文件: {temp_path}")
            return f"file://{temp_path}"  # 返回本地文件路径
        else:
            raise Exception("API 响应中既没有 url 也没有 b64_json")

        return image_url

    def _call_gemini_api(self, prompt: str, size: str) -> str:
        """调用 Google Gemini API"""
        # Gemini 图片生成实现
        # 这里简化处理，实际需要使用 Gemini 的 imagen API
        raise NotImplementedError("Gemini 图片生成暂未实现")

    def _download_image(self, url: str) -> bytes:
        """下载图片"""
        # 处理本地文件路径（base64 格式返回的临时文件）
        if url.startswith('file://'):
            file_path = url[7:]  # 移除 'file://' 前缀
            with open(file_path, 'rb') as f:
                return f.read()

        # 禁用代理
        response = requests.get(url, timeout=30, proxies={'http': None, 'https': None})
        response.raise_for_status()
        return response.content

    def _compress_if_needed(self, image_data: bytes, max_size_mb: float = 2.0) -> bytes:
        """如果图片超过指定大小则压缩"""

        size_mb = len(image_data) / (1024 * 1024)
        if size_mb <= max_size_mb:
            return image_data

        logger.info(f"图片大小 {size_mb:.2f}MB，开始压缩")

        # 使用 PIL 压缩
        img = Image.open(BytesIO(image_data))

        # 转换为 RGB（如果是 RGBA）
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # 逐步降低质量直到满足大小要求
        quality = 85
        while quality > 50:
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_data = output.getvalue()

            compressed_size_mb = len(compressed_data) / (1024 * 1024)
            if compressed_size_mb <= max_size_mb:
                logger.info(f"压缩完成: {compressed_size_mb:.2f}MB (质量: {quality})")
                return compressed_data

            quality -= 5

        logger.warning(f"压缩后仍超过限制: {compressed_size_mb:.2f}MB")
        return compressed_data

    def _generate_fallback_image(self, weather_data: Dict, size: str) -> bytes:
        """生成降级占位图片"""
        from datetime import datetime

        # 解析尺寸
        if 'x' in size:
            width, height = map(int, size.split('x'))
        else:
            width, height = 900, 383

        # 根据天气选择背景色
        condition = weather_data.get('condition', 'Clear').lower()
        if 'rain' in condition:
            bg_color = (108, 142, 191)  # 雨天蓝灰色
        elif 'cloud' in condition:
            bg_color = (156, 175, 193)  # 多云灰蓝色
        elif 'snow' in condition:
            bg_color = (220, 230, 240)  # 雪天浅蓝色
        else:
            bg_color = (135, 206, 235)  # 晴天天蓝色

        # 创建图片
        img = Image.new('RGB', (width, height), color=bg_color)
        d = ImageDraw.Draw(img)

        # 添加渐变效果（简单模拟）
        for i in range(height):
            alpha = i / height
            color = tuple(int(c * (1 - alpha * 0.3)) for c in bg_color)
            d.line([(0, i), (width, i)], fill=color)

        # 添加文字信息
        date_str = datetime.now().strftime('%Y年%m月%d日')
        temp = weather_data.get('temperature', '20')
        condition_text = weather_data.get('condition', 'Clear')

        text_lines = [
            "财经日报",
            date_str,
            f"{condition_text} {temp}°C"
        ]

        # 计算文字位置（居中）
        y_offset = height // 2 - 60
        for line in text_lines:
            # 使用默认字体
            bbox = d.textbbox((0, 0), line)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2

            # 添加阴影效果
            d.text((x + 2, y_offset + 2), line, fill=(0, 0, 0, 128))
            d.text((x, y_offset), line, fill=(255, 255, 255))
            y_offset += 40

        # 转换为字节
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)

        logger.info(f"降级图片生成成功: {width}x{height}")
        return buffer.getvalue()
