#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章生成模块
使用 AI API 生成各类文章（财经、科技、通用新闻等）
支持基于模板的灵活文章结构
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import os
import yaml

logger = logging.getLogger(__name__)


class ArticleGenerator:
    """文章生成器 - 支持多种文章类型的通用生成器"""

    def __init__(self, config: dict, api_key: str = None,
                 ai_provider: str = "openai",
                 api_base_url: str = None,
                 model_name: str = None,
                 mock_mode: bool = False,
                 template_config_path: str = None):
        self.config = config
        self.api_key = api_key
        self.ai_provider = ai_provider
        self.api_base_url = api_base_url
        self.model_name = model_name
        self.mock_mode = mock_mode
        self.style = config.get('style', 'professional_engaging')
        self.min_length = config.get('min_length', 800)
        self.max_length = config.get('max_length', 1500)
        self.include_summary = config.get('include_summary', True)

        # 支持新的时段标题格式配置
        self.title_formats = config.get('title_formats', {})
        self.title_format = config.get('title_format', '财经早报 | {date}')

        # 加载文章模板配置
        self.templates = self._load_templates(template_config_path)

        # 默认文章类型（向后兼容）
        self.default_article_type = config.get('article_type', 'financial_report')

        # Mock 模板目录
        self.mock_template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'templates', 'mock'
        )

        # 设置默认值
        if self.ai_provider == "anthropic":
            self.api_key = self.api_key or os.getenv('ANTHROPIC_API_KEY')
            self.model_name = self.model_name or "claude-3-5-sonnet-20241022"
        elif self.ai_provider == "openai":
            self.api_key = self.api_key or os.getenv('OPENAI_API_KEY')
            self.api_base_url = self.api_base_url or "https://api.openai.com/v1"
            self.model_name = self.model_name or "gpt-4"

    def _load_templates(self, template_config_path: str = None) -> Dict:
        """加载文章模板配置"""
        if template_config_path is None:
            # 默认路径
            template_config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config', 'article_templates.yaml'
            )

        try:
            with open(template_config_path, 'r', encoding='utf-8') as f:
                template_config = yaml.safe_load(f)
                logger.info(f"成功加载文章模板配置: {template_config_path}")

                # 如果配置中包含 template_files，则加载拆分的模板文件
                if 'template_files' in template_config:
                    templates = {}
                    config_dir = os.path.dirname(template_config_path)

                    for template_name, template_file in template_config['template_files'].items():
                        template_path = os.path.join(config_dir, template_file)
                        try:
                            with open(template_path, 'r', encoding='utf-8') as tf:
                                templates[template_name] = yaml.safe_load(tf)
                                logger.info(f"成功加载模板: {template_name} from {template_path}")
                        except Exception as e:
                            logger.warning(f"无法加载模板文件 {template_path}: {e}")

                    template_config['templates'] = templates

                return template_config
        except Exception as e:
            logger.warning(f"无法加载模板配置文件 {template_config_path}: {e}，使用默认模板")
            return self._get_default_templates()

    def generate_article(self, news_items: List, date_str: str,
                        article_type: str = None, custom_topic: str = None) -> str:
        """
        生成文章

        Args:
            news_items: 新闻条目列表
            date_str: 日期字符串
            article_type: 文章类型 (financial_report, tech_news, general_news, knowledge_explanation)
            custom_topic: 自定义主题（用于知识解读类文章）

        Returns:
            Markdown 格式的文章内容
        """
        article_type = article_type or self.default_article_type
        logger.info(f"开始生成文章: {date_str}, 类型: {article_type}")

        # Mock 模式：返回示例文章
        if self.mock_mode:
            logger.info("Mock 模式：使用示例文章")
            return self._generate_mock_article(date_str, article_type)

        if not self.api_key:
            raise ValueError(f"未配置 API Key (provider: {self.ai_provider})")

        # 构建提示词
        prompt = self._build_prompt(news_items, date_str, article_type, custom_topic)

        # 根据 provider 调用不同的 API
        try:
            # 打印 prompt 到日志
            logger.info(f"=== AI Prompt ===\n{prompt}\n{'='*40}")

            if self.ai_provider == "openai":
                article_content = self._call_openai_api(prompt)
            elif self.ai_provider == "anthropic":
                article_content = self._call_anthropic_api(prompt)
            else:
                raise ValueError(f"不支持的 AI provider: {self.ai_provider}")

            # 后处理：添加标题和页脚
            article_content = self._post_process(article_content, date_str, article_type)

            logger.info(f"文章生成成功 (provider: {self.ai_provider})，长度: {len(article_content)} 字符")
            logger.debug(f"文章内容预览:\n{article_content[:500]}...")
            return article_content

        except Exception as e:
            logger.error(f"文章生成失败 (provider: {self.ai_provider}): {e}")
            raise

    def _generate_mock_article(self, date_str: str, article_type: str = 'financial_report') -> str:
        """生成 Mock 文章"""
        return self._get_mock_article_template(date_str, article_type)

    def _call_openai_api(self, prompt: str) -> str:
        """调用 OpenAI 兼容的 API（包括 DeepSeek）"""
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base_url
        )

        logger.info(f"调用 OpenAI API: {self.api_base_url}, model: {self.model_name}")

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4096,
            temperature=0.7
        )

        return response.choices[0].message.content

    def _call_anthropic_api(self, prompt: str) -> str:
        """调用 Anthropic Claude API"""
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)

        logger.info(f"调用 Anthropic API, model: {self.model_name}")

        response = client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.content[0].text

    def _build_prompt(self, news_items: List, date_str: str,
                     article_type: str = 'financial_report',
                     custom_topic: str = None) -> str:
        """构建 AI 提示词"""

        # 获取模板配置
        template = self._get_template(article_type)
        if not template:
            logger.warning(f"未找到文章类型 {article_type} 的模板，使用默认模板")
            template = self._get_template('financial_report')

        # 根据模板配置决定素材呈现格式
        # 如果 title_formats 为空字符串，使用 bullet 格式（知识解读类）
        # 否则使用 numbered 格式（新闻类）
        title_formats = template.get('title_formats')

        if title_formats == "":
            # 简化素材格式，作为引子
            news_list = "\n\n".join([
                f"• {item.summary}"
                for item in news_items
            ])
            news_list = f"**当前热点引子（仅供参考，用于触发主题联想）：**\n\n{news_list}"
        else:
            # 默认：编号列表格式
            news_list = "\n\n".join([
                f"【{i+1}】{item.title}\n来源：{item.source}\n摘要：{item.summary}"
                for i, item in enumerate(news_items)
            ])

        date_formatted = datetime.strptime(date_str, '%Y%m%d').strftime('%Y年%m月%d日')

        # 根据模板配置决定是否生成标题
        title = self._format_title(date_str, article_type)

        return self._build_prompt_from_template(
            template, date_formatted, news_list, title, date_str, custom_topic, article_type
        )

    def _post_process(self, content: str, date_str: str, article_type: str = 'financial_report') -> str:
        """后处理文章内容"""
        # 获取模板
        template = self._get_template(article_type)

        # 确保有标题（如果 AI 没有生成且配置了标题格式）
        if not content.startswith('#'):
            title = self._format_title(date_str, article_type)
            if title:  # 只有当有标题格式时才添加
                content = f"# {title}\n\n{content}"

        # 添加页脚（如果 AI 没有生成）
        if template and 'footer' in template:
            footer_content = template['footer'].get('content', '')
            # 检查是否已经包含页脚内容的关键词
            footer_keywords = ['仅供参考', '投资有风险', '关注我们']
            has_footer = any(keyword in content for keyword in footer_keywords)

            if not has_footer and footer_content:
                content += f"\n\n---\n\n<!-- footer -->\n{footer_content.strip()}\n<!-- /footer -->\n"

        return content

    def _format_title(self, date_str: str, article_type: str = None) -> Optional[str]:
        """
        格式化文章标题，根据模板配置和当前时间选择合适的标题格式

        Args:
            date_str: 日期字符串 (YYYYMMDD)
            article_type: 文章类型

        Returns:
            格式化的标题，如果配置为空字符串则返回 None（表示由 AI 生成）
        """
        date_formatted = datetime.strptime(date_str, '%Y%m%d').strftime('%Y年%m月%d日')

        # 优先从模板中获取 title_formats
        title_format = None
        if article_type:
            template = self._get_template(article_type)
            if template and 'title_formats' in template:
                template_title_formats = template['title_formats']

                # 如果配置为空字符串，返回 None 表示由 AI 生成标题
                if template_title_formats == "":
                    logger.info(f"文章类型 {article_type} 配置为 AI 生成标题")
                    return None

                # 如果是字典（时段格式），根据当前时间选择
                if isinstance(template_title_formats, dict):
                    title_format = self._get_title_format_by_time(template_title_formats)
                # 如果是字符串，直接使用
                elif isinstance(template_title_formats, str):
                    title_format = template_title_formats

        # 回退到主配置（向后兼容）
        if not title_format:
            if self.title_formats:
                title_format = self._get_title_format_by_time(self.title_formats)
            else:
                title_format = self.title_format

        return title_format.replace('{date}', date_str).replace('{date_formatted}', date_formatted)

    def _get_title_format_by_time(self, title_formats: dict) -> str:
        """
        根据当前时间获取对应的标题格式

        Args:
            title_formats: 标题格式字典

        Returns:
            对应时段的标题格式
        """
        now = datetime.now()
        hour = now.hour

        # 早晨: 2:00-10:00
        if 2 <= hour < 10:
            return title_formats.get('morning', self.title_format)
        # 白天: 10:00-17:00
        elif 10 <= hour < 17:
            return title_formats.get('afternoon', self.title_format)
        # 晚上: 17:00-2:00
        else:
            return title_formats.get('evening', self.title_format)

    def _get_mock_article_template(self, date_str: str, article_type: str = 'financial_report') -> str:
        """获取 Mock 文章模板"""
        date_formatted = datetime.strptime(date_str, '%Y%m%d').strftime('%Y年%m月%d日')
        title = self._format_title(date_str, article_type)

        # 如果没有标题格式（AI 生成），使用默认标题
        if not title:
            title = f"{article_type} | {date_formatted}"

        # 从文件加载 Mock 模板
        return self._load_mock_template(article_type, title, date_formatted)

    def _load_mock_template(self, article_type: str, title: str, date_formatted: str) -> str:
        """从文件加载 Mock 模板"""
        template_file = os.path.join(self.mock_template_dir, f"{article_type}.md")

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
                # 替换占位符
                return template_content.replace('{title}', title).replace('{date_formatted}', date_formatted)
        except FileNotFoundError:
            logger.warning(f"Mock 模板文件不存在: {template_file}，使用默认模板")
            # 回退到 financial_report 模板
            fallback_file = os.path.join(self.mock_template_dir, "financial_report.md")
            try:
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    return template_content.replace('{title}', title).replace('{date_formatted}', date_formatted)
            except FileNotFoundError:
                logger.error(f"默认 Mock 模板也不存在: {fallback_file}")
                return f"# {title}\n\n*Mock 模式示例文章*\n\n{date_formatted}"

    def _get_template(self, article_type: str) -> Optional[Dict]:
        """获取指定类型的文章模板"""
        templates = self.templates.get('templates', {})
        return templates.get(article_type)

    def _build_prompt_from_template(self, template: Dict, date_formatted: str,
                                    news_list: str, title: Optional[str], date_str: str,
                                    custom_topic: str = None, article_type: str = 'financial_report') -> str:
        """根据模板构建提示词"""
        article_name = template.get('name', '文章')
        summary_config = template.get('summary', {})
        body_config = template.get('body', {})
        common_reqs = self.templates.get('common_requirements', {})

        # 构建提示词
        topic_info = f"\n\n**解读主题：** {custom_topic}" if custom_topic else ""

        # 从配置文件读取 prompt 开头
        prompt_intro = self.templates.get('prompt_intro', '你是一位资深记者和内容创作者，擅长撰写生动有趣的{article_name}。')
        prompt_intro = prompt_intro.replace('{article_name}', article_name)

        prompt = f"""{prompt_intro}

今天是 {date_formatted}，请根据以下新闻素材，撰写一篇{article_name}。{topic_info}

**新闻素材：**
{news_list}

"""

        # 使用通用重要说明（从 common_requirements 生成）
        authenticity = common_reqs.get('authenticity', '')
        data_handling = common_reqs.get('data_handling', '')
        compliance = common_reqs.get('compliance', '')
        prompt += f"""**重要说明：**
- {authenticity}
- {data_handling}
- 如果新闻素材不足以填充某个章节，可以省略该章节或简化处理
- {compliance}

"""

        prompt += """**文章结构：**

"""

        # 如果有标题格式，使用固定标题；否则让 AI 生成标题
        if title:
            prompt += f"# {title}\n\n"
        else:
            prompt += "# [请根据内容生成一个简洁有力的标题]\n\n"

        prompt += f"""> ## {summary_config.get('title', '摘要')}
>
> {summary_config.get('prompt', '概括核心要点')}

---

{body_config.get('prompt', '撰写正文内容')}

---

**写作要求：**
1. **真实性第一**：{common_reqs.get('authenticity', '严格使用提供的素材')}
2. **数据呈现**：{common_reqs.get('data_handling', '有数据就用，没有就用描述性词汇')}
3. **长度**：{common_reqs.get('length', '根据素材灵活调整')}
4. **合规**：{common_reqs.get('compliance', '遵守内容监管规定')}
5. **排版**："""

        # 添加格式要求
        formatting = common_reqs.get('formatting', [])
        for i, fmt in enumerate(formatting, 1):
            prompt += f"\n   - {fmt}"

        prompt += "\n\n请严格按照上述结构输出文章，只使用提供的新闻素材，不要编造信息。"

        # 注意：不在 prompt 中包含 footer，footer 在后处理中添加
        return prompt

    def _get_default_templates(self) -> Dict:
        """获取默认模板配置（当无法加载配置文件时使用）"""
        return {
            'templates': {
                'financial_report': {
                    'name': '财经日报',
                    'summary': {
                        'title': '📝 编者按',
                        'style': 'quote',
                        'prompt': '用 2-3 句话概括今日市场核心要点，语气轻松但专业。'
                    },
                    'body': {
                        'prompt': '根据新闻素材撰写财经报道，包括新闻速递、市场表现、市场展望等内容。'
                    },
                    'footer': {
                        'content': '本文内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。\n关注我们，获取更多财经资讯。'
                    }
                }
            },
            'common_requirements': {
                'authenticity': '严格只使用提供的新闻素材',
                'data_handling': '如果新闻中有具体数字就使用，没有就用描述性词汇',
                'length': '根据新闻素材的丰富程度灵活调整',
                'compliance': '遵守内容监管规定，不涉及敏感话题',
                'formatting': [
                    '使用分隔线（---）区分章节',
                    '重要信息用 **加粗**',
                    '禁止使用列表，取而代之使用段落'
                ]
            }
        }

    def get_available_article_types(self) -> List[str]:
        """获取所有可用的文章类型"""
        templates = self.templates.get('templates', {})
        return list(templates.keys())

    def get_news_search_config(self, article_type: str, custom_topic: str = None) -> Optional[Dict]:
        """
        获取指定文章类型的新闻搜索配置

        Args:
            article_type: 文章类型
            custom_topic: 自定义主题（用于替换 query 中的 {topic} 占位符）

        Returns:
            新闻搜索配置字典，如果不需要搜索则返回 None
        """
        template = self._get_template(article_type)
        if not template or 'news_search' not in template:
            logger.info(f"文章类型 {article_type} 没有配置 news_search")
            return None

        config = template['news_search'].copy()

        # 检查是否启用
        if not config.get('enabled', False):
            logger.info(f"文章类型 {article_type} 的新闻搜索已禁用")
            return None

        # 如果查询中包含 {topic} 占位符，替换为实际主题
        if custom_topic and 'query' in config:
            config['query'] = config['query'].replace('{topic}', custom_topic)
            logger.info(f"替换主题占位符: {custom_topic}")

        return config
