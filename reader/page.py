"""Render a full chapter HTML page with reader chrome."""

import re
import sys
from pathlib import Path

from reader.assets_sync import sync_assets
from reader.config import TAG, VERSION
from reader.html_body import md_to_html_body

ROOT = Path(__file__).resolve().parent.parent


def render_page(ch: str, title: str, body: str) -> str:
    v = VERSION
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
  <link rel="stylesheet" href="reader.css?v={v}">
</head>
<body class="reader-enabled" data-ch="{ch}">
  <div class="container">
    <a class="nav-back" href="index.html">← 返回目录</a>
    <header class="story-header">
      <h1>{title}</h1>
      <p class="tag">{TAG}</p>
    </header>
    <article class="story-body">
      {body}
    </article>
  </div>
  <footer><p><a href="index.html">← 返回目录</a></p></footer>
  <script src="reader.js?v={v}"></script>
</body>
</html>
"""


def build_chapter(ch: str) -> Path:
    ch = ch.zfill(2)
    md_path = ROOT / "stories" / f"ch{ch}.md"
    if not md_path.exists():
        print(f"缺少 {md_path}")
        sys.exit(1)
    md = md_path.read_text(encoding="utf-8")
    title_m = re.search(r"^# (.+)$", md, re.M)
    title = title_m.group(1) if title_m else f"Chapter {int(ch)}"
    body = md_to_html_body(md)
    html = render_page(ch, title, body)
    out = ROOT / "docs" / f"ch{ch}.html"
    out.write_text(html, encoding="utf-8")
    return out


def build(ch: str) -> None:
    sync_assets()
    out = build_chapter(ch)
    print(f"生成 {out}")
