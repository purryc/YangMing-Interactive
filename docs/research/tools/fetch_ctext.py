#!/usr/bin/env python3
"""Fetch Chinese Text Project OCR chapters for Wang Wencheng Gong Quanshu."""

from __future__ import annotations

import argparse
import html
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = "https://ctext.org/wiki.pl?if=gb&remap=gb&res=483031"
CHAPTER = "https://ctext.org/wiki.pl?if=gb&chapter={chapter}&remap=gb"


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Codex Wang Yangming source pack/1.0"},
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as error:
            if error.code not in (403, 429) or attempt == 5:
                raise
            wait_seconds = 10 * (attempt + 1)
            print(f"HTTP {error.code}; waiting {wait_seconds}s", flush=True)
            time.sleep(wait_seconds)
    raise RuntimeError("Unreachable retry path")


def html_to_text(raw_html: str) -> str:
    raw_html = re.sub(r"<script\b.*?</script>", " ", raw_html, flags=re.S | re.I)
    raw_html = re.sub(r"<style\b.*?</style>", " ", raw_html, flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw_html))
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    return text


def chapter_title(root_html: str, chapter: str) -> str:
    pattern = rf'chapter={re.escape(chapter)}[^>]*>([^<]+)<'
    match = re.search(pattern, root_html)
    if not match:
        return f"chapter-{chapter}"
    return html.unescape(match.group(1)).strip()


def chapter_ids(root_html: str) -> list[str]:
    ids = re.findall(r"chapter=(\d+)", root_html)
    return list(dict.fromkeys(ids))


def trim_content(text: str) -> str:
    markers = ["若有错字，请 协助纠正 。", "若有錯字，請 協助糾正 。"]
    for marker in markers:
        if marker in text:
            text = text.split(marker, 1)[1]
            break
    text = re.sub(r"\s*(\d{1,4})\s+", r"\n\1 ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root_html = fetch(ROOT)
    ids = chapter_ids(root_html)
    output = Path(args.output)
    lines = [
        "# 王文成公全书 OCR 全文",
        "",
        f"Source: {ROOT}",
        "Provider: 中国哲学书电子化计划 / Chinese Text Project.",
        "Access note: OCR text generated from the corresponding scanned base text; the site warns that OCR may contain errors. Verify important wording against the scan PDF.",
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")

    for index, chapter in enumerate(ids, 1):
        title = chapter_title(root_html, chapter)
        url = CHAPTER.format(chapter=chapter)
        print(f"[{index}/{len(ids)}] {chapter} {title}", flush=True)
        try:
            text = trim_content(html_to_text(fetch(url)))
        except Exception as error:
            text = f"FETCH FAILED: {error}"
        with output.open("a", encoding="utf-8") as handle:
            handle.write("\n".join([f"## {title}", "", f"Source URL: {url}", "", text, ""]) + "\n")
        time.sleep(2.5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
