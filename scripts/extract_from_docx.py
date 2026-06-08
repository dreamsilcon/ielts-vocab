#!/usr/bin/env python3
"""从宋鹏浩1600-Total.docx 提取章节词汇，生成 notes/ 和 stories/ 骨架。"""

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX_DEFAULT = Path("/mnt/d/E-book/英语学习/宋鹏浩单词课/宋鹏浩1600-Total.docx")
ROOT = Path(__file__).resolve().parent.parent
POS = r"(?:n\.|v\.|adj\.|adv\.)"
SKIP = {
    "the", "she", "his", "they", "when", "after", "time", "perhaps",
    "floating", "algorithms", "observation", "reaching", "individual",
    "wish", "shed", "stop", "continue", "hug", "edge", "margin", "brink",
    "centre", "describe", "prescribe", "demonstrate",
}

# 解析器易漏掉的重要词，手动补全
MANUAL = {
    "01": [
        ("proficiency", "n.", "精通，熟练"),
        ("allege", "v.", "（未经证实地）宣称，断言"),
        ("cease", "v.", "停止，结束"),
        ("mercury", "n.", "汞，水银；水银柱"),
    ],
}


def read_paragraphs(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    paras = []
    tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
    for p in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        texts = [t.text for t in p.iter(tag) if t.text]
        if texts:
            paras.append("".join(texts))
    return paras


def chapter_bounds(paras: list[str]) -> list[tuple[str, int]]:
    return [(p.strip(), i) for i, p in enumerate(paras) if re.match(r"^\d{2}$", p.strip())]


def extract_chapter(paras: list[str], num: str) -> list[str]:
    starts = chapter_bounds(paras)
    idx = next(i for n, i in starts if n == num)
    next_idx = next((i for n, i in starts if int(n) == int(num) + 1), len(paras))
    return paras[idx + 1 : next_idx]


def parse_headwords(lines: list[str]) -> list[dict]:
    words, seen = [], set()
    patterns = [
        rf"^([A-Za-z][A-Za-z\-/]*)\s+/[ˈˌa-zɑɒæʊəɪiːuːɔːeɪaɪɔɪaʊɪəeə\.\-]+/\s*(?:{POS}\s*)?(.+)",
        rf"^([A-Za-z][A-Za-z\-/]*)\s+({POS})\s*(.+)",
        rf"^([A-Za-z][A-Za-z\-/]*)\s+({POS}[^a-zA-Z].*)",
    ]
    for line in lines:
        line = line.strip()
        for pat in patterns:
            m = re.match(pat, line)
            if not m:
                continue
            w = m.group(1).replace("/", "").lower()
            if w in seen or len(w) < 3 or w in SKIP:
                break
            seen.add(w)
            g = m.groups()
            pos = g[1] if len(g) > 2 and re.match(POS, g[1]) else ""
            meaning = re.sub(r"[（(].*", "", g[-1]).split(".")[0][:40].strip(" ;")
            words.append({"word": w, "pos": pos, "meaning": meaning})
            break
    return words


def write_notes(ch: str, words: list[dict]) -> Path:
    out = ROOT / "notes" / f"ch{ch}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# 第 {int(ch)} 章",
        "",
        "> 来源：宋鹏浩1600-Total.docx",
        "",
        "## 单词列表",
        "",
        "| 单词 | 词性 | 释义 |",
        "|------|------|------|",
    ]
    for w in words:
        lines.append(f"| {w['word']} | {w['pos']} | {w['meaning']} |")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main():
    docx = Path(sys.argv[1]) if len(sys.argv) > 1 else DOCX_DEFAULT
    ch = sys.argv[2] if len(sys.argv) > 2 else "01"
    if not docx.exists():
        print(f"找不到文件: {docx}", file=sys.stderr)
        sys.exit(1)
    paras = read_paragraphs(docx)
    lines = extract_chapter(paras, ch.zfill(2))
    words = parse_headwords(lines)
    for w, pos, meaning in MANUAL.get(ch.zfill(2), []):
        if w not in {x["word"] for x in words}:
            words.append({"word": w, "pos": pos, "meaning": meaning})
    words.sort(key=lambda x: lines.index(next(l for l in lines if x["word"] in l.lower())) if any(x["word"] in l.lower() for l in lines) else 999)
    # 保持 docx 出现顺序
    order = []
    for line in lines:
        for w in words:
            if w["word"] in line.lower() and w["word"] not in order:
                order.append(w["word"])
    words = [next(x for x in words if x["word"] == w) for w in order] + [x for x in words if x["word"] not in order]
    path = write_notes(ch.zfill(2), words)
    meta = ROOT / "data" / f"ch{ch.zfill(2)}.json"
    meta.parent.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"第 {ch} 章：{len(words)} 个词 → {path}")


if __name__ == "__main__":
    main()
