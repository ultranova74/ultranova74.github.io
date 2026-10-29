#!/usr/bin/env python3
"""
每天从 pages/ 随机抽取文章，更新首页「文章介绍」区域（简洁列表风格）
"""

import random
import datetime
import re
from pathlib import Path

PAGES_DIR = "pages"
INDEX_FILE = "index.html"
SAMPLE_SIZE = 10          # 每天显示多少篇

TZ = datetime.timezone(datetime.timedelta(hours=8))

def get_title(file_path: Path) -> str:
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read(4000)
            lower = content.lower()
            start = lower.find("<title>")
            if start != -1:
                end = lower.find("</title>", start)
                if end != -1:
                    title = content[start+7:end].strip()
                    if title:
                        return title
    except Exception:
        pass
    return file_path.stem

def main():
    today = datetime.datetime.now(TZ).date()
    pages_dir = Path(PAGES_DIR)

    if not pages_dir.exists():
        print(f"❌ 找不到 {PAGES_DIR} 目录")
        return

    all_files = [f for f in pages_dir.glob("**/*.html") if f.is_file()]
    if not all_files:
        print("❌ pages/ 下没有 HTML 文件")
        return

    selected = random.sample(all_files, min(SAMPLE_SIZE, len(all_files)))

    # 生成文章列表 HTML
    items = []
    for f in selected:
        title = get_title(f)
        rel = f.as_posix()
        items.append(f'          <li style="margin-bottom:14px; line-height:1.6;"><a href="{rel}" style="color:#1e40af; text-decoration:none; font-size:16px;">{title}</a></li>')

    articles_html = f"""    <section class="friend-link" id="friend-link">
        <h2 class="section-title">文章介绍</h2>
        <div class="link-list" style="max-width:900px; margin:0 auto; padding:20px 0;">
            <h2 style="text-align:center; font-size:22px; margin-bottom:8px; color:#1e293b;">今日精选文章</h2>
            <p style="text-align:center; color:#64748b; font-size:14px; margin-bottom:28px;">{today.isoformat()} 更新 · 共 {len(selected)} 篇精选</p>
            <ul style="list-style:none; padding:0 20px; margin:0;">
{chr(10).join(items)}
            </ul>
            <p style="text-align:center; margin-top:30px; color:#94a3b8; font-size:13px;">本站共收录 {len(all_files)} 篇文章 · 每日自动随机更新</p>
        </div>
    </section>"""

    # 读取并替换
    with open(INDEX_FILE, encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- ARTICLES:START -->.*?<!-- ARTICLES:END -->"
    if not re.search(pattern, content, re.S):
        print("❌ index.html 中缺少 <!-- ARTICLES:START --> 和 <!-- ARTICLES:END --> 标记")
        return

    new_content = re.sub(pattern, f"<!-- ARTICLES:START -->\n{articles_html}\n<!-- ARTICLES:END -->", content, flags=re.S)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ 首页文章区域已更新 | 总文章：{len(all_files)} | 今日精选：{len(selected)} | 日期：{today}")

if __name__ == "__main__":
    main()
