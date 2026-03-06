# Tests

测试文件目录。

## 测试文件

- `test_article_generation.py` - 完整文章生成测试（使用真实 Exa API）
- `test_structure.py` - 项目结构验证

## 运行测试

```bash
# 完整文章生成测试（需要配置 API Key）
python tests/test_article_generation.py

# 项目结构验证
python tests/test_structure.py

# Mock 模式完整流程测试（不消耗 API 配额）
python wechat_editor_bot.py --mock
```

## 测试说明

### test_article_generation.py
测试完整的文章生成流程：
1. 使用 Exa API 采集真实新闻
2. 使用 DeepSeek 生成文章
3. 转换为微信 HTML 格式
4. 保存到 `output/test/` 目录

**要求**: 需要在 `config/secrets.yaml` 中配置 `exa_api_key` 和 `deepseek_key`

### test_structure.py
验证项目文件和目录结构是否完整。

## 添加新测试

1. 在此目录创建 `test_*.py` 文件
2. 使用 Mock 模式避免消耗 API 配额
3. 确保测试可独立运行
4. 添加必要的文档说明
