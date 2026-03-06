# WeChat Editor Bot - 微信编辑器机器人

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

通用的内容生成和微信公众号发布平台。支持多种文章类型（财经、科技、通用新闻、知识解读），自动采集新闻、生成文章、配图并发布到微信公众号。

## ✨ 核心特性

- 📝 **多种文章类型** - 支持财经日报、科技资讯、通用新闻摘要、知识解读等多种文章类型
- 🔍 **智能新闻采集** - 基于文章类型自动配置搜索关键词，灵活过滤内容
- ✍️ **AI 文章生成** - 使用 DeepSeek/Claude API 生成专业、易读的文章（1200-1800 字）
- 🌤️ **AI 天气服务** - 使用 DeepSeek AI 获取实时天气信息
- 🎨 **天气主题封面** - 根据实时天气生成油画风格封面图（晴天/阴天/雨天不同风格）
- 📱 **微信自动发布** - 自动转换为微信格式并创建草稿（支持人工审核）
- 🗂️ **文件自动管理** - 30 天自动归档，保持目录整洁
- 🎨 **精美排版** - 编者按卡片样式，小字免责声明，支持多种主题
- ⚙️ **高度可配置** - 文章类型、新闻源、样式主题均可自定义

## 📚 支持的文章类型

1. **财经日报** (`financial_report`) - 股市行情、经济数据、政策动态
2. **科技资讯** (`tech_news`) - 产品发布、技术突破、行业动态
3. **通用新闻摘要** (`general_news`) - 任意主题的新闻汇总
4. **知识解读** (`knowledge_explanation`) - 解释经济名词、历史事件等

## 🚀 快速开始

### 前置要求

- Python 3.9+
- 微信公众号（服务号或认证订阅号）
- DeepSeek API Key（文章生成 + 天气获取，推荐）或 Claude API Key
- Exa API Key（新闻搜索）
- 图片生成 API（TuZi/OpenAI/Gemini/ModelScope 任选其一）

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd wechat-editor-bot

# 推荐使用 uv（更快）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 或使用传统 pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 配置

```bash
# 复制配置模板
cp config/secrets.yaml.example config/secrets.yaml

# 编辑配置文件，填入你的 API keys
vim config/secrets.yaml
```

**config/secrets.yaml 示例：**

```yaml
api:
  # Exa API（用于新闻搜索）
  exa_api_key: "your-exa-api-key"

  # DeepSeek API（用于文章生成）
  deepseek_key: "sk-xxxxx"
  deepseek_base_url: "https://api.deepseek.com"
  deepseek_model: "deepseek-chat"

  # 图片生成 API
  image_provider: "tuzi"  # 可选: openai, gemini, tuzi, modelscope
  image_key: "your_image_api_key"
  image_base_url: "https://api.tu-zi.com/v1"
  image_model: "doubao-seedream-4-5-251128"

wechat:
  appid: "wx_your_appid"
  secret: "your_wechat_secret"
```

### 运行

```bash
# Mock 模式测试（不消耗 API 配额）
uv run python wechat_editor_bot.py --mock

# 生产模式（使用默认文章类型：财经日报）
uv run python wechat_editor_bot.py

# 生成科技资讯
uv run python wechat_editor_bot.py --article-type tech_news

# 生成通用新闻摘要
uv run python wechat_editor_bot.py --article-type general_news

# 生成知识解读（需要指定主题）
uv run python wechat_editor_bot.py --article-type knowledge_explanation --topic "量化宽松"

# 自定义配置文件
uv run python wechat_editor_bot.py --config custom_config.yaml --secrets custom_secrets.yaml
```

## 📖 配置文件说明

### 主配置文件 (`config/wechat_bot_config.yaml`)

通用配置，包括默认文章类型、图片配置、微信发布配置等。

```yaml
article:
  article_type: "financial_report"  # 默认文章类型
  style: "professional_engaging"
  min_length: 1200
  max_length: 1800
  include_summary: true

image:
  primary_size: "3000x1276"
  secondary_size: "2000x2000"
  style: "oil_painting"
  mood: "relaxing"

weather:
  location: "Nanjing"

wechat:
  auto_publish: false
  create_draft: true
  theme: "warm"
  author: "Jasper"
  enable_comment: true
  only_fans_comment: false

cleanup:
  keep_days: 3
  archive_enabled: true
```

