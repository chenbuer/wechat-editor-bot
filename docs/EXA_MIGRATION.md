# Exa API 迁移指南

## 概述

系统已从 RSS + Tushare 方案迁移到 Exa API 方案，以解决以下问题：
- RSS 源大部分失效或解析错误
- Tushare 免费账户权限不足
- 依赖包编译问题

## 主要变更

### 1. 新增模块
- `modules/exa_news_gatherer.py` - Exa API 集成模块

### 2. 更新模块
- `modules/news_gatherer.py` - 使用 Exa API 替代 RSS + Tushare

### 3. 删除模块
- `modules/rss_news_fetcher.py` - 已删除
- `modules/market_data_service.py` - 已删除

### 4. 配置变更
- `config/finance_news_config.yaml` - 添加 `exa_search` 配置
- `config/secrets.yaml.example` - 添加 `exa_api_key`，移除 `tushare_token`

### 5. 依赖变更
- `pyproject.toml` - 移除 `tushare` 和 `feedparser`

## 配置步骤

### 1. 获取 Exa API Key

访问 https://exa.ai 注册并获取 API Key。

### 2. 配置 secrets.yaml

编辑 `config/secrets.yaml`，添加所有必需的 API Key：

```yaml
api:
  # Exa API（用于新闻搜索）
  exa_api_key: "your-exa-api-key-here"

  # DeepSeek API（用于文章生成）
  deepseek_key: "your-deepseek-api-key"
  deepseek_base_url: "https://api.deepseek.com"
  deepseek_model: "deepseek-chat"

  # 天气 API（可选）
  weather_api_key: ""

  # 图片生成 API（必需）
  image_provider: "tuzi"
  image_key: "your-image-api-key"
  image_base_url: "https://api.tu-zi.com/v1"
  image_model: "doubao-seedream-4-5-251128"

# 微信公众号配置（必需）
wechat:
  appid: "your-wechat-app-id"
  secret: "your-wechat-app-secret"
```

### 3. 自定义搜索查询（可选）

编辑 `config/finance_news_config.yaml`，自定义搜索查询：

```yaml
news:
  exa_search:
    # 综合查询（覆盖所有主题）
    query: "最新财经新闻 股市行情 A股港股美股指数 经济数据指标 宏观政策 国际经济动态"
    num_results: 50
    use_autoprompt: true
    time_range: "24h"  # 24h 或 48h

    # 可选：指定高质量财经媒体
    include_domains:
      - "cailianshe.com"
      - "jin10.com"
      - "reuters.com"
      - "bloomberg.com"
```

### 4. 更新依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

## Exa API 优势

### 1. 单次请求获取所有内容
- 一次 API 调用获取 50 条新闻
- 覆盖财经新闻 + 市场数据
- 减少 API 调用次数，降低成本

### 2. 智能搜索
- 神经搜索（语义理解）
- 自动查询优化（`use_autoprompt`）
- 日期过滤、域名过滤

### 3. 内容提取
- 自动提取文章摘要
- 高亮关键信息
- 完整文本内容

### 4. 缓存机制
- 1 小时内不重复请求
- 缓存文件：`output/.exa_cache.json`
- API 失败时使用旧缓存

## 成本优化

### 缓存策略
- 同一小时内多次运行使用缓存
- 避免重复 API 调用
- 每天运行 1 次：每月约 30 次调用

### 查询优化
- 综合查询覆盖所有主题
- 客户端过滤排除无关内容
- 最大化单次请求价值

## 测试

运行测试脚本验证配置：

```bash
python test_article_generation.py
```

预期输出：
```
[步骤 1/3] 采集真实新闻（Exa API）
从 Exa 获取到多条新闻
✅ 采集到多条新闻

[步骤 2/4] 生成文章
✅ Markdown 已保存: ...

[步骤 3/4] 转换为微信 HTML
✅ HTML 已保存: ...
```

## 故障排除

### 问题 1: "Exa API Key 未配置"
**解决方案**: 检查 `config/secrets.yaml` 中是否正确配置了 `exa_api_key`

### 问题 2: API 调用失败
**解决方案**:
1. 检查 API Key 是否有效
2. 检查网络连接
3. 查看 `output/.exa_cache.json` 是否有旧缓存可用

### 问题 3: 返回结果太少
**解决方案**:
1. 调整 `time_range` 为 `48h`
2. 修改 `query` 使其更宽泛
3. 移除 `include_domains` 限制

### 问题 4: 返回无关内容
**解决方案**:
1. 添加更多 `exclude_keywords`
2. 启用 `include_domains` 过滤
3. 优化 `query` 使其更精确

## 回滚方案

如需回滚到旧版本：

```bash
git checkout HEAD~1 modules/news_gatherer.py
git checkout HEAD~1 modules/rss_news_fetcher.py
git checkout HEAD~1 modules/market_data_service.py
git checkout HEAD~1 config/finance_news_config.yaml
git checkout HEAD~1 pyproject.toml
```

## 支持

如有问题，请查看：
- Exa API 文档: https://docs.exa.ai
- 项目 README: README.md
- 配置指南: CONFIG_GUIDE.md
