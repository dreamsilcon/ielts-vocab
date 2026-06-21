"""English / Chinese markup and sentence splitting."""

import re

KW_RE = re.compile(r"<b>([^<]+)</b>\s*(/[^/\s][^/]*/)")
ZH_KW_RE = re.compile(r"<b>([^<]+)</b>\(([^)]+)\)")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
ZH_SENT_SPLIT = re.compile(r"(?<=[。！？])\s+")


def en_to_html(text: str) -> str:
    return KW_RE.sub(
        r'<span class="w">'
        r'<strong class="kw">\1</strong>'
        r'<span class="ipa">\2</span>'
        r"</span>",
        text,
    )


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [p.strip() for p in SENT_SPLIT.split(text) if p.strip()]


def split_zh_sentences(text: str) -> list[str]:
    text = text.removeprefix("zh:").strip()
    if not text:
        return []
    return [p.strip() for p in ZH_SENT_SPLIT.split(text) if p.strip()]


def zh_markup(text: str) -> str:
    return ZH_KW_RE.sub(
        r'<span class="w-cn">'
        r"<strong>\1</strong>"
        r'<span class="en-ref">(\2)</span>'
        r"</span>",
        text,
    )


def en_to_sentences_html(text: str) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return f'<span class="sent" data-idx="0">{en_to_html(text.strip())}</span>'
    spans = []
    for i, sent in enumerate(sentences):
        hidden = "" if i == 0 else " hidden"
        spans.append(f'<span class="sent" data-idx="{i}"{hidden}>{en_to_html(sent)}</span>')
    return " ".join(spans)


def zh_to_sentences_html(zh_line: str) -> str:
    sentences = split_zh_sentences(zh_line)
    if not sentences:
        return ""
    if len(sentences) == 1:
        return f'<span class="sent-zh" data-zh-idx="0" hidden>{zh_markup(sentences[0])}</span>'
    return " ".join(
        f'<span class="sent-zh" data-zh-idx="{i}" hidden>{zh_markup(s)}</span>'
        for i, s in enumerate(sentences)
    )