### 模板配置文件 (`config/article_templates.yaml`)

定义每种文章类型的标题格式、新闻搜索配置、内容结构和样式。

```yaml
templates:
  financial_report:
    name: "财经日报"

    # 标题格式（支持时段格式或空字符串让 AI 生成）
    title_formats:
      morning: "财经早报 | {date}"
      afternoon: "财经速递 | {date}"
      evening: "财经日报 | {date}"

    # 新闻搜索配置
    news_search:
      enabled: true
      query: "最新财经新闻 股市行情 A股港股美股指数"
      num_results: 50
      time_range: 24  # 最近 24 小时
      include_domains: []  # 可选：限制搜索域名（留空则搜索所有网站）
        # - "reuters.com"
        # - "bloomberg.com"
      exclude_keywords:
        - "加密货币"
        - "赌博"

    # 文章结构
    summary:
      title: "📝 编者按"
      prompt: "用 2-3 句话概括今日市场核心要点"

    body:
      prompt: "撰写财经报道，包括新闻速递、市场表现、市场展望"

    footer:
      content: "本文内容仅供参考，不构成投资建议。"

  tech_news:
    name: "科技资讯"
    title_formats: ""  # 空字符串表示由 AI 生成标题
    # ... 其他配置
```

## 🎨 自定义文章类型

你可以在 `config/article_templates.yaml` 中添加新的文章类型：

1. 定义标题格式（`title_formats`）- 可以是时段格式、固定格式或空字符串（AI 生成）
2. 配置新闻搜索（`news_search`）- 包括搜索关键词、时间范围、结果数量等
3. 设置摘要样式（`summary`）
4. 提供正文结构参考（`body`）
5. 配置页脚内容（`footer`）

详见 [文章模板使用指南](docs/article_templates_usage.md)。

## 📁 项目结构

```
wechat-editor-bot/
├── wechat_editor_bot.py         # 主程序入口
├── pyproject.toml               # 项目配置和依赖
├── uv.lock                      # 依赖锁定文件
├── modules/                     # 核心模块
│   ├── exa_news_gatherer.py     # Exa 新闻采集
│   ├── article_generator.py     # AI 文章生成
│   ├── weather_service.py       # 天气服务
│   ├── image_generator.py       # 封面图生成
│   ├── wechat_publisher.py      # 微信 API 集成
│   └── file_manager.py          # 文件管理
├── config/
│   ├── wechat_bot_config.yaml   # 主配置文件
│   ├── article_templates.yaml   # 文章模板配置
│   ├── secrets.yaml             # 敏感配置（不提交）
│   └── secrets.yaml.example     # 配置模板
├── output/                      # 输出目录
│   ├── articles/                # Markdown 文章
│   ├── html/                    # 微信 HTML
│   ├── images/                  # 封面图片
│   └── archive/                 # 归档（30天+）
├── tests/                       # 测试文件
├── .github/workflows/           # GitHub Actions
│   ├── test-news-bot.yml        # CI 测试
│   └── daily-news.yml           # 定时任务
└── docs/                        # 文档
```

## ⚙️ 配置说明

详细配置指南请参考 [docs/CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md)

### 关键配置项

**wechat_bot_config.yaml**（主配置）：

```yaml
article:
  article_type: "financial_report"  # 默认文章类型
  style: "professional_engaging"
  min_length: 1200
  max_length: 1800
  include_summary: true

image:
  primary_size: "3000x1276"
  secondary_size: "2000x2000"
  style: "oil_painting"
  mood: "relaxing"

weather:
  location: "Nanjing"

wechat:
  auto_publish: false
  create_draft: true
  theme: "warm"  # 主题：ocean（深海静谧）、fresh（清新绿色）、warm（热情似火）
  author: "Jasper"
  enable_comment: true
  only_fans_comment: false

cleanup:
  keep_days: 3
  archive_enabled: true
```

