#!/usr/bin/env python3
"""从 stories/chXX.md 生成 docs/chXX.html（简单版）。"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def md_to_html_body(md: str) -> str:
    """将故事 markdown 中的 **word**（释义）转为 span.word。"""
    html_parts = []
    in_table = False
    for line in md.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(">"):
            continue
        if line.startswith("---"):
            continue
        if line.startswith("## "):
            html_parts.append(f"<h2>{line[3:]}</h2>")
            continue
        if line.startswith("|") and "---" not in line:
            if not in_table:
                html_parts.append('<div class="groups"><table>')
                in_table = True
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] == "主题":
                html_parts.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr></thead><tbody>")
            else:
                html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            continue
        if in_table and not line.startswith("|"):
            html_parts.append("</tbody></table></div>")
            in_table = False
        if line.startswith("- "):
            html_parts.append(f'<p class="coverage">{line[2:]}</p>')
            continue
        if not line.strip():
            continue
        # **word**（meaning） -> spans
        def repl(m):
            w, meaning = m.group(1), m.group(2)
            return f'<span class="word">{w}</span><span class="meaning">（{meaning}）</span>'
        line = re.sub(r"\*\*([^*]+)\*\*（([^）]+)）", repl, line)
        line = re.sub(r"\*\*([^*]+)\*\*", r'<span class="word">\1</span>', line)
        html_parts.append(f"<p>{line}</p>")
    if in_table:
        html_parts.append("</tbody></table></div>")
    return "\n      ".join(html_parts)


def build(ch: str):
    ch = ch.zfill(2)
    md_path = ROOT / "stories" / f"ch{ch}.md"
    if not md_path.exists():
        print(f"缺少 {md_path}")
        sys.exit(1)
    md = md_path.read_text(encoding="utf-8")
    title_m = re.search(r"^# (.+)$", md, re.M)
    title = title_m.group(1) if title_m else f"第 {int(ch)} 章"
    body = md_to_html_body(md)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <a class="nav-back" href="index.html">← 返回目录</a>
    <header class="story-header">
      <h1>{title}</h1>
    </header>
    <article class="story-body">
      {body}
    </article>
  </div>
  <footer><p><a href="index.html">← 返回目录</a></p></footer>
</body>
</html>
"""
    out = ROOT / "docs" / f"ch{ch}.html"
    out.write_text(html, encoding="utf-8")
    print(f"生成 {out}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "01")
