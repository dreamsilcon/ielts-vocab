#!/usr/bin/env python3
"""从 stories/chXX.md 生成 docs/chXX.html（统一阅读模式）。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from reader.page import build  # noqa: E402

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "01")