## 🎨 文章样式特性

- **编者按卡片**：标题和内容在统一的卡片中，带渐变背景和阴影
- **章节标题**：使用"一、二、三、"编号，带背景色和左边框
- **免责声明**：小字居中显示，简洁美观
- **无分割线**：章节之间无 hr 分割线，视觉更流畅

## 🕐 定时任务

### 方式 1：GitHub Actions（推荐）

推送到 GitHub 后自动启用，需在仓库 Settings → Secrets 中配置：

- `EXA_API_KEY` - Exa API Key（新闻搜索）
- `DEEPSEEK_API_KEY` - DeepSeek API Key（文章生成）
- `IMAGE_PROVIDER` - 图片生成服务商（tuzi/openai/gemini/modelscope）
- `IMAGE_API_KEY` - 图片生成 API Key
- `IMAGE_BASE_URL` - 图片 API 地址
- `IMAGE_MODEL` - 图片生成模型
- `WECHAT_APPID` - 微信公众号 AppID
- `WECHAT_SECRET` - 微信公众号 Secret

**定时任务：** 每天北京时间 07:00 自动运行，根据触发时间生成对应的文章标题：
- 早晨 (2:00-10:00)：生成"财经早报"
- 白天 (10:00-17:00)：生成"财经速递"
- 晚上 (17:00-2:00)：生成"财经日报"

### 方式 2：本地 Cron

```bash
crontab -e

# 每天 7:00 运行（财经日报）
0 7 * * * cd /path/to/wechat-editor-bot && uv run python wechat_editor_bot.py --article-type financial_report >> logs/cron.log 2>&1
```

## 💰 成本估算

| 服务 | 月成本 | 说明 |
|------|--------|------|
| Exa API | ~$5-10 | 新闻搜索服务 |
| DeepSeek API | ~$1-2 | 30 篇文章 + 天气查询，极低成本 |
| 图片生成 | $1-30 | 取决于提供商（TuZi/OpenAI/Gemini） |
| **总计** | **$7-42** | 使用 DeepSeek 可大幅降低成本 |

## 🔧 故障排查

### 图片生成失败

```bash
# 检查配置
cat config/secrets.yaml | grep image

# 查看日志
tail -f wechat_editor_bot.log
```

### 微信上传失败

- 检查 appid/secret 是否正确
- 确认公众号类型支持素材管理接口
- 图片大小 < 2MB（系统会自动压缩）
- **IP 白名单问题**：如遇到 `errcode: 40164` 错误，需要在微信公众平台添加 IP 白名单
  - 登录 [微信公众平台](https://mp.weixin.qq.com/)
  - 进入 设置 → 安全中心 → IP 白名单
  - 添加你的服务器或本地 IP 地址
- 查看[微信错误码文档](https://developers.weixin.qq.com/doc/offiaccount/Return_codes/Return_code_descriptions_new.html)

### 天气获取失败

- 确认 DeepSeek API Key 已配置
- 检查 `weather.provider` 设置为 `"ai"`
- 查看日志中的错误信息

### 文章质量不佳

- 调整 `config/article_templates.yaml` 中的模板配置
- 修改 `modules/article_generator.py` 中的提示词
- 调整新闻搜索的 `num_results` 获取更多新闻源

## 📚 文档

- [安装指南](docs/INSTALL.md)
- [配置指南](docs/CONFIG_GUIDE.md)
- [样式指南](docs/STYLE_GUIDE.md)

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

- [Exa API](https://exa.ai/) - 智能新闻搜索
- [DeepSeek API](https://www.deepseek.com/) - AI 文章生成和天气服务
- [微信公众平台](https://mp.weixin.qq.com/) - 内容发布平台

---

**⚠️ 重要提示**：
1. 系统默认创建草稿而非自动发布，请在微信后台人工审核后发布
2. 自动过滤敏感关键词，但仍需人工检查内容合规性
3. 注意 API 调用限制和成本控制
4. 建议先在 Mock 模式下测试完整流程
