# 配置文件说明

## 配置文件结构

项目使用多个配置文件：

### 1. `config/wechat_bot_config.yaml` - 主配置文件
包含非敏感的业务配置，可以提交到 Git。

### 2. `config/article_templates.yaml` - 模板索引配置
定义模板文件路径和通用写作要求。

### 3. `config/templates/*.yaml` - 文章模板详情
每种文章类型有独立的模板文件（financial_report.yaml、knowledge_explanation.yaml）。

### 4. `config/secrets.yaml` - 敏感配置
包含 API 密钥、AppID 等敏感信息，**不应提交到 Git**（已在 .gitignore 中）。

## 配置详解

### wechat_bot_config.yaml

```yaml
# 文章生成配置
article:
  article_type: "financial_report"  # 默认文章类型
  style: "professional_engaging"
  min_length: 1200
  max_length: 1800
  include_summary: true

# 图片生成配置
image:
  primary_size: "3000x1276"
  style: "oil_painting"
  mood: "relaxing"

# 天气服务配置
weather:
  location: "Nanjing"

# 微信发布配置
wechat:
  auto_publish: false
  create_draft: true
  theme: "warm"
  author: "Jasper"
  enable_comment: true
  only_fans_comment: false

# 文件管理配置
cleanup:
  keep_days: 3
  archive_enabled: true
```

### article_templates.yaml（模板索引）

```yaml
# 模板文件路径配置
template_files:
  financial_report: "templates/financial_report.yaml"
  knowledge_explanation: "templates/knowledge_explanation.yaml"

# 通用写作要求（适用于所有模板）
common_requirements:
  authenticity: "严格只使用提供的新闻素材，不要编造任何数据、新闻或信息"
  data_handling: "如果新闻中有具体数字就使用，没有就用描述性词汇，不要编造"
  length: "根据新闻素材的丰富程度灵活调整，保持内容充实但不冗余"
  compliance: "遵守内容监管规定，不涉及敏感话题"
  formatting:
    - "使用分隔线（---）区分章节"
    - "重要信息用 **加粗**"
    - "禁止使用列表，取而代之使用段落"
```

### templates/financial_report.yaml（财经日报模板）

```yaml
# 财经日报模板
name: "财经日报"

# 标题格式配置（支持时段格式或空字符串让 AI 生成）
title_formats:
  morning: "财经早报 | {date}"
  afternoon: "财经速递 | {date}"
  evening: "财经日报 | {date}"

# 新闻搜索配置
news_search:
  enabled: true
  query: "最新财经新闻 股市行情 A股港股美股指数"
  num_results: 50
  use_autoprompt: true
  include_domains: []
  exclude_keywords:
    - "加密货币"
    - "赌博"
  time_range: 24

summary:
  title: "📝 编者按"
  style: "quote"
  prompt: "用 2-3 句话概括今日市场核心要点，语气轻松但专业。"

body:
  reference_structure: |
    ## 一、新闻速递
    ### 🇨🇳 国内要闻
    ### 🌍 国际动态

    ## 二、市场表现
    ### 🏦 A股市场
    ### 🦀 美股市场
    ### 🐂 全球市场

    ## 三、市场展望

  prompt: |
    根据提供的新闻素材撰写正文，参考以下结构（可根据内容灵活调整）...
    （详细提示词省略）

footer:
  content: |
    本文内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。
    关注我们，获取更多财经资讯。
```

其他文章类型模板（knowledge_explanation.yaml）结构类似，具体内容请查看 [docs/article_templates_usage.md](article_templates_usage.md)。

### secrets.yaml

```yaml
# API 配置
api:
  # Exa API（用于新闻搜索）
  exa_api_key: "your-exa-api-key"

  # DeepSeek API（用于文章生成和天气获取）
  deepseek_key: "sk-xxxxx"
  deepseek_base_url: "https://api.deepseek.com"
  deepseek_model: "deepseek-chat"

  # 图片生成 API
  image_provider: "tuzi"  # 可选: openai, gemini, tuzi, modelscope
  image_key: "your_image_api_key"
  image_base_url: "https://api.tu-zi.com/v1"
  image_model: "doubao-seedream-4-5-251128"

# 微信公众号配置
wechat:
  appid: "wx_your_appid"
  secret: "your_wechat_secret"
```

## 配置项说明

### 文章类型 (article_type)

- `financial_report` - 财经日报
- `knowledge_explanation` - 知识解读

### 标题格式 (title_formats)

支持三种配置方式：

1. **时段格式**（字典）：根据当前时间自动选择
```yaml
title_formats:
  morning: "财经早报 | {date}"
  afternoon: "财经速递 | {date}"
  evening: "财经日报 | {date}"
```

2. **固定格式**（字符串）：始终使用相同格式
```yaml
title_formats: "科技资讯 | {date}"
```

3. **AI 生成**（空字符串）：让 AI 根据内容生成标题
```yaml
title_formats: ""
```

### 新闻搜索配置 (news_search)

- `enabled` - 是否启用新闻搜索
- `query` - 搜索关键词
- `num_results` - 返回结果数量
- `use_autoprompt` - 是否使用 Exa 的自动提示优化
- `time_range` - 时间范围（小时数，如 24 表示最近 24 小时）
- `exclude_keywords` - 排除关键词列表

### 图片配置 (image)

- `primary_size` - 封面图尺寸（如 "3000x1276"）
- `style` - 图片风格（如 "oil_painting"）
- `mood` - 图片氛围（如 "relaxing"）

### 微信配置 (wechat)

- `auto_publish` - 是否自动发布（建议设为 false）
- `create_draft` - 是否创建草稿
- `theme` - 主题样式（ocean/fresh/warm）
- `author` - 作者名称
- `enable_comment` - 是否开启评论
- `only_fans_comment` - 是否仅粉丝可评论

### 文件管理配置 (cleanup)

- `keep_days` - 保留天数
- `archive_enabled` - 是否启用归档

## 最佳实践

1. **敏感信息管理**
   - 永远不要将 `secrets.yaml` 提交到 Git
   - 使用环境变量作为备选方案
   - 定期轮换 API 密钥

2. **文章质量优化**
   - 调整 `num_results` 获取更多新闻源
   - 使用 `exclude_keywords` 过滤无关内容
   - 根据需要调整 `time_range`

3. **标题格式选择**
   - 财经日报：使用时段格式，区分早报/速递/日报
   - 知识解读：使用 AI 生成，更具吸引力

4. **测试流程**
   - 先使用 `--mock` 模式测试
   - 确认配置正确后再使用生产模式
   - 定期检查生成的文章质量
