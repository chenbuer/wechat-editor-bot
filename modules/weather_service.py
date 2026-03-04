#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气服务模块
使用 AI 获取天气信息
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class WeatherService:
    """天气服务"""

    def __init__(self, location: str = "Nanjing", ai_api_key: str = None,
                 ai_base_url: str = "https://api.deepseek.com",
                 ai_model: str = "deepseek-chat"):
        self.location = location
        self.ai_api_key = ai_api_key
        self.ai_base_url = ai_base_url
        self.ai_model = ai_model

    def get_current_weather(self) -> Dict:
        """
        获取当前天气

        Returns:
            天气数据字典
        """
        logger.info(f"获取天气信息: {self.location}")

        # 使用 AI 获取天气
        if self.ai_api_key:
            try:
                return self._get_weather_from_ai()
            except Exception as e:
                logger.warning(f"AI 获取天气失败: {e}，使用默认值")
                return self._get_default_weather()
        else:
            logger.warning("未配置 AI API Key，使用默认天气")
            return self._get_default_weather()

    def _get_weather_from_ai(self) -> Dict:
        """使用 AI 获取天气信息"""
        from openai import OpenAI
        from datetime import datetime

        client = OpenAI(
            api_key=self.ai_api_key,
            base_url=self.ai_base_url
        )

        # 构建提示词
        now = datetime.now()
        date_str = now.strftime('%Y年%m月%d日')
        hour = now.hour
        month = now.month

        prompt = f"""请提供 {self.location} 在 {date_str} 当前时刻的天气信息。

要求：
1. 基于当前日期（{month}月）和地理位置，给出合理的天气状况
2. 返回 JSON 格式，包含以下字段：
   - condition: 天气状况（英文，如 Clear, Cloudy, Rainy, Snowy 等）
   - temperature: 温度（摄氏度，只返回数字）
   - description: 天气描述（中文，简短）

只返回 JSON，不要其他内容。"""

        response = client.chat.completions.create(
            model=self.ai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )

        # 解析 AI 返回
        import json
        content = response.choices[0].message.content.strip()

        # 移除可能的 markdown 代码块标记
        if content.startswith('```'):
            content = content.split('\n', 1)[1]
            content = content.rsplit('```', 1)[0]

        weather_info = json.loads(content)

        # 确定时间段
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        elif 18 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        weather_data = {
            'condition': weather_info.get('condition', 'Clear'),
            'temperature': str(weather_info.get('temperature', '20')),
            'time_of_day': time_of_day,
            'location': self.location
        }

        logger.info(f"AI 获取天气: {weather_data['condition']}, {weather_data['temperature']}°C")
        return weather_data

    def _get_default_weather(self) -> Dict:
        """返回默认天气数据"""
        from datetime import datetime
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        elif 18 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        return {
            'condition': 'Clear',
            'temperature': '20',
            'time_of_day': time_of_day,
            'location': self.location
        }
