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
- 🔧 **模块化执行** - 支持单独执行各个步骤，失败后可从断点继续

## 📚 支持的文章类型

1. **财经日报** (`financial_report`) - 股市行情、经济数据、政策动态
2. **知识解读** (`knowledge_explanation`) - 解释经济名词、历史事件等

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

#### 完整流程（一键运行）

```bash
# Mock 模式测试（不消耗 API 配额）
uv run python wechat_editor_bot.py --mock

# 生产模式（使用默认文章类型：财经日报）
uv run python wechat_editor_bot.py

# 生成知识解读（需要指定主题）
uv run python wechat_editor_bot.py --article-type knowledge_explanation --topic "量化宽松"

# 自定义配置文件
uv run python wechat_editor_bot.py --config custom_config.yaml --secrets custom_secrets.yaml
```

#### 模块化执行（单独运行各步骤）

系统支持将完整流程拆分为独立步骤，失败后可从断点继续：

```bash
# 1. 搜索新闻
uv run python wechat_editor_bot.py search --article-type financial_report --time-range 48

# 2. 生成文章（从缓存读取新闻）
uv run python wechat_editor_bot.py generate

# 3. 转换为微信 HTML
uv run python wechat_editor_bot.py convert --theme warm

# 4. 获取天气信息
uv run python wechat_editor_bot.py weather --location Beijing

# 5. 生成封面图片
uv run python wechat_editor_bot.py image

# 6. 上传到微信
uv run python wechat_editor_bot.py upload

# 查看当前状态
uv run python wechat_editor_bot.py status

# 清理缓存
uv run python wechat_editor_bot.py clean --keep-days 7
```

**模块化执行的优势：**
- ✅ 失败后可从断点继续，无需重新运行
- ✅ 可以手动编辑中间结果（如修改文章后再转换）
- ✅ 方便调试和测试单个模块
- ✅ 灵活组合不同功能

**使用场景示例：**

