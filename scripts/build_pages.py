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
        r'<strong class="kw">\1</strong><span class="ipa">\2</span>',
        text,
    )


def zh_to_html(text: str) -> str:
    text = text.removeprefix("zh:").strip()
    return ZH_KW_RE.sub(
        r'<strong class="kw-cn">\1</strong>(\2)',
        text,
    )


def md_to_html_body(md: str) -> str:
    html_parts = []
    in_story = False
    for line in md.splitlines():
        if line.startswith("#") or line.startswith(">") or line.startswith("---"):
            continue
        if line.startswith("## Story"):
            in_story = True
            html_parts.append("<h2>Story</h2>")
            continue
        if line.startswith("## "):
            in_story = False
            html_parts.append(f"<h2>{line[3:]}</h2>")
            continue
        if line.startswith("- "):
            html_parts.append(f'<p class="coverage">{line[2:]}</p>')
            continue
        if not line.strip():
            continue
        if line.startswith("zh:"):
            html_parts.append(
                f'<p class="zh">{zh_to_html(line)}</p></div>'
            )
            continue
        if in_story:
            html_parts.append(
                f'<div class="block"><p class="en">{en_to_html(line)}</p>'
            )
            continue
        html_parts.append(f"<p>{en_to_html(line)}</p>")
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
