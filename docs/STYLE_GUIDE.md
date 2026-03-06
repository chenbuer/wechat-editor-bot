# 文章样式指南

本文档说明财经早报的样式设计和自定义方法。

## 📐 样式概览

### 今日看点（Summary）
- **位置**: 文章开头，标题下方
- **样式**:
  - 使用 blockquote 容器
  - 左侧主题色边框（6px）
  - 主题色背景
  - 圆角（4px）
  - 内阴影效果
- **内容**:
  - 标题：22px，加粗，主题色（如 💡 今日看点）
  - 正文：16px，斜体，灰色

### 章节标题
- **大章节**（一、二、三、）:
  - 22px 字号
  - 渐变背景
  - 左侧蓝色边框
  - 圆角和阴影
- **小章节**（A股市场、美股市场等）:
  - 18px 字号
  - 底部蓝色下划线
  - 无背景

### 免责声明
- **样式**:
  - 12px 小字
  - 居中显示
  - 灰色文字（#999）
  - 无标题，简洁美观
- **内容**: "本文内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。关注我们，获取更多财经资讯。"

### 分割线
- 所有 `<hr>` 标签设置为 `display: none`
- 章节之间无视觉分割线

## 🎨 主题配置

系统支持两种主题，在 `config/finance_news_config.yaml` 中配置：

```yaml
wechat:
  theme: "ocean"  # 或 "fresh"、"warm"
```

### Ocean 主题（深海静谧）
- **主色**: #4a7c9b（深蓝）
- **背景**: #f0f4f8（浅蓝灰）
- **适合**: 技术文章、商业分析、财经报道
- **特点**: 专业、沉稳、现代

### Fresh 主题（清新绿色）
- **主色**: #42b983（绿色）
- **背景**: #f8faf8（浅绿灰）
- **适合**: 生活随笔、自然主题
- **特点**: 清新、活泼、自然

### Warm 主题（热情红色）
- **主色**: #5f0101
- **背景**: 
- **适合**: 
- **特点**:
## 🛠️ 自定义样式

### 修改"今日看点"样式

编辑 `modules/markdown_converter.py`，找到 `blockquote` 部分：

```python
/* 引用块 */
blockquote {{
    margin: 16px 0;
    padding: 14px 18px;
    background: {theme['caption_background']};
    border-left: 6px solid {theme['primary']};
    border-radius: 4px;
    color: {theme['text']};
    font-style: italic;
    box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.05);
}}
```

### 修改免责声明样式

找到 `.disclaimer-text` 部分：

```python
/* 免责声明 - 小字提示 */
.disclaimer-text {{
    text-align: center;
    color: #999;
    font-size: 12px;
    line-height: 1.6;
    margin: 30px 0 20px;
    padding: 0 20px;
}}
```

### 修改章节标题样式

找到 `h2` 部分：

```css
/* 大章节标题 - 带背景色 */
h2 {{
    font-size: 22px;
    font-weight: 600;
    color: {theme['primary']};
    margin: 20px 0 12px;
    padding: 12px 16px;
    background: linear-gradient(135deg, {theme['caption_background']} 0%, rgba(255,255,255,0.5) 100%);
    border-left: 4px solid {theme['primary']};
    border-radius: 6px;
    line-height: 1.4;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}}
```

## 📱 微信适配

### 样式内联化
系统使用 `premailer` 自动将 CSS 内联化，确保在微信公众号中正确显示。

### 图片尺寸
- **主图**: 900x383（微信推荐尺寸）
- **最大文件大小**: 2MB（自动压缩）

### 字体大小
- **标题**: 20-28px
- **正文**: 15-16px
- **小字**: 12-14px

### 颜色使用
- 避免使用纯黑（#000），使用深灰（#3a4150）
- 链接颜色使用主题色
- 强调文字使用主题辅助色

## 🔧 常见问题

### Q: 如何修改文章标题格式？
A: 编辑 `config/finance_news_config.yaml`:
```yaml
article:
  title_format: "财经早报 | {date}"
```

### Q: 如何调整间距？
A: 修改 `markdown_converter.py` 中的 `margin` 和 `padding` 值。

### Q: 如何添加新的样式类？
A:
1. 在 `generate_css()` 函数中添加 CSS 规则
2. 在 `convert_markdown_to_html()` 中使用 BeautifulSoup 添加 class
3. 测试并验证样式

### Q: 样式在微信中显示不正确？
A:
- 检查是否使用了微信不支持的 CSS 属性
- 确认 premailer 正确内联化了样式
- 查看生成的 HTML 文件，检查内联样式

## 📚 参考资源

- [微信公众号排版规范](https://mp.weixin.qq.com/)
- [Premailer 文档](https://github.com/peterbe/premailer)
- [Python Markdown 扩展](https://python-markdown.github.io/extensions/)
