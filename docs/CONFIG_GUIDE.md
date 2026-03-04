# 配置文件说明

## 配置文件结构

项目使用两个配置文件：

### 1. `config/finance_news_config.yaml` - 常规配置
包含非敏感的业务配置，可以提交到 Git。

### 2. `config/secrets.yaml` - 敏感配置
包含 API 密钥、AppID 等敏感信息，**不应提交到 Git**（已在 .gitignore 中）。

## 配置详解

### finance_news_config.yaml

```yaml
# 新闻采集配置
news:
  # 新闻源配置（可自定义）
  sources:
    - name: "财联社"
      enabled: true
      priority: 1  # 优先级：1-5，数字越小优先级越高
    - name: "金十数据"
      enabled: true
      priority: 1
    - name: "雪球"
      enabled: true
      priority: 2
    - name: "央视新闻"
      enabled: true
      priority: 2
    - name: "新浪财经"
      enabled: true
      priority: 3
    - name: "东方财富"
      enabled: true
      priority: 3

  # 搜索关键词
  search_keywords:
    - "股市 财经"
    - "经济 金融"
    - "A股 市场"
    - "宏观经济"

  # 排除关键词
  exclude_keywords:
    - "加密货币"
    - "比特币"
    - "政治"
    - "赌博"

  time_range: "24h"          # 新闻时间范围
  max_sources: 10            # 最大新闻数量
  enable_deduplication: true # 启用去重

# 文章生成配置
article:
  # 文章标题格式
  title_format: "不大早的财经早报 | {date}"  # {date} 会被替换为日期

  # 文章结构（可自定义）
  sections:
    - name: "编者按"
      enabled: true
      emoji: "📝"
    - name: "新闻速递"
      enabled: true
      emoji: "📰"
      subsections:
        - "国内要闻"
        - "国际动态"
    - name: "股市表现"
      enabled: true
      emoji: "📊"
      subsections:
        - "A股市场"
        - "美股市场"
        - "全球市场"
    - name: "市场展望"
      enabled: true
      emoji: "🔮"
    - name: "免责声明"
      enabled: true
      emoji: "⚠️"

  # 文章风格
  style: "professional_engaging"  # 专业且引人入胜
  min_length: 1200           # 最小字数
  max_length: 1800           # 最大字数
  include_summary: true
  language: "zh-CN"
  tone: "neutral"            # neutral, optimistic, cautious
  add_disclaimer: true

  # 排版选项
  use_emoji: true            # 使用 emoji
  use_section_numbers: true  # 使用章节编号（一、二、三）
  use_bold: true             # 使用加粗强调
  use_dividers: true         # 使用分隔线

# 图片生成配置
image:
  primary_size: "900x383"    # 微信公众号主图尺寸
  secondary_size: "500x500"  # 备用尺寸
  style: "oil_painting"      # 图片风格
  mood: "relaxing"           # 氛围：relaxing, energetic, professional
  quality: "high"            # low, medium, high
  enable_compression: true   # 自动压缩到 2MB 以下
  max_size_mb: 2.0          # 最大文件大小（微信限制）
  fallback_enabled: true     # 启用降级策略（API 失败时使用默认图片）
  weather_based: true        # 根据天气生成图片

# 天气服务配置
weather:
  location: "Shanghai"       # 城市名称（支持中英文）
  provider: "ai"             # 天气数据来源：ai（使用 AI 生成）
  enable_weather_based_image: true  # 根据天气生成图片

# 微信发布配置
wechat:
  auto_publish: false        # 安全起见：仅创建草稿，不自动发布
  create_draft: true         # 创建草稿
  theme: "ocean"             # HTML 主题：fresh, ocean
  author: "财经日报"          # 文章作者
  enable_comment: false      # 是否开启评论
  only_fans_comment: false   # 是否仅粉丝可评论

# 文件管理配置
cleanup:
  keep_days: 30              # 保留天数
  archive_enabled: true      # 启用归档
  archive_path: "output/archive"  # 归档路径

# 日志配置
logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  file: "finance_news_bot.log"
  max_size_mb: 10
  backup_count: 5

# 重试配置
retry:
  max_attempts: 3            # 最大重试次数
  delay_seconds: 5           # 重试延迟（秒）
  exponential_backoff: true  # 指数退避

# 运行模式
mode:
  mock: false                # Mock 模式（测试用）
  dry_run: false             # 干运行（不实际发布）
  verbose: false             # 详细输出
```

### secrets.yaml

```yaml
# 微信公众号配置
wechat:
  appid: "wx_your_appid"
  secret: "your_wechat_secret"

# API 配置
api:
  # DeepSeek API（推荐，用于文章生成和天气获取）
  deepseek_key: "sk-xxxxx"
  deepseek_base_url: "https://api.deepseek.com"
  deepseek_model: "deepseek-chat"

  # Claude API（备选）
  anthropic_key: "sk-ant-xxxxx"

  # 图片生成 API
  image_provider: "tuzi"  # 可选: openai, tuzi, gemini, modelscope
  image_key: "your_image_api_key"
  image_base_url: "https://api.tu-zi.com/v1"
  image_model: "doubao-seedream-4-5-251128"
```

