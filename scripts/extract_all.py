#!/usr/bin/env python3
"""从 docx 批量提取章节词表、音标，跳过缺失章节 29/32。"""

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX = Path("/mnt/d/E-book/英语学习/宋鹏浩单词课/宋鹏浩1600-Total.docx")
ROOT = Path(__file__).resolve().parent.parent
POS = r"(?:n\.|v\.|adj\.|adv\.)"
SKIP = {
    "the", "she", "his", "they", "when", "after", "time", "perhaps",
    "floating", "algorithms", "observation", "reaching", "individual",
    "wish", "shed", "stop", "continue", "hug", "edge", "margin", "brink",
    "centre", "describe", "prescribe", "demonstrate",
}
SKIP_CHAPTERS = {"29", "32"}
MANUAL = {
    "01": [
        ("proficiency", "n.", "精通，熟练"),
        ("allege", "v.", "（未经证实地）宣称"),
        ("cease", "v.", "停止"),
        ("mercury", "n.", "汞，水银"),
    ],
}


def read_paragraphs(docx: Path) -> list[str]:
    with zipfile.ZipFile(docx) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
    paras = []
    for p in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        texts = [t.text for t in p.iter(tag) if t.text]
        if texts:
            paras.append("".join(texts))
    return paras


def chapter_lines(paras: list[str], num: str) -> list[str]:
    starts = [(p.strip(), i) for i, p in enumerate(paras) if re.match(r"^\d{2}$", p.strip())]
    idx = next(i for n, i in starts if n == num)
    nxt = next((i for n, i in starts if int(n) == int(num) + 1), len(paras))
    return paras[idx + 1 : nxt]


def parse_chapter(lines: list[str], num: str) -> tuple[list[dict], dict]:
    words, seen, phonetics = [], set(), {}
    patterns = [
        rf"^([A-Za-z][A-Za-z\-/]*)\s+/[ˈˌa-zɑɒæʊəɪiːuːɔːeɪaɪɔɪaʊɪəeə\.\-]+/\s*(?:{POS}\s*)?(.+)",
        rf"^([A-Za-z][A-Za-z\-/]*)\s+({POS})\s*(.+)",
        rf"^([A-Za-z][A-Za-z\-/]*)\s+({POS}[^a-zA-Z].*)",
    ]
    for line in lines:
        pm = re.search(
            r"^([A-Za-z][A-Za-z\-/]*)\s+(/[ˈˌa-zɑɒæʊəɪiːuːɔːeɪaɪɔɪaʊɪəeə\.\-]+/)",
            line,
        )
        if pm:
            phonetics[pm.group(1).replace("/", "").lower()] = pm.group(2)
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
            meaning = re.sub(r"[（(].*", "", g[-1]).split(".")[0][:50].strip(" ;")
            words.append({"word": w, "pos": pos, "meaning": meaning})
            break
    for w, pos, meaning in MANUAL.get(num, []):
        if w not in seen:
            words.append({"word": w, "pos": pos, "meaning": meaning})
    return words, phonetics


def ipa_fallback(word: str, docx_ipa: dict) -> str:
    if word in docx_ipa:
        return docx_ipa[word]
    venv_py = ROOT / ".venv" / "lib"
    if venv_py.exists():
        import sys

        for p in venv_py.iterdir():
            sp = p / "site-packages"
            if sp.is_dir() and str(sp) not in sys.path:
                sys.path.insert(0, str(sp))
    try:
        import eng_to_ipa

        raw = eng_to_ipa.convert(word)
        if raw and "*" not in raw:
            return "/" + raw + "/"
    except Exception:
        pass
    return f"/{word}/"


def write_notes(num: str, words: list[dict]) -> None:
    ch = int(num)
    path = ROOT / "notes" / f"ch{num}.md"
    lines = [
        f"# 第 {ch} 章",
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
    path.write_text("\n".join(lines), encoding="utf-8")


def extract_chapter(num: str, paras: list[str]) -> dict | None:
    if num in SKIP_CHAPTERS:
        return None
    lines = chapter_lines(paras, num)
    words, docx_ipa = parse_chapter(lines, num)
    if not words:
        return None
    phonetics = {w["word"]: ipa_fallback(w["word"], docx_ipa) for w in words}
    write_notes(num, words)
    (ROOT / "data" / f"ch{num}.json").write_text(
        json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / "data" / f"ch{num}_phonetics.json").write_text(
        json.dumps(phonetics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"num": num, "count": len(words), "words": words, "phonetics": phonetics}


def main():
    nums = sys.argv[1:] if len(sys.argv) > 1 else [f"{i:02d}" for i in range(1, 32)]
    paras = read_paragraphs(DOCX)
    results = []
    for num in nums:
        r = extract_chapter(num.zfill(2), paras)
        if r:
            results.append(r)
            print(f"ch{num}: {r['count']} words")
        elif num.zfill(2) in SKIP_CHAPTERS:
            print(f"ch{num}: skipped (missing in notes)")
    (ROOT / "data" / "chapters_meta.json").write_text(
        json.dumps(
            [{"num": r["num"], "count": r["count"]} for r in results],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
