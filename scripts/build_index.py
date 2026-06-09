#!/usr/bin/env python3
"""生成 docs/index.html 章节列表。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"29", "32"}


def main():
    meta_path = ROOT / "data" / "chapters_meta.json"
    chapters = json.loads(meta_path.read_text()) if meta_path.exists() else []
    cards = []
    for c in chapters:
        num = c["num"]
        if num in SKIP:
            continue
        story = ROOT / "stories" / f"ch{num}.md"
        ready = story.exists()
        cls = "card ready" if ready else "card pending"
        href = f"ch{num}.html" if ready else "#"
        cards.append(
            f'        <a class="{cls}" href="{href}">\n'
            f'          <span class="num">{num}</span>\n'
            f'          <span class="title">第 {int(num)} 章</span>\n'
            f'          <span class="meta">{c["count"]} 词</span>\n'
            f"        </a>"
        )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>宋鹏浩 · 雅思单词故事</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <h1>雅思单词记忆故事</h1>
    <p class="subtitle">《雅思核心词汇精讲精练》宋鹏昊 · 每章一个故事</p>
  </header>

  <main class="container">
    <section class="intro">
      <p>把每章单词编进连贯故事，读一遍故事，记住一整章词汇。第 29、32 章笔记缺失，暂未生成。</p>
    </section>

    <section class="chapters">
      <h2>章节列表</h2>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </section>
  </main>

  <footer>
    <p>词源：宋鹏浩1600-Total.docx · <a href="https://github.com/dreamsilcon/ielts-vocab">GitHub</a></p>
  </footer>
</body>
</html>
"""
    out = ROOT / "docs" / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"生成 {out}（{len([c for c in chapters if c['num'] not in SKIP])} 章）")


if __name__ == "__main__":
    main()
