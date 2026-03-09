# 文章模板系统使用指南

## 概述

文章生成器已重构为基于模板的通用系统，支持多种文章类型。每篇文章由三部分组成：

1. **Summary（摘要）** - 使用引用格式（quote），概括核心要点
2. **Body（正文）** - 灵活的内容结构，AI 根据模板参考生成
3. **Footer（页脚）** - 标准免责声明或结束语

## 配置文件

### 主配置文件
`config/wechat_bot_config.yaml` - 设置默认文章类型

```yaml
article:
  article_type: "financial_report"  # 默认文章类型
```

### 模板配置文件
`config/article_templates.yaml` - 定义模板文件路径和通用要求
`config/templates/*.yaml` - 定义各种文章类型的详细模板

## 支持的文章类型

### 1. financial_report（财经日报）
- **用途**：日常财经新闻报道
- **结构**：编者按 + 新闻速递 + 市场表现 + 市场展望
- **适用场景**：股市行情、经济数据、政策动态

### 2. tech_news（科技资讯）
- **用途**：科技领域新闻报道
- **结构**：今日看点 + 重磅新闻 + 产品与技术 + 行业动态 + 趋势观察
- **适用场景**：产品发布、技术突破、行业动态

### 3. general_news（通用新闻摘要）
- **用途**：任意主题的新闻汇总
- **结构**：今日要闻 + 核心新闻 + 深度解读 + 相关影响
- **适用场景**：综合新闻、跨领域资讯

### 4. knowledge_explanation（知识解读）
- **用途**：解释经济名词、历史事件等
- **结构**：核心要点 + 背景介绍 + 核心概念 + 实际案例 + 当前影响
- **适用场景**：热点解读、知识科普

## 使用方法

### 基础用法

```python
from modules.article_generator import ArticleGenerator

# 初始化生成器
generator = ArticleGenerator(
    config=article_config,
    api_key="your_api_key",
    ai_provider="openai"
)

# 生成默认类型文章（财经日报）
article = generator.generate_article(
    news_items=news_list,
    date_str="20260306"
)
```

### 指定文章类型

```python
# 生成科技资讯
article = generator.generate_article(
    news_items=news_list,
    date_str="20260306",
    article_type="tech_news"
)

# 生成通用新闻摘要
article = generator.generate_article(
    news_items=news_list,
    date_str="20260306",
    article_type="general_news"
)
```

### 知识解读（带自定义主题）

```python
# 解读特定主题
article = generator.generate_article(
    news_items=news_list,
    date_str="20260306",
    article_type="knowledge_explanation",
    custom_topic="量化宽松政策"
)
```

### 查询可用的文章类型

```python
# 获取所有支持的文章类型
available_types = generator.get_available_article_types()
print(available_types)
# 输出: ['financial_report', 'tech_news', 'general_news', 'knowledge_explanation']
```

## 自定义模板

### 添加新的文章类型

**步骤 1：** 在 `config/article_templates.yaml` 中添加模板索引：

```yaml
template_files:
  my_custom_type: "templates/my_custom_type.yaml"
```

**步骤 2：** 创建 `config/templates/my_custom_type.yaml`：

```yaml
name: "自定义文章类型"

# 标题格式配置
title_formats:
  morning: "自定义早报 | {date}"
  evening: "自定义日报 | {date}"

# 新闻搜索配置
news_search:
  enabled: true
  query: "自定义搜索关键词"
  num_results: 30
  use_autoprompt: true
  include_domains: []
  exclude_keywords:
    - "排除的关键词"
  time_range: 24

summary:
  title: "📌 核心摘要"
  style: "quote"
  prompt: "用简洁的语言概括核心内容"

body:
  reference_structure: |
    ## 一、主要内容
    ## 二、详细分析

  prompt: |
    根据新闻素材撰写文章，包含以下内容：
    - 主要内容：列举关键信息
    - 详细分析：深入解读

footer:
  content: |
    本文内容仅供参考。
    关注我们，获取更多资讯。
```

### 修改现有模板

直接编辑 `config/article_templates.yaml` 中对应的模板配置即可。修改后无需重启，下次生成文章时会自动加载新配置。

## 模板结构说明

### Summary 部分
- `title`: 摘要标题（如 "📝 编者按"）
- `style`: 固定为 "quote"，表示使用引用格式
- `prompt`: 给 AI 的指令，说明如何生成摘要

### Body 部分
- `reference_structure`: 参考结构（可选），展示建议的章节布局
- `prompt`: 给 AI 的详细指令，说明如何生成正文内容

### Footer 部分
- `content`: 页脚文本，通常是免责声明或结束语

## 注意事项

1. **向后兼容**：未指定 `article_type` 时，默认使用 `financial_report`
2. **模板加载失败**：如果无法加载模板文件，系统会使用内置的默认模板
3. **AI 灵活性**：Body 部分的结构仅作参考，AI 会根据实际新闻素材灵活调整
4. **真实性优先**：所有模板都强调只使用提供的新闻素材，不编造信息

## Mock 模式

Mock 模式下，每种文章类型都有对应的示例文章：

```python
generator = ArticleGenerator(
    config=article_config,
    mock_mode=True
)

# 生成 Mock 文章
article = generator.generate_article(
    news_items=[],
    date_str="20260306",
    article_type="tech_news"
)
```

## 常见问题

### Q: 如何修改文章的标题格式？
A: 编辑对应模板文件（如 `config/templates/financial_report.yaml`）中的 `title_formats` 配置。

### Q: 如何调整文章长度？
A: 在 `config/wechat_bot_config.yaml` 中修改 `min_length` 和 `max_length`。

### Q: 如何更改 AI 模型？
A: 在初始化 `ArticleGenerator` 时指定 `model_name` 参数。

### Q: 模板修改后需要重启吗？
A: 不需要。模板配置在每次生成文章时动态加载。

## 示例输出

### 财经日报示例

```markdown
# 财经早报 | 20260306

> ## 📝 编者按
>
> 2026年3月6日，市场迎来积极信号...

---

## 一、新闻速递
...

---

本文内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。
关注我们，获取更多财经资讯。
```

### 科技资讯示例

```markdown
# 科技速递 | 20260306

> ## 💡 今日看点
>
> 2026年3月6日，科技领域迎来多项重磅消息...

---

## 一、重磅新闻
...

---

本文内容仅供参考，不代表投资建议。
关注我们，获取更多科技资讯。
```
