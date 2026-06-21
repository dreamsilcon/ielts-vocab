"""Build story HTML body with reader toolbar, parts, and sentence blocks."""

import re

from reader.config import DEFAULT_PART_TITLE
from reader.markup import en_to_sentences_html, split_sentences, zh_to_sentences_html

TOOLBAR = """
    <div class="reader-toolbar" role="toolbar" aria-label="阅读模式">
      <span class="reader-label">阅读</span>
      <button type="button" class="reader-btn reader-toggle" data-toggle="zh" aria-pressed="false">显示中文</button>
      <button type="button" class="reader-btn reader-toggle" data-toggle="focus" aria-pressed="false">只高亮生词</button>
      <button type="button" class="reader-btn reader-toggle" data-toggle="all" aria-pressed="false">显示全部</button>
      <span class="part-progress-text">0 / 0 Parts 已读完</span>
    </div>"""


def block_html(en: str, zh: str, block_id: str) -> str:
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
        f'<p class="en">{en_to_sentences_html(en)}</p>'
        f"{zh_part}"
        f"{actions}"
        f"</div>"
    )


def close_part(title: str, blocks: list[str], part_idx: int) -> str:
    inner = "\n        ".join(blocks)
    return f"""
      <section class="story-part" data-part="{part_idx}">
        <header class="part-header">
          <button type="button" class="part-toggle" aria-expanded="false">
            <span class="part-title">{title}</span>
            <span class="part-chevron" aria-hidden="true">▸</span>
          </button>
          <button type="button" class="part-mark" title="标记本 Part 读完">完成</button>
        </header>
        <div class="part-content">
        {inner}
        </div>
      </section>"""


class _Parser:
    def __init__(self) -> None:
        self.html_parts: list[str] = ["<h2>Story</h2>", TOOLBAR]
        self.part_idx = -1
        self.block_idx = 0
        self.current_title: str | None = None
        self.current_blocks: list[str] = []

    def ensure_part(self, title: str | None = None) -> None:
        if self.current_title is None:
            self.part_idx += 1
            self.block_idx = 0
            self.current_title = title or DEFAULT_PART_TITLE

    def flush_part(self) -> None:
        if self.current_title is None:
            return
        self.html_parts.append(close_part(self.current_title, self.current_blocks, self.part_idx))
        self.current_blocks = []
        self.current_title = None

    def add_block(self, en: str, zh: str = "") -> None:
        self.ensure_part()
        bid = f"p{self.part_idx}-b{self.block_idx}"
        self.current_blocks.append(block_html(en, zh, bid))
        self.block_idx += 1

    def start_part(self, title: str) -> None:
        if self.current_blocks or self.current_title:
            self.flush_part()
        self.part_idx += 1
        self.block_idx = 0
        self.current_title = title


def md_to_html_body(md: str) -> str:
    p = _Parser()
    in_story = False
    pending_en: str | None = None

    for line in md.splitlines():
        if line.startswith("## Story"):
            in_story = True
            continue
        if line.startswith("## ") and in_story:
            if pending_en:
                p.add_block(pending_en)
                pending_en = None
            p.flush_part()
            break
        if line.strip() == "---":
            continue
        if not in_story or not line.strip():
            continue
        if line.startswith("### "):
            if pending_en:
                p.add_block(pending_en)
                pending_en = None
            p.start_part(line[4:])
            continue
        if line.startswith("zh:"):
            if pending_en:
                p.add_block(pending_en, line)
                pending_en = None
            continue
        pending_en = line

    if pending_en:
        p.add_block(pending_en)
    p.flush_part()

    if re.search(r"^## Coverage", md, re.M):
        p.html_parts.append("<h2>Coverage</h2>")
        for line in md.splitlines():
            if line.startswith("- "):
                p.html_parts.append(f'<p class="coverage">{line[2:]}</p>')
    return "\n      ".join(p.html_parts)
