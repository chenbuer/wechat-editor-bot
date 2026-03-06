# 财经新闻自动化系统 - 安装指南

## 系统要求

- Python 3.9+
- uv 或 pip
- 网络连接（用于 API 调用）

## 快速安装

### 使用 uv（推荐）

```bash
cd wechat-editor-bot

# 1. 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 同步依赖
uv sync

# 3. 验证安装
python tests/test_structure.py
```

### 使用 pip

```bash
cd wechat-editor-bot

# 1. 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -e .

# 3. 验证安装
python tests/test_structure.py
```

## 配置

### 1. 配置 API 密钥

复制示例配置文件并编辑：

```bash
cp config/secrets.yaml.example config/secrets.yaml
```

编辑 `config/secrets.yaml`：

```yaml
api:
  # Exa API（用于新闻搜索）
  # 注册地址: https://exa.ai
  exa_api_key: "your-exa-api-key"

  # DeepSeek API（用于文章生成）
  deepseek_key: "your-deepseek-api-key"
  deepseek_base_url: "https://api.deepseek.com"
  deepseek_model: "deepseek-chat"

  # 天气 API（可选，不配置则使用 AI 获取天气）
  weather_api_key: ""

  # 图片生成 API（必需）
  # 推荐使用兔子 API: https://api.tu-zi.com
  image_provider: "tuzi"
  image_key: "your-image-api-key"
  image_base_url: "https://api.tu-zi.com/v1"
  image_model: "doubao-seedream-4-5-251128"

# 微信公众号配置（必需，用于发布文章）
wechat:
  appid: "your-wechat-app-id"
  secret: "your-wechat-app-secret"
```

### 2. 自定义配置（可选）

编辑 `config/finance_news_config.yaml` 调整参数：

```yaml
news:
  exa_search:
    query: "最新财经新闻 股市行情 A股港股美股指数 经济数据指标 宏观政策 国际经济动态"
    num_results: 50
    use_autoprompt: true
    time_range: "24h"
  exclude_keywords:
    - "加密货币"
    - "比特币"

article:
  min_length: 800
  max_length: 1500

image:
  primary_size: "900x383"
  style: "oil_painting"
```

## 测试运行

### 测试文章生成（推荐）

```bash
python tests/test_article_generation.py
```

这将：
- 使用 Exa API 采集真实新闻
- 使用 DeepSeek 生成文章
- 转换为微信 HTML 格式
- 保存到 `output/test/` 目录

### Mock 模式（不消耗 API 配额）

```bash
python wechat_editor_bot.py --mock
```

这将：
- 使用示例新闻数据
- 生成测试文章和封面图
- 保存到 `output/` 目录
- 不调用微信 API

### 生产模式

```bash
# 财经日报
python wechat_editor_bot.py --article-type financial_report

# 科技资讯
python wechat_editor_bot.py --article-type tech_news
```

这将：
- 使用 Exa API 采集真实新闻
- 使用 DeepSeek 生成文章
- 生成封面图片
- 上传到微信并创建草稿

## 验证安装

运行结构验证脚本：

```bash
python tests/test_structure.py
```

应该看到所有项目文件和目录都标记为 ✅。

## 常见问题

### 问题 1: Exa API Key 未配置

```
未配置 Exa API Key
```

**解决方案**: 在 `config/secrets.yaml` 中配置 `exa_api_key`

```bash
cp config/secrets.yaml.example config/secrets.yaml
# 编辑 config/secrets.yaml 添加 API Key
```

### 问题 2: DeepSeek API Key 未配置

```
未配置 DeepSeek API Key
```

**解决方案**: 在 `config/secrets.yaml` 中配置 `deepseek_key`

### 问题 3: 依赖安装失败

```
ModuleNotFoundError: No module named 'yaml'
```

**解决方案**: 重新安装依赖

```bash
uv sync
# 或
pip install -e .
```

### 问题 4: 微信 API 错误

```
获取 access_token 失败
```

**解决方案**: 检查 `config/secrets.yaml` 中的 `app_id` 和 `app_secret`

## 下一步

安装完成后：

1. **测试文章生成**: `python tests/test_article_generation.py`
2. **查看输出**: `ls -la output/test/`
3. **运行 Mock 模式**: `python wechat_editor_bot.py --mock`
4. **配置定时任务**: 参考 README.md 中的 cron 配置
5. **监控日志**: `tail -f wechat_editor_bot.log`

## 获取帮助

```bash
python wechat_editor_bot.py --help
```

## 相关文档

- [配置指南](../CONFIG_GUIDE.md) - 详细配置说明
- [Exa 迁移指南](../EXA_MIGRATION.md) - Exa API 使用说明
- [贡献指南](../CONTRIBUTING.md) - 开发指南

## 卸载

```bash
# 删除虚拟环境
rm -rf .venv

# 删除输出文件
rm -rf output/*

# 删除日志
rm -f wechat_editor_bot.log

# 删除缓存
rm -f output/.exa_cache.json
```
