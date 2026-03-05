#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转微信公众号 HTML 转换器
支持多主题：清新绿色、深海静谧
适配电脑端和手机端

从 md2wechat.py 移动到 modules 目录
"""

import markdown
import sys
import os
from pathlib import Path


# ============================================================================
# 主题定义
# ============================================================================

# 清新主题（绿色调）
FRESH_THEME = {
    'name': '清新绿色',
    'mood': '清新自然',
    'colors': '绿色调',
    'best_for': '生活随笔、自然主题',
    'background': '#f8faf8',
    'text': '#3a3a3a',
    'primary': '#42b983',
    'secondary': '#35a372',
    'caption_background': '#f0f9f4',
}

# 深海静谧主题（蓝色调）
OCEAN_THEME = {
    'name': '深海静谧',
    'mood': '深邃静谧',
    'colors': '蓝色调',
    'best_for': '技术文章、商业分析',
    'background': '#f0f4f8',
    'text': '#3a4150',
    'primary': '#4a7c9b',
    'secondary': '#3d6a8a',
    'caption_background': '#e8f0f8',
}

THEMES = {
    'fresh': FRESH_THEME,
    'ocean': OCEAN_THEME,
}


# ============================================================================
# CSS 生成函数
# ============================================================================

def generate_css(theme):
    """根据主题生成 CSS"""

    # 根据主题选择网格纹理
    if theme['name'] == '深海静谧':
        grid_pattern = f"background-image: linear-gradient(rgba(74, 124, 155, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(74, 124, 155, 0.03) 1px, transparent 1px); background-size: 24px 24px;"
        card_shadow = "box-shadow: 0 8px 28px rgba(58, 65, 80, 0.06), 0 0 16px rgba(74, 124, 155, 0.15);"
        border_radius = "14px"
        letter_spacing = "0.2px"
    else:
        grid_pattern = ""
        card_shadow = "box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);"
        border_radius = "12px"
        letter_spacing = "0.5px"

    return f"""
/* 主容器 */
.wechat-content {{
    background-color: {theme['background']};
    padding: 40px 16px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: {theme['text']};
    letter-spacing: {letter_spacing};
}}

/* 内容卡片 */
.content-card {{
    max-width: 800px;
    margin: 0 auto;
    background: #ffffff;
    {grid_pattern}
    padding: 25px;
    border-radius: {border_radius};
    {card_shadow}
    border: 1px solid rgba(0, 0, 0, 0.05);
}}

/* 标题样式 */
h1 {{
    font-size: 28px;
    font-weight: 600;
    color: {theme['secondary']};
    margin: 20px 0 12px;
    padding-bottom: 10px;
    border-bottom: 3px solid {theme['primary']};
    line-height: 1.4;
}}

/* 大章节标题 - 带背景色 */
h2 {{
    font-size: 22px;
    font-weight: 600;
    color: {theme['primary']};
    margin: 24px 0 3px;
    padding: 12px 16px;
    background: linear-gradient(135deg, {theme['caption_background']} 0%, rgba(255,255,255,0.5) 100%);
    border-bottom: 2px solid {theme['primary']};
    # border-radius: 6px;
    line-height: 1.4;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}}

/* 编者按标题不应用通用 h2 样式 */
.editor-note-card h2 {{
    background: none;
    border: none;
    box-shadow: none;
    padding: 14px 20px 10px 20px;
    margin: 0;
    font-size: 20px;
}}

h3 {{
    font-size: 18px;
    font-weight: 800;
    color: {theme['secondary']};
    margin: 16px 0 10px;
    line-height: 1.4;
    display: inline-block;
    padding-bottom: 4px;
    font-style: italic;
}}

h4, h5, h6 {{
    font-size: 17px;
    font-weight: 600;
    color: {theme['secondary']};
    margin: 14px 0 10px;
    line-height: 1.4;
}}

/* 段落 */
p {{
    margin: 3px 0;
    text-align: justify;
    color: {theme['text']};
    line-height: 1.75;
}}

/* 编者按卡片容器 */
.editor-note-card {{
    margin: 20px 0;
    border-left: 4px solid {theme['primary']};
    overflow: hidden;
}}

/* 编者按标题 */
.editor-note-title {{
    font-size: 20px;
    font-weight: 600;
    color: {theme['text']};
    margin: 0;
    padding: 14px 20px 10px 20px;
    line-height: 1.4;
}}

/* 编者按内容 */
.editor-note-content {{
    margin: 0;
    padding: 0 20px 14px 20px;
    text-align: justify;
    color: #555;
    line-height: 1.75;
    font-style: italic;
    font-size: 15px;
}}

/* 免责声明 - 小字提示 */
.disclaimer-text {{
    text-align: center;
    color: #999;
    font-size: 12px;
    line-height: 1.6;
    margin: 30px 0 20px;
    padding: 0 20px;
}}

/* 强调 */
strong {{
    color: {theme['secondary']};
    font-weight: 500;
}}

em {{
    color: {theme['primary']};
    font-style: italic;
}}

/* 链接 */
a {{
    color: {theme['primary']};
    text-decoration: none;
    border-bottom: 1px solid {theme['primary']};
    transition: all 0.3s;
}}

a:hover {{
    color: {theme['secondary']};
    border-bottom-color: {theme['secondary']};
}}

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

blockquote p {{
    margin: 6px 0;
    color: {theme['text']};
}}

/* 列表 */
ul, ol {{
    margin: 12px 0;
    padding-left: 28px;
}}

li {{
    margin: 6px 0;
    line-height: 1.75;
    color: {theme['text']};
}}

ul li {{
    list-style-type: disc;
}}

