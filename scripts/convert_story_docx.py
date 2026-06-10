#!/usr/bin/env python3
"""将「分章节整理/ch* story.docx」转为 stories/chXX.md 格式。"""

import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY_DIR = Path("/mnt/d/E-book/英语学习/宋鹏浩单词课/分章节整理")

TAG_P = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
TAG_T = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


def read_docx_paragraphs(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paras = []
    for p in root.iter(TAG_P):
        texts = [t.text for t in p.iter(TAG_T) if t.text]
        if texts:
            paras.append("".join(texts))
    return paras


def is_chinese_line(s: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", s))


def is_skipped(s: str) -> bool:
    if re.match(r"^Part \d+ Vocabulary Audit\s*$", s):
        return True
    if s.startswith("✅"):
        return True
    return False


def is_part_header(s: str) -> bool:
    if re.match(r"^Part \d+", s):
        return True
    return bool(re.match(r"^Epilogue\b", s))


def en_markup(text: str) -> str:
    """word (/ipa/) → <b>word</b> /ipa/"""
    return re.sub(
        r"\b([A-Za-z][A-Za-z\-]*)\s*\((/[^)]+/)\)",
        r"<b>\1</b> \2",
        text,
    )


def zh_markup(text: str) -> str:
    """中文（word，...，/ipa/） → <b>中文</b>(word)"""

    def repl(m):
        return f"<b>{m.group(1)}</b>({m.group(2)})"

    return re.sub(
        r"([\u4e00-\u9fff]+(?:[/／][\u4e00-\u9fff]+)?)\s*[（(]\s*([A-Za-z]+)[^）)]*[）)]",
        repl,
        text,
    )


def pair_paragraphs(paras: list[str]) -> list[tuple[str, str]]:
    """英文段 + 中文段 配对；Part 标题单独保留在英文侧。"""
    pairs: list[tuple[str, str]] = []
    i = 0
    while i < len(paras):
        p = paras[i].strip()
        if not p or is_skipped(p):
            i += 1
            continue
        if is_part_header(p):
            # Part 标题作为独立块（仅英文行，中文空）
            pairs.append((f"**{p}**", ""))
            i += 1
            continue
        if is_chinese_line(p):
            i += 1
            continue
        en_parts = [p]
        i += 1
        while i < len(paras) and paras[i].strip() and not is_chinese_line(paras[i]) and not is_part_header(paras[i]):
            en_parts.append(paras[i].strip())
            i += 1
        zh_parts = []
        while i < len(paras) and paras[i].strip() and is_chinese_line(paras[i]):
            zh_parts.append(paras[i].strip())
            i += 1
        en = " ".join(en_parts)
        zh = " ".join(zh_parts)
        pairs.append((en, zh))
    return pairs


def convert(ch: int, docx_path: Path | None = None) -> Path:
    chs = f"{ch:02d}"
    if docx_path is None:
        candidates = [
            STORY_DIR / f"ch{ch} story.docx",
            STORY_DIR / f"ch{chs} story.docx",
            STORY_DIR / f"ch{ch} story.doc",
            STORY_DIR / f"ch{chs} story.doc",
        ]
        docx_path = next((p for p in candidates if p.exists()), None)
    if not docx_path or not docx_path.exists():
        raise FileNotFoundError(f"找不到 story docx: ch{ch}")

    paras = [p.strip() for p in read_docx_paragraphs(docx_path) if p.strip() and not is_skipped(p.strip())]
    pairs = pair_paragraphs(paras)

    lines = [
        f"# Chapter {chs} · Memory Story",
        "",
        "> From GPT story (分章节整理 docx)",
        "",
        "---",
        "",
        "## Story",
        "",
    ]
    for en, zh in pairs:
        if en.startswith("**Part") or en.startswith("**Epilogue"):
            part = en.strip("*")
            lines.append(f"### {part}")
            lines.append("")
            continue
        lines.append(en_markup(en))
        lines.append("")
        if zh:
            lines.append(f"zh: {zh_markup(zh)}")
            lines.append("")

    lines.extend(["---", "", "## Coverage", "", f"- Source: `{docx_path.name}`", ""])
    out = ROOT / "stories" / f"ch{chs}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


if __name__ == "__main__":
    ch = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    path = convert(ch)
    print(f"生成 {path}")
