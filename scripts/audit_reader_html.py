#!/usr/bin/env python3
"""Verify chapter HTML uses reader shell only — no legacy or duplicated reader markup."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

FORBIDDEN = [
    (r"reader-toolbar", "inline toolbar (belongs in reader.js)"),
    (r"is-pending|is-visible", "legacy sentence classes"),
    (r"data-read-mode|data-mode=", "legacy mode attributes"),
    (r'style\.css\?v=', "versioned base stylesheet"),
    (r"<script(?! src=\"reader\.js)", "inline script blocks"),
]

REQUIRED = [
    (r'class="reader-enabled"', "reader-enabled body"),
    (r'reader\.css\?v=', "reader.css link"),
    (r'reader\.js\?v=', "reader.js script"),
    (r"story-part", "story-part sections"),
]


def audit(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues = []
    for pat, msg in FORBIDDEN:
        if re.search(pat, text):
            issues.append(msg)
    for pat, msg in REQUIRED:
        if not re.search(pat, text):
            issues.append(f"missing {msg}")
    return issues


def main() -> None:
    chapters = sys.argv[1:] if len(sys.argv) > 1 else [
        f"{i:02d}" for i in range(1, 32) if i not in (29, 32)
    ]
    bad = []
    for ch in chapters:
        path = DOCS / f"ch{ch.zfill(2)}.html"
        if not path.exists():
            bad.append((ch, ["file missing"]))
            continue
        issues = audit(path)
        if issues:
            bad.append((ch, issues))
    if bad:
        for ch, issues in bad:
            print(f"ch{ch}: {', '.join(issues)}")
        sys.exit(1)
    print(f"OK: {len(chapters)} chapter pages — reader shell clean")


if __name__ == "__main__":
    main()
