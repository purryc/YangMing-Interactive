#!/usr/bin/env python3
"""Upload local source files into an existing NotebookLM notebook."""

from __future__ import annotations

import argparse
import re
import sys
import time
from typing import Optional
from pathlib import Path


NOTEBOOKLM_SKILL = Path("/Users/hmi/.agents/skills/notebooklm")
sys.path.insert(0, str(NOTEBOOKLM_SKILL / "scripts"))

from patchright.sync_api import sync_playwright  # noqa: E402
from browser_utils import BrowserFactory  # noqa: E402


def visible_text(page) -> str:
    try:
        return page.locator("body").inner_text(timeout=5000)
    except Exception:
        return ""


def find_button(page, selectors: list[str]) -> Optional[object]:
    for selector in selectors:
        loc = page.locator(selector)
        try:
            count = loc.count()
        except Exception:
            count = 0

        if count == 0:
            continue

        for idx in range(count):
            candidate = loc.nth(idx)
            try:
                if candidate.is_visible(timeout=1000):
                    return candidate
            except Exception:
                continue
    return None


def click_upload_button(page) -> bool:
    upload_button = find_button(page, [
        'button:has-text("Upload files")',
        'button:has-text("Add sources")',
        'button:has-text("Add source")',
    ])
    if upload_button is None:
        return False

    upload_button.click()
    return True


def click_upload_files(page) -> bool:
    upload_button = find_button(page, [
        'button:has-text("Upload files")',
        'button:has-text("Upload")',
    ])
    if upload_button is None:
        return False

    upload_button.click()
    return True


def ensure_sources_tab(page) -> None:
    try:
        sources_tab = page.locator('[role="tab"]').filter(has_text="Sources").first
        if sources_tab.count() == 0:
            return
        if sources_tab.get_attribute("aria-selected") != "true":
            sources_tab.click()
            page.wait_for_timeout(1000)
    except Exception:
        return


def upload_with_file_input(page, paths: list[str]) -> bool:
    file_inputs = page.locator("input[type='file']")
    try:
        input_count = file_inputs.count()
    except Exception:
        input_count = 0

    for idx in range(input_count):
        try:
            file_inputs.nth(idx).set_input_files(paths)
            return True
        except Exception:
            continue
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook-url", required=True)
    parser.add_argument("--upload-dir", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--show-browser", action="store_true")
    args = parser.parse_args()

    upload_dir = Path(args.upload_dir).resolve()
    paths = sorted(str(path) for path in upload_dir.iterdir() if path.is_file())
    if not paths:
        raise SystemExit(f"No files found in {upload_dir}")

    print(f"Notebook: {args.notebook_url}", flush=True)
    print(f"Upload files: {len(paths)}", flush=True)
    for path in paths:
        print(f" - {path}", flush=True)

    pw = sync_playwright().start()
    context = None
    try:
        context = BrowserFactory.launch_persistent_context(
            pw,
            headless=not args.show_browser,
        )
        page = context.new_page()
        page.set_default_timeout(60000)
        page.goto(args.notebook_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_url(re.compile(r"^https://notebooklm\.google\.com/notebook/"), timeout=30000)
        page.wait_for_timeout(5000)

        title_input = page.locator("input").first
        title_input.fill(args.title)
        title_input.press("Enter")
        print(f"Renamed notebook to: {args.title}", flush=True)
        page.wait_for_timeout(1500)

        # Sources tab is where Add sources exists.
        ensure_sources_tab(page)

        # First open Sources tab, then drive the upload flow:
        # 1) click "Add sources" if needed
        # 2) in that panel, click "Upload files"
        upload_opened = False
        try:
            if not click_upload_button(page):
                raise RuntimeError("Upload button not found")

            # If "Upload files" button is visible now, use native chooser.
            try:
                with page.expect_file_chooser(timeout=12000) as chooser_info:
                    click_upload_files(page)
                chooser = chooser_info.value
                chooser.set_files(paths)
                upload_opened = True
            except Exception:
                # Click once more to open panel and then retry upload files.
                if click_upload_button(page):
                    with page.expect_file_chooser(timeout=12000) as chooser_info:
                        click_upload_files(page)
                    chooser = chooser_info.value
                    chooser.set_files(paths)
                    upload_opened = True
                else:
                    raise
        except Exception as exc:
            # In many cases NotebookLM exposes a native file input in DOM.
            if not upload_with_file_input(page, paths):
                raise RuntimeError(f"Upload control not available: {exc}")
            print("Files submitted via file input.", flush=True)

        if upload_opened:
            print("Files submitted to NotebookLM.", flush=True)

        deadline = time.time() + 900
        last_report = ""
        expected_names = [Path(path).name for path in paths]
        while time.time() < deadline:
            text = visible_text(page)
            found = sum(1 for name in expected_names if name in text)
            status_bits = []
            for token in ["Uploading", "Processing", "Converting", "Importing", "Creating", "Error", "Failed"]:
                if token.lower() in text.lower():
                    status_bits.append(token)
            report = f"visible_files={found}/{len(paths)} status={','.join(status_bits) or 'none'} url={page.url}"
            if report != last_report:
                print(report, flush=True)
                last_report = report

            if found >= len(paths) and not any(bit in status_bits for bit in ["Uploading", "Converting", "Importing", "Creating"]):
                break
            page.wait_for_timeout(5000)

        print("Final URL:", page.url, flush=True)
        print("Final visible file count:", sum(1 for name in expected_names if name in visible_text(page)), flush=True)
        page.screenshot(path=str(upload_dir.parent / "notes" / "notebooklm-upload-final.png"), full_page=True)
        context.storage_state(path=str(NOTEBOOKLM_SKILL / "data/browser_state/state.json"))
        return 0
    finally:
        if context:
            context.close()
        pw.stop()


if __name__ == "__main__":
    raise SystemExit(main())
