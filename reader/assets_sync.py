"""Copy reader static assets from reader/assets/ to docs/."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"
DOCS = ROOT / "docs"


def sync_assets() -> None:
    DOCS.mkdir(exist_ok=True)
    for name in ("reader.js", "reader.css"):
        src = ASSETS / name
        dst = DOCS / name
        shutil.copy2(src, dst)
