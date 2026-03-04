#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章生成模块
使用 Claude API 生成财经文章
"""

import logging
from typing import List
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ArticleGenerator:
    """文章生成器"""

    def __init__(self, config: dict, api_key: str = None,
                 ai_provider: str = "openai",
                 api_base_url: str = None,
                 model_name: str = None,
                 mock_mode: bool = False):
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
        self.title_format = config.get('title_format', '不大早的财经早报 | {date}')

        # 设置默认值
        if self.ai_provider == "anthropic":
            self.api_key = self.api_key or os.getenv('ANTHROPIC_API_KEY')
            self.model_name = self.model_name or "claude-3-5-sonnet-20241022"
        elif self.ai_provider == "openai":
            self.api_key = self.api_key or os.getenv('OPENAI_API_KEY')
            self.api_base_url = self.api_base_url or "https://api.openai.com/v1"
            self.model_name = self.model_name or "gpt-4"

    def generate_article(self, news_items: List, date_str: str) -> str:
        """
        生成文章

        Args:
            news_items: 新闻条目列表
            date_str: 日期字符串

        Returns:
            Markdown 格式的文章内容
        """
        logger.info(f"开始生成文章: {date_str}")

        # Mock 模式：返回示例文章
        if self.mock_mode:
            logger.info("Mock 模式：使用示例文章")
            return self._generate_mock_article(date_str)

        if not self.api_key:
            raise ValueError(f"未配置 API Key (provider: {self.ai_provider})")

        # 构建提示词
        prompt = self._build_prompt(news_items, date_str)

        # 根据 provider 调用不同的 API
        try:
            if self.ai_provider == "openai":
                article_content = self._call_openai_api(prompt)
            elif self.ai_provider == "anthropic":
                article_content = self._call_anthropic_api(prompt)
            else:
                raise ValueError(f"不支持的 AI provider: {self.ai_provider}")

            # 后处理：添加免责声明
            article_content = self._post_process(article_content, date_str)

            logger.info(f"文章生成成功 (provider: {self.ai_provider})，长度: {len(article_content)} 字符")
            return article_content

        except Exception as e:
            logger.error(f"文章生成失败 (provider: {self.ai_provider}): {e}")
            raise

    def _generate_mock_article(self, date_str: str) -> str:
        """生成 Mock 文章"""
        return self._get_mock_article_template(date_str)

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

    def _build_prompt(self, news_items: List, date_str: str) -> str:
        """构建 AI 提示词"""
        news_list = "\n\n".join([
            f"【{i+1}】{item.title}\n来源：{item.source}\n摘要：{item.summary}"
            for i, item in enumerate(news_items)
        ])

        date_formatted = datetime.strptime(date_str, '%Y%m%d').strftime('%Y年%m月%d日')
        title = self._format_title(date_str)

        return self._get_prompt_template(date_formatted, news_list, title, date_str)

    def _post_process(self, content: str, date_str: str) -> str:
        """后处理文章内容"""
        # 确保有标题（如果 AI 没有生成）
        if not content.startswith('#'):
            title = self._format_title(date_str)
            content = f"# {title}\n\n{content}"

        # 确保有免责声明（如果 AI 没有生成）
        if '投资有风险' not in content:
            disclaimer = "\n---\n\n本文内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。关注我们，获取更多财经资讯。\n"
            content += disclaimer

        return content

    def _format_title(self, date_str: str) -> str:
        """格式化文章标题"""
        date_formatted = datetime.strptime(date_str, '%Y%m%d').strftime('%Y年%m月%d日')
        return self.title_format.replace('{date}', date_str).replace('{date_formatted}', date_formatted)

    def _get_mock_article_template(self, date_str: str) -> str:
        """获取 Mock 文章模板"""
        date_formatted = datetime.strptime(date_str, '%Y%m%d').strftime('%Y年%m月%d日')
        title = self._format_title(date_str)

        return f"""# {title}

## 📝 编者按

{date_formatted}，市场迎来积极信号。央行降准释放万亿流动性，科技与新能源板块表现强势，A股三大指数集体收涨。国际市场方面，美股延续反弹态势，全球风险偏好有所回升。

---

## 一、📰 新闻速递

### 🇨🇳 国内要闻

**💰 央行宣布降准0.5个百分点**

中国人民银行宣布下调金融机构存款准备金率0.5个百分点，预计释放长期资金约1万亿元，支持实体经济发展，降低企业融资成本。

**🚗 新能源汽车销量持续增长**

2月新能源汽车销量同比增长35%，市场渗透率突破40%。多家车企宣布扩产计划，行业景气度持续提升。

**📈 科技板块表现亮眼**

今日科技板块整体上涨3.2%，人工智能、半导体等细分领域涨幅居前。多家科技公司发布业绩预告，显示行业基本面向好。

### 🌍 国际动态

**🇺🇸 美联储官员释放鸽派信号**