```bash
# 场景1：搜索失败后重试
uv run python wechat_editor_bot.py search --article-type financial_report --num-results 100
# 成功后继续
uv run python wechat_editor_bot.py generate

# 场景2：手动编辑文章后继续
uv run python wechat_editor_bot.py search
uv run python wechat_editor_bot.py generate
# 手动编辑 output/20260309_financial_report.md
uv run python wechat_editor_bot.py convert --input output/20260309_financial_report.md
uv run python wechat_editor_bot.py weather
uv run python wechat_editor_bot.py image
uv run python wechat_editor_bot.py upload

# 场景3：只生成图片（已有天气数据）
uv run python wechat_editor_bot.py weather
uv run python wechat_editor_bot.py image
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

### 模板配置文件

模板配置分为两个文件：

**1. 模板索引 (`config/article_templates.yaml`)**

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

**2. 模板详情 (`config/templates/*.yaml`)**

以财经日报模板为例 (`config/templates/financial_report.yaml`)：

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
  use_autoprompt: false  # 禁用自动优化，避免查询偏移
  search_type: "keyword"  # 搜索类型：keyword（精确）/ neural（语义）/ auto（自动）
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
    ## 二、市场表现
    ## 三、市场展望

  prompt: |
    根据提供的新闻素材撰写正文，参考以下结构（可根据内容灵活调整）...

footer:
  content: |
    本文内容仅供参考，不构成投资建议。
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
│   ├── bot/                     # 机器人核心模块
│   │   ├── config.py            # 配置管理和服务工厂
│   │   ├── commands.py          # 命令实现
│   │   ├── pipeline.py          # 工作流管道
│   │   └── mock_data.py         # Mock 数据
│   ├── cli/                     # 命令行模块
│   │   ├── parser.py            # CLI 参数解析
│   │   └── dispatcher.py        # 命令分发器
│   ├── exa_news_gatherer.py     # Exa 新闻采集
│   ├── article_generator.py     # AI 文章生成
│   ├── weather_service.py       # 天气服务
│   ├── image_generator.py       # 封面图生成
│   ├── wechat_publisher.py      # 微信 API 集成
│   ├── markdown_converter.py    # Markdown 到 HTML 转换
│   ├── file_manager.py          # 文件管理
│   ├── cache_manager.py         # 缓存管理（模块化执行）
│   └── news_gatherer.py         # 新闻采集接口
├── config/
│   ├── wechat_bot_config.yaml   # 主配置文件
│   ├── article_templates.yaml   # 模板配置索引
│   ├── templates/               # 文章模板配置
│   │   ├── financial_report.yaml
│   │   └── knowledge_explanation.yaml
│   ├── secrets.yaml             # 敏感配置（不提交）
│   └── secrets.yaml.example     # 配置模板
├── output/                      # 输出目录
│   ├── articles/                # Markdown 文章
│   ├── html/                    # 微信 HTML
│   ├── images/                  # 封面图片
│   └── archive/                 # 归档（30天+）
├── .cache/                      # 缓存目录（模块化执行）
│   ├── 20260309_news.json       # 新闻数据
│   ├── 20260309_article.json    # 文章元数据
│   ├── 20260309_weather.json    # 天气数据
│   ├── 20260309_images.json     # 图片元数据
│   └── 20260309_html.json       # HTML 元数据
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

# 周一早上 8:00 - 72小时（涵盖周末）
0 8 * * 1 cd /path/to/wechat-editor-bot && uv run python wechat_editor_bot.py --time-range 72 >> logs/cron.log 2>&1

# 周二到周五早上 8:00 - 使用默认24小时
0 8 * * 2-5 cd /path/to/wechat-editor-bot && uv run python wechat_editor_bot.py >> logs/cron.log 2>&1
```

**Crontab 时间字段说明：**
```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日 (1 - 31)
│ │ │ ┌───────────── 月 (1 - 12)
│ │ │ │ ┌───────────── 星期 (0 - 7，0和7都是周日)
│ │ │ │ │
* * * * * 要执行的命令
```

## 💰 成本估算

| 服务 | 月成本 | 说明 |
|------|--------|------|
| Exa API | ~$5-10 | 新闻搜索服务 |
| DeepSeek API | ~$1-2 | 30 篇文章 + 天气查询，极低成本 |
| 图片生成 | $1-30 | 取决于提供商（TuZi/OpenAI/Gemini） |
| **总计** | **$7-42** | 使用 DeepSeek 可大幅降低成本 |

## 🔧 故障排查

### 模块化执行相关

**查看当前状态：**
```bash
uv run python wechat_editor_bot.py status
```

**从失败步骤继续：**
```bash
# 如果 generate 步骤失败，修复后重新运行
uv run python wechat_editor_bot.py generate

# 继续后续步骤
uv run python wechat_editor_bot.py convert
uv run python wechat_editor_bot.py weather
uv run python wechat_editor_bot.py image
uv run python wechat_editor_bot.py upload
```

**清理缓存：**
```bash
# 清理所有缓存
uv run python wechat_editor_bot.py clean

# 清理指定日期
uv run python wechat_editor_bot.py clean --date 20260309

# 保留最近 7 天
uv run python wechat_editor_bot.py clean --keep-days 7
```

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

- 调整 `config/templates/` 中的模板配置
- 修改 `modules/article_generator.py` 中的提示词
- 调整新闻搜索的 `num_results` 获取更多新闻源

## 📚 命令行参数详解

### 参数分类说明

命令行参数分为两类：

| 类型 | 说明 | 示例 |
|------|------|------|
| **全局参数** | 用于完整流程，无子命令时生效 | `python wechat_editor_bot.py --article-type knowledge_explanation --topic "量化宽松"` |
| **子命令参数** | 需要先指定子命令，只对该子命令生效 | `python wechat_editor_bot.py search --time-range 72` |

---

### 全局参数（完整流程）

不指定子命令时，执行完整流程（搜索 → 生成 → 转换 → 天气 → 图片 → 上传）。

```bash
python wechat_editor_bot.py [全局参数]
```

**全局参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config FILE` | 配置文件路径 | config/wechat_bot_config.yaml |
| `--secrets FILE` | Secrets 文件路径 | config/secrets.yaml |
| `--mock` | Mock 模式（不调用真实 API） | - |
| `--article-type TYPE` | 文章类型 | financial_report |
| `--topic TEXT` | 搜索主题（替换模板中的 {topic} 占位符） | - |
| `--time-range HOURS` | 新闻搜索时间范围（小时），覆盖配置文件中的设置 | 使用配置文件值 |

**完整流程示例：**
```bash
# 使用默认配置（财经日报，24小时）
python wechat_editor_bot.py

# 生成知识解读（需要指定主题）
python wechat_editor_bot.py --article-type knowledge_explanation --topic "量化宽松"

# 覆盖时间范围为72小时（如周一涵盖周末）
python wechat_editor_bot.py --time-range 72

# 组合使用
python wechat_editor_bot.py --article-type financial_report --time-range 72
```

---

### 子命令参数（模块化执行）

#### search - 搜索新闻
```bash
python wechat_editor_bot.py search [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--article-type TYPE` | 文章类型 |
| `--topic TEXT` | 搜索主题（替换模板中的 {topic} 占位符） |
| `--date DATE` | 日期（格式：20260309） |
| `--time-range HOURS` | 时间范围（小时，如 24、48、168） |
| `--num-results NUM` | 结果数量 |
| `--enable-search` | 强制启用搜索（用于默认不搜索的类型） |
| `--output FILE` | 输出文件路径 |

---

#### generate - 生成文章
```bash
python wechat_editor_bot.py generate [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--news-file FILE` | 新闻数据文件（默认从缓存读取） |
| `--article-type TYPE` | 文章类型 |
| `--topic TEXT` | 自定义主题 |
| `--date DATE` | 日期 |
| `--output FILE` | 输出文件路径 |

---

#### convert - 转换为微信 HTML
```bash
python wechat_editor_bot.py convert [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--input FILE` | 输入 Markdown 文件（默认从缓存读取） |
| `--theme THEME` | 主题样式（warm/cool/professional） |
| `--date DATE` | 日期 |
| `--output FILE` | 输出文件路径 |

---

#### weather - 获取天气信息
```bash
python wechat_editor_bot.py weather [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--location LOCATION` | 位置（如 Beijing、Nanjing） |
| `--date DATE` | 日期 |
| `--output FILE` | 输出文件路径 |

---

#### image - 生成封面图片
```bash
python wechat_editor_bot.py image [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--weather-file FILE` | 天气数据文件（默认从缓存读取） |
| `--date DATE` | 日期 |
| `--output-dir DIR` | 输出目录 |

---

#### upload - 上传到微信
```bash
python wechat_editor_bot.py upload [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--html FILE` | HTML 文件 |
| `--image FILE` | 封面图文件 |
| `--title TEXT` | 文章标题 |
| `--markdown FILE` | Markdown 文件（用于提取标题） |
| `--date DATE` | 日期 |
| `--no-create-draft` | 不创建草稿（只上传图片） |

---

#### status - 查看状态
```bash
python wechat_editor_bot.py status [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--date DATE` | 日期（默认今天） |

---

#### clean - 清理缓存
```bash
python wechat_editor_bot.py clean [子命令参数]
```

**子命令参数：**
| 参数 | 说明 |
|------|------|
| `--date DATE` | 清理指定日期的缓存 |
| `--keep-days NUM` | 保留最近 N 天的文件 |
| `--cache-only` | 只清理缓存 |
| `--output-only` | 只清理输出文件 |

## 🎯 搜索参数详解

### `--topic` 参数说明

`--topic` 参数用于自定义搜索主题，会替换模板中的 `{topic}` 占位符。

**各文章类型的默认主题：**

| 文章类型 | 默认主题 | 模板配置 |
|----------|----------|----------|
| `financial_report` | 财经 | `"{topic} 财经新闻 股市行情 经济数据 宏观政策"` |
| `knowledge_explanation` | 知识 | `"{topic} 知识解读 背景 分析 案例"` |

**使用场景：**

```bash
# 指定主题搜索（知识解读）
uv run python wechat_editor_bot.py search --article-type knowledge_explanation --topic "量化宽松"
# 实际搜索：量化宽松 知识解读 背景 分析 案例
```

### Exa 搜索模式

Exa API 支持多种搜索模式，通过模板中的 `search_type` 配置：

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| `keyword` | 精确匹配关键词 | 主题明确、需要精准结果 |
| `neural` | 语义理解搜索 | 主题模糊、探索性搜索 |
| `auto` | 自动选择最佳模式 | 通用场景 |

**配置示例：**

```yaml
# config/templates/financial_report.yaml
news_search:
  search_type: "keyword"  # 使用精确关键词搜索
  use_autoprompt: false   # 禁用自动优化，避免查询偏移
```

## 📚 文档

- [安装指南](docs/INSTALL.md)
- [配置指南](docs/CONFIG_GUIDE.md)
- [样式指南](docs/STYLE_GUIDE.md)
- [缓存管理指南](docs/CACHE_GUIDE.md)

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
