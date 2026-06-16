#!/usr/bin/env python3
"""统计 stories/chXX.md 中的核心词（以 story 文件为准，不对照 data/chXX.json）。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from story_meta import story_info  # noqa: E402


def audit(ch: str) -> dict:
    info = story_info(ch)
    if not info:
        return {"total": 0, "words": [], "source": ""}
    return {"total": info["count"], "words": info["words"], "source": info["source"]}


if __name__ == "__main__":
    ch = sys.argv[1] if len(sys.argv) > 1 else "01"
    r = audit(ch)
    ch = ch.zfill(2)
    if r["total"] == 0:
        print(f"Chapter {ch}: 无 story 文件")
        sys.exit(1)
    src = f" ({r['source']})" if r["source"] else ""
    print(f"Chapter {ch}: {r['total']} 词{src}")
    print("Source: story file (authoritative)")
