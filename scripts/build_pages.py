#!/usr/bin/env python3
"""从 stories/chXX.md 生成 docs/chXX.html。"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READER_CHAPTERS = set(range(1, 10))  # ch01–ch09

KW_RE = re.compile(r"<b>([^<]+)</b>\s*(/[^/\s][^/]*/)")
ZH_KW_RE = re.compile(r"<b>([^<]+)</b>\(([^)]+)\)")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
ZH_SENT_SPLIT = re.compile(r"(?<=[。！？])\s+")


def en_to_html(text: str) -> str:
    return KW_RE.sub(
        r'<span class="w">'
        r'<strong class="kw">\1</strong>'
        r'<span class="ipa">\2</span>'
        r"</span>",
        text,
    )


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    parts = SENT_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]


def split_zh_sentences(text: str) -> list[str]:
    text = text.removeprefix("zh:").strip()
    if not text:
        return []
    parts = ZH_SENT_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]


def zh_markup(text: str) -> str:
    return ZH_KW_RE.sub(
        r'<span class="w-cn">'
        r"<strong>\1</strong>"
        r'<span class="en-ref">(\2)</span>'
        r"</span>",
        text,
    )


def zh_to_html(text: str) -> str:
    text = text.removeprefix("zh:").strip()
    return zh_markup(text)


def zh_to_sentences_html(zh_line: str) -> str:
    sentences = split_zh_sentences(zh_line)
    if not sentences:
        return ""
    if len(sentences) == 1:
        return f'<span class="sent-zh" data-zh-idx="0" hidden>{zh_markup(sentences[0])}</span>'
    spans = []
    for i, sent in enumerate(sentences):
        spans.append(f'<span class="sent-zh" data-zh-idx="{i}" hidden>{zh_markup(sent)}</span>')
    return " ".join(spans)


def en_to_sentences_html(text: str) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        html = en_to_html(text)
        return f'<span class="sent" data-idx="0">{html}</span>'
    spans = []
    for i, sent in enumerate(sentences):
        hidden = "" if i == 0 else " hidden"
        spans.append(f'<span class="sent" data-idx="{i}"{hidden}>{en_to_html(sent)}</span>')
    return " ".join(spans)


def block_html(en: str, zh: str, block_id: str, reader: bool) -> str:
    en_content = en_to_sentences_html(en) if reader else en_to_html(en)
    if reader:
        total = max(len(split_sentences(en)), 1)
        actions = (
            f'<div class="block-actions">'
            f'<button type="button" class="btn-next">下一句 →</button>'
            f'<span class="sent-progress">1 / {total} 句</span>'
            f"</div>"
        )
        zh_part = ""
        if zh:
            zh_content = zh_to_sentences_html(zh)
            zh_part = f'<p class="zh" hidden>{zh_content}</p>'
        return (
            f'<div class="block" data-block-id="{block_id}">'
            f'<p class="en">{en_content}</p>'
            f"{zh_part}"
            f"{actions}"
            f"</div>"
        )
    return (
        f'<div class="block">'
        f'<p class="en">{en_content}</p>'
        f'<p class="zh">{zh_to_html(zh)}</p>'
        f"</div>"
    )


def reader_toolbar() -> str:
    return """
    <div class="reader-toolbar" role="toolbar" aria-label="阅读模式">
      <span class="reader-label">阅读</span>
      <button type="button" class="reader-btn reader-toggle" data-toggle="zh" aria-pressed="false">显示中文</button>
      <button type="button" class="reader-btn reader-toggle" data-toggle="focus" aria-pressed="false">只高亮生词</button>
      <button type="button" class="reader-btn reader-toggle" data-toggle="all" aria-pressed="false">显示全部</button>
      <span class="part-progress-text">0 / 0 Parts 已读完</span>
    </div>"""


def close_part(part_title: str, blocks: list[str], part_idx: int) -> str:
    inner = "\n        ".join(blocks)
    return f"""
      <section class="story-part" data-part="{part_idx}">
        <header class="part-header">
          <button type="button" class="part-toggle" aria-expanded="false">
            <span class="part-title">{part_title}</span>
            <span class="part-chevron" aria-hidden="true">▸</span>
          </button>
          <button type="button" class="part-mark" title="标记本 Part 读完">完成</button>
        </header>
        <div class="part-content">
        {inner}
        </div>
      </section>"""


def md_to_html_body_reader(md: str) -> str:
    html_parts = ["<h2>Story</h2>", reader_toolbar()]
    in_story = False
    pending_en: str | None = None
    part_idx = -1
    block_idx = 0
    current_blocks: list[str] = []
    current_title: str | None = None

    def flush_part():
        nonlocal current_title, current_blocks, part_idx
        if current_title is None:
            return
        html_parts.append(close_part(current_title, current_blocks, part_idx))
        current_blocks = []

    for line in md.splitlines():
        if line.startswith("## Story"):
            in_story = True
            continue
        if line.startswith("## ") and in_story:
            if pending_en and current_title is not None:
                bid = f"p{part_idx}-b{block_idx}"
                current_blocks.append(block_html(pending_en, "", bid, True))
                pending_en = None
            flush_part()
            break
        if line.strip() == "---":
            continue
        if not in_story or not line.strip():
            continue
        if line.startswith("### "):
            if pending_en:
                bid = f"p{part_idx}-b{block_idx}"
                current_blocks.append(block_html(pending_en, "", bid, True))
                block_idx += 1
                pending_en = None
            flush_part()
            part_idx += 1
            block_idx = 0
            current_title = line[4:]
            continue
        if line.startswith("zh:"):
            if pending_en:
                bid = f"p{part_idx}-b{block_idx}"
                current_blocks.append(block_html(pending_en, line, bid, True))
                block_idx += 1
                pending_en = None
            continue
        pending_en = line

    if pending_en and current_title is not None:
        bid = f"p{part_idx}-b{block_idx}"
        current_blocks.append(block_html(pending_en, "", bid, True))
    flush_part()

    if re.search(r"^## Coverage", md, re.M):
        html_parts.append("<h2>Coverage</h2>")
        for line in md.splitlines():
            if line.startswith("- "):
                html_parts.append(f'<p class="coverage">{line[2:]}</p>')
    return "\n      ".join(html_parts)


def md_to_html_body(md: str) -> str:
    html_parts = ["<h2>Story</h2>"]
    in_story = False
    pending_en: str | None = None

    for line in md.splitlines():
        if line.startswith("## Story"):
            in_story = True
            continue
        if line.startswith("## ") and in_story:
            if pending_en:
                html_parts.append(block_html(pending_en, "", "", False))
                pending_en = None
            break
        if line.strip() == "---":
            continue
        if not in_story or not line.strip():
            continue
        if line.startswith("### "):
            html_parts.append(f"<h3>{line[4:]}</h3>")
            continue
        if line.startswith("zh:"):
            if pending_en:
                html_parts.append(block_html(pending_en, line, "", False))
                pending_en = None
            continue
        pending_en = line

    if re.search(r"^## Coverage", md, re.M):
        html_parts.append("<h2>Coverage</h2>")
        for line in md.splitlines():
            if line.startswith("- "):
                html_parts.append(f'<p class="coverage">{line[2:]}</p>')
    return "\n      ".join(html_parts)


def build(ch: str):
    ch = ch.zfill(2)
    ch_num = int(ch)
    reader = ch_num in READER_CHAPTERS
    md_path = ROOT / "stories" / f"ch{ch}.md"
    if not md_path.exists():
        print(f"缺少 {md_path}")
        sys.exit(1)
    md = md_path.read_text(encoding="utf-8")
    title_m = re.search(r"^# (.+)$", md, re.M)
    title = title_m.group(1) if title_m else f"Chapter {ch_num}"
    body = md_to_html_body_reader(md) if reader else md_to_html_body(md)

    body_class = ' class="reader-enabled"' if reader else ""
    body_data = f' data-ch="{ch}"' if reader else ""
    asset_v = "?v=4" if reader else ""
    reader_script = f'\n  <script src="reader.js{asset_v}"></script>' if reader else ""
    tag = "阅读模式 · 逐句展开 · Part 进度" if reader else "英文故事 + 中文对照 · 关键词高亮"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css{asset_v}">
</head>
<body{body_class}{body_data}>
  <div class="container">
    <a class="nav-back" href="index.html">← 返回目录</a>
    <header class="story-header">
      <h1>{title}</h1>
      <p class="tag">{tag}</p>
    </header>
    <article class="story-body">
      {body}
    </article>
  </div>
  <footer><p><a href="index.html">← 返回目录</a></p></footer>{reader_script}
</body>
</html>
"""
    out = ROOT / "docs" / f"ch{ch}.html"
    out.write_text(html, encoding="utf-8")
    suffix = " (阅读模式)" if reader else ""
    print(f"生成 {out}{suffix}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "01")