/* 代码 */
code {{
    background: {theme['caption_background']};
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', Consolas, monospace;
    font-size: 14px;
    color: #e74c3c;
}}

pre {{
    background: #2c3e50;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 20px 0;
}}

pre code {{
    background: transparent;
    color: {theme['primary']};
    padding: 0;
    font-size: 14px;
    line-height: 1.6;
}}

/* 表格 */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 15px;
}}

th {{
    background: {theme['primary']};
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
}}

td {{
    padding: 12px;
    border-bottom: 1px solid #e8e8e8;
    color: {theme['text']};
}}

tr:nth-child(even) {{
    background: #f9f9f9;
}}

/* 分割线 - 隐藏 */
hr {{
    display: none;
}}

/* 图片 */
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 16px auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}}

/* 响应式设计 */
@media (max-width: 768px) {{
    .wechat-content {{
        padding: 20px 12px;
    }}

    .content-card {{
        padding: 24px 16px;
        border-radius: 8px;
    }}

    h1 {{
        font-size: 24px;
    }}

    h2 {{
        font-size: 20px;
    }}

    h3 {{
        font-size: 18px;
    }}

    pre {{
        padding: 12px;
        font-size: 13px;
    }}

    table {{
        font-size: 14px;
    }}

    th, td {{
        padding: 8px;
    }}
}}
"""


def convert_markdown_to_html(markdown_file, output_file=None, title=None, theme='fresh'):
    """
    将 Markdown 文件转换为微信公众号 HTML

    Args:
        markdown_file: Markdown 文件路径
        output_file: 输出 HTML 文件路径（可选）
        title: HTML 标题（可选，默认使用文件名）
        theme: 主题名称 (fresh/ocean)

    Returns:
        生成的 HTML 内容
    """
    # 获取主题配置
    if theme not in THEMES:
        print(f"警告：未知主题 '{theme}'，使用默认主题 'fresh'")
        theme = 'fresh'

    theme_config = THEMES[theme]
    # 读取 Markdown 文件
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {markdown_file}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：读取文件失败 - {e}")
        sys.exit(1)

    # 配置 Markdown 扩展
    extensions = [
        'markdown.extensions.extra',      # 支持表格、代码块等
        'markdown.extensions.codehilite', # 代码高亮
        'markdown.extensions.toc',        # 目录
        'markdown.extensions.nl2br',      # 换行转 <br>
        'markdown.extensions.sane_lists', # 更好的列表支持
    ]

    # 转换 Markdown 为 HTML
    md = markdown.Markdown(extensions=extensions)
    content_html = md.convert(md_content)

    # 使用 BeautifulSoup 处理特殊样式
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content_html, 'html.parser')

    # 处理编者按卡片样式（第一个 h2 + 第一个 p 包装到 div 中）
    h2_tags = soup.find_all('h2')
    if h2_tags:
        first_h2 = h2_tags[0]
        next_p = first_h2.find_next_sibling('p')

        if next_p:
            # 创建一个 div 包装编者按
            editor_note_div = soup.new_tag('div', **{'class': 'editor-note-card'})

            # 修改 h2 和 p 的 class
            first_h2['class'] = 'editor-note-title'
            next_p['class'] = 'editor-note-content'

            # 将 h2 和 p 移到 div 中
            first_h2.insert_before(editor_note_div)
            editor_note_div.append(first_h2.extract())
            editor_note_div.append(next_p.extract())

        # 处理免责声明 - 查找包含"投资有风险"的段落
        all_p_tags = soup.find_all('p')
        for p in all_p_tags:
            if '投资有风险' in p.get_text():
                p['class'] = 'disclaimer-text'
                break

    content_html = str(soup)

    # 生成主题 CSS
    theme_css = generate_css(theme_config)

    # 如果没有指定标题，使用文件名
    if title is None:
        title = Path(markdown_file).stem

    # 生成完整的 HTML
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{theme_css}
    </style>
</head>
<body>
    <div class="wechat-content">
        <div class="content-card">
{content_html}
        </div>
    </div>
</body>
</html>"""

    # 输出到文件或标准输出
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_template)
            print(f"✅ 转换成功！输出文件：{output_file}")
        except Exception as e:
            print(f"错误：写入文件失败 - {e}")
            sys.exit(1)
    else:
        print(html_template)

    return html_template


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Markdown 转微信公众号 HTML 转换器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
主题说明：
  fresh  - 清新绿色主题（适合生活随笔、自然主题）
  ocean  - 深海静谧主题（适合技术文章、商业分析）

示例：
  python md2wechat.py article.md
  python md2wechat.py article.md -o output.html
  python md2wechat.py article.md -t ocean
  python md2wechat.py article.md -t ocean -o output.html
        """
    )

    parser.add_argument('input', help='输入的 Markdown 文件')
    parser.add_argument('-o', '--output', help='输出的 HTML 文件（默认：输入文件名.html）')
    parser.add_argument('-t', '--theme', choices=['fresh', 'ocean'], default='fresh',
                        help='主题选择（默认：fresh）')
    parser.add_argument('--title', help='HTML 标题（默认：文件名）')

    args = parser.parse_args()

    markdown_file = args.input
    output_file = args.output
    theme = args.theme
    title = args.title

    # 如果没有指定输出文件，自动生成
    if output_file is None:
        output_file = Path(markdown_file).stem + '.html'

    # 显示主题信息
    theme_info = THEMES[theme]
    print(f"🎨 使用主题：{theme_info['name']}")
    print(f"   风格：{theme_info['mood']}")
    print(f"   色调：{theme_info['colors']}")
    print(f"   适合：{theme_info['best_for']}")
    print()

    convert_markdown_to_html(markdown_file, output_file, title, theme)


if __name__ == '__main__':
    main()
