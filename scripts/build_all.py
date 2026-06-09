#!/usr/bin/env python3
"""批量生成 docs/chXX.html，跳过缺失章节 29/32。"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"29", "32"}


def main():
    chapters = sys.argv[1:] if len(sys.argv) > 1 else [
        f"{i:02d}" for i in range(1, 32) if f"{i:02d}" not in SKIP
    ]
    build = ROOT / "scripts" / "build_pages.py"
    ok, fail = [], []
    for ch in chapters:
        if ch in SKIP:
            continue
        story = ROOT / "stories" / f"ch{ch}.md"
        if not story.exists():
            fail.append(ch)
            continue
        r = subprocess.run([sys.executable, str(build), ch], capture_output=True, text=True)
        if r.returncode == 0:
            ok.append(ch)
        else:
            fail.append(ch)
            print(r.stderr, file=sys.stderr)
    print(f"Built {len(ok)} pages; missing stories: {fail}")


if __name__ == "__main__":
    main()