多位美联储官员表示，如果通胀继续回落，可能会考虑放缓加息步伐。市场对此反应积极，美股三大指数集体上涨。

**🛢️ 国际油价小幅回调**

受需求预期影响，国际油价小幅回调，布伦特原油跌0.8%至82美元/桶。

---

## 二、📊 股市表现

### A股市场

**指数表现：**

上证指数收涨 **1.2%**，报收 3,245 点；深证成指上涨 **1.5%**，报收 11,680 点；创业板指大涨 **2.1%**，报收 2,456 点。

**热门板块：**

半导体板块领涨，涨幅超过 **4%**；新能源汽车板块上涨 **3.5%**；金融板块稳健上涨 **1.8%**。

**市场情绪：**

两市成交额较昨日放大15%，北向资金净流入约80亿元，市场情绪明显回暖。

### 美股市场

**指数表现：**

道琼斯指数上涨 **0.8%**；纳斯达克指数上涨 **1.2%**；标普500指数上涨 **0.9%**。

**板块动态：**

科技股表现强势，芯片、云计算板块领涨。

### 全球市场

**港股：** 恒生指数上涨 **1.5%**，科技股带动港股上涨。

**欧洲股市：** 普遍收涨，德国DAX指数涨 **0.6%**。

**日本股市：** 日经225指数上涨 **0.4%**。

---

## 三、🔮 市场展望

**市场走势预判：**

在政策利好和资金面改善的支持下，市场有望延续反弹态势。科技、新能源等成长板块仍是资金关注重点。

**关键因素：**

关注后续经济数据的验证，留意外部环境变化，观察资金流向和板块轮动。

**风险提示：**

市场普涨之后，板块与个股的分化或将随之而来。建议投资者保持理性，关注基本面良好、估值合理的优质标的，做好风险控制。

---

本文内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。关注我们，获取更多财经资讯。

---

*本文为 Mock 模式生成的示例文章*
"""

    def _get_prompt_template(self, date_formatted: str, news_list: str, title: str, date_str: str) -> str:
        """获取 AI 提示词模板"""
        return f"""你是一位资深财经记者，擅长撰写生动有趣的财经早报。

今天是 {date_formatted}，请根据以下财经新闻，撰写一篇财经早报。

**新闻素材：**
{news_list}

**重要说明：**
- 只能使用上述提供的新闻素材，不要添加任何未提供的新闻
- 如果新闻中没有提供具体数据（如指数点位、涨跌幅），不要编造，可以使用描述性词汇如上涨、下跌等
- 如果新闻素材不足以填充某个章节，可以省略该章节或简化处理
- 保持真实性，不要杜撰任何数据或新闻

**文章结构（严格按照以下结构）：**

# {title}

## 📝 编者按
用 2-3 句话概括今日市场核心要点，语气轻松但专业。

---

## 一、📰 新闻速递

### 🇨🇳 国内要闻
根据提供的新闻素材，列举国内重要的财经新闻，每条新闻：
- 使用 emoji 图标开头
- 标题简洁有力
- 1-2 句话说明要点和影响

### 🌍 国际动态
根据提供的新闻素材，列举国际重要的财经新闻，格式同上
（如果新闻素材中没有国际新闻，可以省略此部分）

---

## 二、📊 股市表现

### A股市场

**指数表现：**
根据新闻素材中的信息描述指数表现（如果没有具体数据，使用描述性词汇）

**热门板块：**
根据新闻素材列举热门板块

**市场情绪：**
根据新闻素材描述市场情绪

### 美股市场
（如果新闻素材中没有美股信息，可以省略此部分）

### 全球市场
（如果新闻素材中没有全球市场信息，可以省略此部分）

---

## 三、🔮 市场展望

根据提供的新闻素材，分析：
- 市场可能的走势
- 需要关注的关键因素
- 投资者应注意的风险点

（不要编造未提供的信息，基于已有新闻进行合理分析即可）

---

本文内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。
关注我们，获取更多财经资讯。

---

**写作要求：**
1. **真实性第一**：严格只使用提供的新闻素材，不要编造任何数据、新闻或信息
2. **语言风格**：轻松活泼但不失专业，像朋友聊天一样自然
3. **emoji 使用**：适当使用 emoji 增加可读性（📈📉💰🔥⚡️等）
4. **数据呈现**：如果新闻中有具体数字就使用，没有就用描述性词汇，不要编造
5. **排版**：
   - 使用分隔线（---）区分章节
   - 大章节标题使用 ## 一、## 二、## 三、
   - 小标题使用 ###
   - 重要信息用 **加粗**
   - 使用段落而不是列表
6. **长度**：根据新闻素材的丰富程度灵活调整，保持内容充实但不冗余
7. **合规**：遵守内容监管规定，不涉及敏感话题
8. **免责声明**：文章最后用普通段落写免责声明

请严格按照上述结构输出文章，只使用提供的新闻素材，不要编造信息。"""