## 本地开发配置

### 方法 1: 使用 secrets.yaml（推荐）

1. 复制模板文件：
   ```bash
   cp config/secrets.yaml.template config/secrets.yaml
   ```

2. 编辑 `config/secrets.yaml` 填入真实值

3. 运行程序：
   ```bash
   python finance_news_bot.py
   ```

### 方法 2: 使用环境变量

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export IMAGE_API_KEY="sk-..."
python finance_news_bot.py
```

### 方法 3: 自定义 secrets 路径

```bash
python finance_news_bot.py --secrets /path/to/my-secrets.yaml
```

## GitHub Actions 配置

### 1. 设置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

- `WECHAT_APPID` - 微信公众号 AppID
- `WECHAT_SECRET` - 微信公众号 Secret
- `ANTHROPIC_API_KEY` - Claude API Key
- `IMAGE_API_KEY` - 图片生成 API Key
- `IMAGE_BASE_URL` - 图片 API 地址
- `IMAGE_PROVIDER` - 图片提供商（tuzi/openai）
- `IMAGE_MODEL` - 图片模型名称

### 2. 工作流配置示例

创建 `.github/workflows/daily-news.yml`：

```yaml
name: Daily Financial News

on:
  schedule:
    - cron: '0 0 * * *'  # 每天 UTC 00:00 (北京时间 08:00)
  workflow_dispatch:      # 手动触发

jobs:
  generate-news:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        cd auto-wechat
        pip install -r requirements.txt

    - name: Create secrets.yaml from GitHub Secrets
      run: |
        cd auto-wechat
        cat > config/secrets.yaml << EOF
        wechat:
          appid: "${{ secrets.WECHAT_APPID }}"
          secret: "${{ secrets.WECHAT_SECRET }}"
        api:
          anthropic_key: "${{ secrets.ANTHROPIC_API_KEY }}"
          image_key: "${{ secrets.IMAGE_API_KEY }}"
          image_base_url: "${{ secrets.IMAGE_BASE_URL }}"
          image_provider: "${{ secrets.IMAGE_PROVIDER }}"
          image_model: "${{ secrets.IMAGE_MODEL }}"
        EOF

    - name: Run financial news bot
      run: |
        cd auto-wechat
        python finance_news_bot.py

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: news-output
        path: |
          auto-wechat/output/articles/*.md
          auto-wechat/output/html/*.html
          auto-wechat/output/images/*.jpg
          auto-wechat/*.log
```

### 3. 手动触发工作流

在 GitHub 仓库的 Actions 页面，选择 "Daily Financial News" 工作流，点击 "Run workflow"。

## 配置优先级

程序按以下优先级读取配置：

1. 命令行参数（`--secrets`）
2. `config/secrets.yaml` 文件
3. 环境变量
4. 默认值

## 安全建议

### ✅ 应该做的

- 将 `secrets.yaml` 添加到 `.gitignore`
- 使用 GitHub Secrets 存储敏感信息
- 定期轮换 API 密钥
- 限制 API 密钥权限

### ❌ 不应该做的

- 不要将 `secrets.yaml` 提交到 Git
- 不要在代码中硬编码密钥
- 不要在日志中输出完整密钥
- 不要将密钥分享给他人

## 故障排查

### 问题 1: secrets.yaml 不存在

**错误信息：**
```
⚠️  Secrets 配置文件不存在: config/secrets.yaml
```

**解决方案：**
```bash
cp config/secrets.yaml.template config/secrets.yaml
# 编辑 config/secrets.yaml 填入真实值
```

### 问题 2: API Key 无效

**错误信息：**
```
ValueError: 未配置 ANTHROPIC_API_KEY
```

**解决方案：**
1. 检查 `config/secrets.yaml` 中的 `api.anthropic_key`
2. 或设置环境变量：`export ANTHROPIC_API_KEY="sk-ant-..."`

### 问题 3: 微信上传失败

**错误信息：**
```
获取 access_token 失败
```

**解决方案：**
检查 `config/secrets.yaml` 中的 `wechat.appid` 和 `wechat.secret` 是否正确。

## 配置验证

运行以下命令验证配置：

```bash
# 验证配置文件格式
python -c "import yaml; yaml.safe_load(open('config/finance_news_config.yaml'))"
python -c "import yaml; yaml.safe_load(open('config/secrets.yaml'))"

# 测试运行（Mock 模式）
python finance_news_bot.py --mock

# 查看配置加载日志
python finance_news_bot.py --mock 2>&1 | grep "配置"
```

## 示例配置

### 开发环境

```yaml
# finance_news_config.yaml
mode:
  mock: true
  dry_run: true
  verbose: true

logging:
  level: "DEBUG"
```

### 生产环境

```yaml
# finance_news_config.yaml
mode:
  mock: false
  dry_run: false
  verbose: false

logging:
  level: "INFO"

retry:
  max_attempts: 3
  delay_seconds: 10
```

## 更多信息

- 查看 `config/secrets.yaml.template` 了解完整的配置模板
- 查看 `QUICKREF.py` 了解常用命令
- 查看 `README.md` 了解项目概述
