# 缓存管理指南

## 概述

系统支持模块化执行，每个步骤的中间结果都会缓存到 `.cache/` 目录。这使得失败后可以从断点继续，无需重新运行完整流程。

## 缓存目录结构

```
.cache/
├── 20260309_news.json        # 新闻数据
├── 20260309_article.json     # 文章元数据（标题、路径等）
├── 20260309_weather.json     # 天气数据
├── 20260309_images.json      # 图片元数据
└── 20260309_html.json        # HTML 元数据
```

## 缓存文件说明

### 1. 新闻缓存 (`*_news.json`)

```json
{
  "date": "20260309",
  "timestamp": "2026-03-09T10:00:00",
  "article_type": "financial_report",
  "news": [
    {
      "title": "新闻标题",
      "url": "https://example.com/news",
      "summary": "新闻摘要",
      "published_date": "2026-03-09"
    }
  ]
}
```

### 2. 文章元数据缓存 (`*_article.json`)

```json
{
  "date": "20260309",
  "article_type": "financial_report",
  "md_path": "output/articles/20260309_financial_report.md",
  "title": "财经早报 | 20260309",
  "topic": null
}
```

### 3. 天气数据缓存 (`*_weather.json`)

```json
{
  "location": "Nanjing",
  "condition": "晴",
  "temperature": "15",
  "description": "晴朗，微风",
  "timestamp": "2026-03-09T10:00:00"
}
```

### 4. 图片元数据缓存 (`*_images.json`)

```json
{
  "date": "20260309",
  "primary_path": "output/images/cover-20260309-primary.jpg",
  "secondary_path": null,
  "media_id": "media_id_1",
  "secondary_media_id": null
}
```

### 5. HTML 元数据缓存 (`*_html.json`)

```json
{
  "date": "20260309",
  "html_path": "output/html/20260309_financial_report.html"
}
```

## 模块化执行

### 查看当前状态

```bash
python wechat_editor_bot.py status
```

输出示例：
```
============================================================
[状态] 20260309
============================================================
✅ 新闻搜索: 已完成
   └─ 新闻数量: 50 条
⏳ 文章生成: 未完成
⏳ HTML 转换: 未完成
⏳ 天气获取: 未完成
⏳ 图片生成: 未完成

💡 下一步: python wechat_editor_bot.py generate
============================================================
```

### 从断点继续

如果某个步骤失败，修复后可以直接从该步骤继续：

```bash
# 假设 generate 步骤失败
python wechat_editor_bot.py generate

# 成功后继续后续步骤
python wechat_editor_bot.py convert
python wechat_editor_bot.py weather
python wechat_editor_bot.py image
python wechat_editor_bot.py upload
```

### 手动编辑中间结果

```bash
# 搜索新闻
python wechat_editor_bot.py search

# 生成文章
python wechat_editor_bot.py generate

# 手动编辑文章
vim output/articles/20260309_financial_report.md

# 继续后续步骤（使用修改后的文章）
python wechat_editor_bot.py convert --input output/articles/20260309_financial_report.md
```

## 清理缓存

### 清理所有缓存

```bash
python wechat_editor_bot.py clean
```

### 清理指定日期的缓存

```bash
python wechat_editor_bot.py clean --date 20260309
```

### 保留最近 N 天的文件

```bash
python wechat_editor_bot.py clean --keep-days 7
```

### 只清理缓存

```bash
python wechat_editor_bot.py clean --cache-only
```

### 只清理输出文件

```bash
python wechat_editor_bot.py clean --output-only
```

## 缓存策略

### 新闻缓存

- **时效性**: Exa API 有 1 小时缓存，同一小时内多次运行使用缓存
- **失败回退**: API 失败时使用旧缓存
- **缓存文件**: `output/.exa_cache.json`（独立缓存）

### 文章元数据缓存

- **覆盖策略**: 每次生成新文章时覆盖旧缓存
- **用途**: 存储文章标题、路径等元信息，供后续步骤使用

### 天气数据缓存

- **时效性**: 建议每次运行都重新获取
- **Mock 模式**: 使用默认天气数据

### 图片元数据缓存

- **上传状态**: 记录图片是否已上传到微信
- **Media ID**: 存储微信返回的 media_id

## 最佳实践

### 1. 定期清理

```bash
# 每周清理一次，保留最近 7 天
python wechat_editor_bot.py clean --keep-days 7
```

### 2. 失败重试

```bash
# 查看状态
python wechat_editor_bot.py status

# 从失败步骤继续
python wechat_editor_bot.py <failed_command>
```

### 3. 手动介入

```bash
# 生成文章后手动编辑
python wechat_editor_bot.py generate
vim output/articles/20260309_financial_report.md

# 使用编辑后的文章继续
python wechat_editor_bot.py convert --input output/articles/20260309_financial_report.md
```

### 4. 调试模式

```bash
# 只运行某个步骤进行调试
python wechat_editor_bot.py search --time-range 168 --num-results 100
python wechat_editor_bot.py generate --article-type knowledge_explanation --topic "量化宽松"
```

## 故障排除

### 缓存文件损坏

```bash
# 清理指定日期的缓存
python wechat_editor_bot.py clean --date 20260309

# 重新运行
python wechat_editor_bot.py
```

### 找不到缓存

```bash
# 查看当前状态
python wechat_editor_bot.py status

# 如果某个步骤未完成，重新运行该步骤
python wechat_editor_bot.py <command>
```

### 手动删除缓存

```bash
# 删除所有缓存
rm -rf .cache/*

# 删除指定日期的缓存
rm .cache/20260309_*.json
```

## 相关文档

- [安装指南](INSTALL.md) - 系统安装和配置
- [配置指南](CONFIG_GUIDE.md) - 详细配置说明
- [README](../README.md) - 项目概述
