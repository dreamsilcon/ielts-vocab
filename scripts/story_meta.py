#!/usr/bin/env python3
"""从 stories/chXX.md 读取标题与词数（以 story 文件为准）。"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TITLE_RE = re.compile(r"^# Chapter \d+ · (.+)$", re.M)
KW_RE = re.compile(r"<b>([^<]+)</b>\s*/[^/\s]")


def story_words(md: str) -> list[str]:
    """英文 Story 区段内带音标的核心词（去重、小写、按出现顺序）。"""
    seen: set[str] = set()
    ordered: list[str] = []
    in_story = False
    for line in md.splitlines():
        if line.startswith("## Story"):
            in_story = True
            continue
        if line.startswith("## ") and in_story:
            break
        if not in_story or line.startswith(("zh:", "###")):
            continue
        for w in KW_RE.findall(line):
            key = w.lower()
            if key not in seen:
                seen.add(key)
                ordered.append(w)
    return ordered


def story_info(ch: str) -> dict | None:
    ch = ch.zfill(2)
    path = ROOT / "stories" / f"ch{ch}.md"
    if not path.exists():
        return None
    md = path.read_text(encoding="utf-8")
    title_m = TITLE_RE.search(md)
    raw_title = title_m.group(1).strip() if title_m else f"第 {int(ch)} 章"
    # 旧批量故事默认标题，目录仍显示「第 N 章」
    title = f"第 {int(ch)} 章" if raw_title == "Memory Story" else raw_title
    words = story_words(md)
    source = ""
    for line in md.splitlines():
        if line.startswith("- Source:"):
            source = line.split("`")[1] if "`" in line else line.removeprefix("- Source:").strip()
            break
    return {"title": title, "count": len(words), "words": words, "source": source}
