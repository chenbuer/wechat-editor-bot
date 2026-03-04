# Financial News Automation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

自动化财经新闻采集、文章生成和微信公众号发布系统。每天自动生成专业财经日报，配以天气主题封面图，一键发布到微信公众号。

## ✨ 核心特性

- 🔍 **智能新闻采集** - 基于关键词自动搜索 24 小时财经新闻，过滤敏感内容
- ✍️ **AI 文章生成** - 使用 DeepSeek/Claude API 生成专业、易读的财经文章（1200-1800 字）
- 🌤️ **AI 天气服务** - 使用 DeepSeek AI 获取实时天气信息
- 🎨 **天气主题封面** - 根据实时天气生成油画风格封面图（晴天/阴天/雨天不同风格）
- 📱 **微信自动发布** - 自动转换为微信格式并创建草稿（支持人工审核）
- 🗂️ **文件自动管理** - 30 天自动归档，保持目录整洁
- 🎨 **精美排版** - 编者按卡片样式，小字免责声明，无分割线干扰
- ⚙️ **高度可配置** - 新闻源、文章结构、样式主题均可自定义

## 🚀 快速开始

### 前置要求

- Python 3.9+
- 微信公众号（服务号或认证订阅号）
- DeepSeek API Key（文章生成 + 天气获取，推荐）或 Claude API Key
- 图片生成 API（TuZi/OpenAI/Gemini/ModelScope 任选其一）

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd auto-wechat

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
uv run python finance_news_bot.py --mock

# 生产模式（真实 API 调用）
uv run python finance_news_bot.py

# 自定义配置文件
uv run python finance_news_bot.py --config custom_config.yaml --secrets custom_secrets.yaml
```

## 📁 项目结构

```
auto-wechat/
├── finance_news_bot.py          # 主程序入口
├── pyproject.toml               # 项目配置和依赖
├── uv.lock                      # 依赖锁定文件
├── modules/                     # 核心模块
│   ├── news_gatherer.py         # 新闻采集
│   ├── article_generator.py     # AI 文章生成
│   ├── weather_service.py       # 天气服务
│   ├── image_generator.py       # 封面图生成
│   ├── wechat_publisher.py      # 微信 API 集成
│   ├── markdown_converter.py    # Markdown → 微信 HTML
│   └── file_manager.py          # 文件管理
├── config/
│   ├── finance_news_config.yaml # 常规配置
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

**finance_news_config.yaml**（常规配置）：

```yaml
news:
  sources:
    - name: "财联社"
      enabled: true
      priority: 1
    - name: "金十数据"
      enabled: true
      priority: 1
    - name: "雪球"
      enabled: true
      priority: 2
  search_keywords: ["股市 财经", "经济 金融", "A股 市场"]
  exclude_keywords: ["加密货币", "比特币", "政治"]
  max_sources: 10

article:
  title_format: "不大早的财经早报 | {date}"
  min_length: 1200
  max_length: 1800
  style: "professional_engaging"
  sections:
    - name: "编者按"
      enabled: true
      emoji: "📝"
    - name: "新闻速递"
      enabled: true
      emoji: "📰"
    - name: "股市表现"
      enabled: true
      emoji: "📊"
    - name: "市场展望"
      enabled: true
      emoji: "🔮"

image:
  primary_size: "900x383"  # 微信主图尺寸
  style: "oil_painting"
  mood: "relaxing"

weather:
  location: "Shanghai"
  provider: "ai"  # 使用 AI 获取天气

wechat:
  create_draft: true
  auto_publish: false  # 强烈建议保持 false，人工审核后发布
  theme: "ocean"  # 主题：ocean（深海静谧）或 fresh（清新绿色）
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

### 方式 2：本地 Cron

```bash
crontab -e

# 每天 8:00 运行
0 8 * * * cd /path/to/auto-wechat && uv run python finance_news_bot.py >> logs/cron.log 2>&1
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
tail -f finance_news_bot.log
```

### 微信上传失败

- 检查 appid/secret 是否正确
- 确认公众号类型支持素材管理接口
- 图片大小 < 2MB（系统会自动压缩）
- 查看[微信错误码文档](https://developers.weixin.qq.com/doc/offiaccount/Return_codes/Return_code_descriptions_new.html)

### 天气获取失败

- 确认 DeepSeek API Key 已配置
- 检查 `weather.provider` 设置为 `"ai"`
- 查看日志中的错误信息

### 文章质量不佳

- 调整 `config/finance_news_config.yaml` 中的 `article.style`
- 修改 `modules/article_generator.py` 中的提示词
- 增加 `news.max_sources` 获取更多新闻源

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
