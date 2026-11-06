#!/usr/bin/env python3
"""Fetch selected Wikisource pages as plain Markdown-ish text."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API = "https://zh.wikisource.org/w/api.php"


def api_get(params: dict[str, str]) -> dict:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{API}?{query}",
        headers={"User-Agent": "Codex Wang Yangming source pack/1.0"},
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 5:
                raise
            wait_seconds = 5 * (attempt + 1)
            sys.stderr.write(f"Rate limited; waiting {wait_seconds}s\n")
            time.sleep(wait_seconds)
    raise RuntimeError("Unreachable retry path")


def get_extract(title: str) -> str:
    data = api_get(
        {
            "action": "query",
            "prop": "extracts",
            "explaintext": "1",
            "format": "json",
            "redirects": "1",
            "titles": title,
        }
    )
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        raise RuntimeError(f"Missing Wikisource page: {title}")
    return page.get("extract", "").strip()


def get_links(title: str) -> list[str]:
    data = api_get(
        {
            "action": "parse",
            "page": title,
            "prop": "links",
            "format": "json",
        }
    )
    links = []
    for link in data.get("parse", {}).get("links", []):
        if link.get("ns") == 0:
            links.append(link.get("*", ""))
    return links


def write_collection(output: Path, title: str, pages: list[str], source_url: str) -> None:
    lines = [
        f"# {title}",
        "",
        f"Source: {source_url}",
        "Access: Wikisource public-domain text.",
        "",
    ]
    for page in pages:
        sys.stderr.write(f"Fetching {page}\n")
        text = get_extract(page)
        lines.extend([f"## {page}", "", text, ""])
        time.sleep(1.5)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    chuanxilu_pages = ["傳習錄/卷上", "傳習錄/卷中", "傳習錄/卷下"]
    write_collection(
        outdir / "01-primary-chuanxilu-wikisource.md",
        "傳習錄 / 传习录",
        chuanxilu_pages,
        "https://zh.wikisource.org/wiki/傳習錄",
    )

    complete_root = "王文成公全書 (四部叢刊本)"
    complete_links = [
        link
        for link in get_links(complete_root)
        if link.startswith("王文成公全書 (四部叢刊本)/")
    ]
    order = {
        "序": 0,
        "目録": 1,
        "語錄卷第一": 2,
        "語錄卷第二": 3,
        "語錄卷第三": 4,
        "補": 99,
        "附錄一卷": 100,
    }

    def chinese_number(value: str) -> int:
        digits = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
        }
        if value == "十":
            return 10
        if value.startswith("十"):
            return 10 + digits.get(value[1:], 0)
        if "十" in value:
            left, right = value.split("十", 1)
            return digits.get(left, 0) * 10 + digits.get(right, 0)
        return digits.get(value, 0)

    def sort_key(link: str) -> tuple[int, str]:
        leaf = link.rsplit("/", 1)[-1]
        if leaf in order:
            return (order[leaf], leaf)
        if leaf.startswith("卷第"):
            number = leaf.removeprefix("卷第").replace("下", "").replace("上", "")
            suffix = "b" if leaf.endswith("下") else "a"
            return (20 + chinese_number(number), suffix)
        return (200, leaf)

    complete_pages = sorted(set(complete_links), key=sort_key)
    write_collection(
        outdir / "01-primary-wang-wencheng-complete-wikisource.md",
        "王文成公全書（四部叢刊本）",
        complete_pages,
        "https://zh.wikisource.org/wiki/王文成公全書_(四部叢刊本)",
    )

    bio_pages = [
        "明史/卷195",
        "明儒學案/姚江學案",
    ]
    write_collection(
        outdir / "02-biography-mingshi-mingruxuean-wikisource.md",
        "王陽明生平與姚江學案：明史、明儒學案",
        bio_pages,
        "https://zh.wikisource.org/wiki/明史/卷195 ; https://zh.wikisource.org/wiki/明儒學案/姚江學案",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
