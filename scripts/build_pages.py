#!/usr/bin/env python3
"""从 stories/chXX.md 生成 docs/chXX.html。"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KW_RE = re.compile(r"<b>([^<]+)</b>\s*(/[^/\s][^/]*/)")
ZH_KW_RE = re.compile(r"<b>([^<]+)</b>\(([^)]+)\)")


def en_to_html(text: str) -> str:
    return KW_RE.sub(
        r'<span class="w">'
        r'<strong class="kw">\1</strong>'
        r'<span class="ipa">\2</span>'
        r"</span>",
        text,
    )


def zh_to_html(text: str) -> str:
    text = text.removeprefix("zh:").strip()
    return ZH_KW_RE.sub(
        r'<span class="w-cn">'
        r"<strong>\1</strong>"
        r'<span class="en-ref">(\2)</span>'
        r"</span>",
        text,
    )


def parse_story_blocks(md: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_story = False
    pending_en: str | None = None

    for line in md.splitlines():
        if line.startswith("## Story"):
            in_story = True
            continue
        if line.startswith("## ") and in_story:
            break
        if not in_story or not line.strip():
            continue
        if line.startswith("zh:"):
            if pending_en:
                blocks.append((pending_en, line))
                pending_en = None
            continue
        pending_en = line
    return blocks


def md_to_html_body(md: str) -> str:
    html_parts = ["<h2>Story</h2>"]
    for en, zh in parse_story_blocks(md):
        html_parts.append(
            '<div class="block">'
            f'<p class="en">{en_to_html(en)}</p>'
            f'<p class="zh">{zh_to_html(zh)}</p>'
            "</div>"
        )

    if re.search(r"^## Coverage", md, re.M):
        html_parts.append("<h2>Coverage</h2>")
        for line in md.splitlines():
            if line.startswith("- "):
                html_parts.append(f'<p class="coverage">{line[2:]}</p>')
    return "\n      ".join(html_parts)


def build(ch: str):
    ch = ch.zfill(2)
    md_path = ROOT / "stories" / f"ch{ch}.md"
    if not md_path.exists():
        print(f"缺少 {md_path}")
        sys.exit(1)
    md = md_path.read_text(encoding="utf-8")
    title_m = re.search(r"^# (.+)$", md, re.M)
    title = title_m.group(1) if title_m else f"Chapter {int(ch)}"
    body = md_to_html_body(md)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <a class="nav-back" href="index.html">← 返回目录</a>
    <header class="story-header">
      <h1>{title}</h1>
      <p class="tag">英文故事 + 中文对照 · 关键词高亮</p>
    </header>
    <article class="story-body">
      {body}
    </article>
  </div>
  <footer><p><a href="index.html">← 返回目录</a></p></footer>
</body>
</html>
"""
    out = ROOT / "docs" / f"ch{ch}.html"
    out.write_text(html, encoding="utf-8")
    print(f"生成 {out}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "01")
