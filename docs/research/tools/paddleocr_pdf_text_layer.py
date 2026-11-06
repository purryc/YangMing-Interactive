#!/usr/bin/env python3
"""Create a searchable PDF from a scanned PDF using PaddleOCR text overlays."""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

import fitz
import numpy as np
from paddleocr import PaddleOCR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input scanned PDF path")
    parser.add_argument("--output", required=True, help="Output searchable PDF path")
    parser.add_argument("--dpi", type=int, default=150, help="Render DPI for OCR input")
    parser.add_argument("--start-page", type=int, default=1, help="1-based start page")
    parser.add_argument("--end-page", type=int, default=0, help="1-based end page, 0 means last")
    parser.add_argument("--conf", type=float, default=0.70, help="Minimum OCR confidence")
    parser.add_argument("--ocr-version", default="PP-OCRv6", help="PaddleOCR version profile")
    parser.add_argument("--batch-size", type=int, default=8, help="Number of pages to OCR per batch")
    parser.add_argument("--resume", action="store_true", help="Append to existing output PDF if it exists")
    parser.add_argument("--checkpoint-interval", type=int, default=100, help="Save intermediate output every N processed pages")
    return parser.parse_args()


def save_output(out_doc: fitz.Document, output_path: Path, is_resume: bool, is_checkpoint: bool) -> None:
    """Save safely while avoiding PyMuPDF incremental write restrictions."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    target = output_path
    if is_resume:
        if is_checkpoint:
            target = output_path.with_name(output_path.name + ".checkpoint.pdf")
        else:
            target = output_path.with_name(output_path.name + ".final.pdf")

    out_doc.save(str(target), garbage=4, deflate=True)

    if is_resume and target != output_path:
        shutil.move(str(target), str(output_path))


def page_to_rgb_array(page: fitz.Page, scale: float) -> tuple[fitz.Pixmap, np.ndarray]:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    return pix, image


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    doc = fitz.open(str(input_path))
    total_pages = doc.page_count

    start = max(1, args.start_page)
    end = total_pages if args.end_page == 0 else min(total_pages, args.end_page)
    if start > end:
        raise ValueError("start-page must be <= end-page")

    scale = args.dpi / 72.0
    ocr = PaddleOCR(
        lang="ch",
        ocr_version=args.ocr_version,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    should_resume = args.resume and output_path.exists()
    out_doc = fitz.open(str(output_path)) if should_resume else fitz.open()
    if args.resume and output_path.exists():
        print(f"Resuming into existing file: {output_path} with {out_doc.page_count} pages")
        if start <= 1:
            start = out_doc.page_count + 1
        if out_doc.page_count and out_doc.page_count >= end:
            print("Output already covers requested page range; nothing to do.")
            return 0
    processed = 0
    total_inserted = 0
    total_secs = 0.0

    batch_start = start
    while batch_start <= end:
        batch_end = min(end, batch_start + args.batch_size - 1)
        images: list[tuple[int, fitz.Pixmap, np.ndarray, fitz.Rect]] = []
        for page_num in range(batch_start, batch_end + 1):
            page = doc[page_num - 1]
            pix, image = page_to_rgb_array(page, scale)
            images.append((page_num, pix, image, page.rect))

        ts = time.time()
        try:
            ocr_results = ocr.predict([entry[2] for entry in images])
        except Exception as exc:
            print(f"[{batch_start:04d}-{batch_end:04d}] ocr batch failed: {exc}")
            batch_start = batch_end + 1
            continue

        batch_elapsed = time.time() - ts
        batch_pages = len(images)
        batch_avg = batch_elapsed / max(1, batch_pages)

        for (page_num, pix, _, page_rect), ocr_result in zip(images, ocr_results):
            out_page = out_doc.new_page(width=page_rect.width, height=page_rect.height)
            out_page.insert_image(fitz.Rect(0, 0, page_rect.width, page_rect.height), stream=pix.tobytes("png"))

            text_scale_x = page_rect.width / pix.width
            text_scale_y = page_rect.height / pix.height
            text_count = 0

            for item in range(len(ocr_result["rec_texts"])):
                text = ocr_result["rec_texts"][item]
                score = ocr_result["rec_scores"][item]
                if not text or score < args.conf:
                    continue

                polygon = ocr_result["rec_polys"][item]
                xs = [float(p[0]) for p in polygon]
                ys = [float(p[1]) for p in polygon]
                x0 = min(xs) * text_scale_x
                y1 = max(ys) * text_scale_y

                box_h = max(1.0, (max(ys) - min(ys)) * text_scale_y)
                font_size = max(6.0, min(22.0, box_h * 0.9))
                out_page.insert_text(
                    (x0, y1),
                    text,
                    fontsize=font_size,
                    fontname="china-s",
                    color=(1.0, 1.0, 1.0),
                    render_mode=0,
                )
                text_count += 1

            total_secs += batch_avg
            processed += 1
            total_inserted += text_count
            print(
                f"[{page_num:04d}] processed with {text_count:4d} text blocks in {batch_elapsed:0.2f}s "
                f"(avg={total_secs / processed:0.2f}s) total text={total_inserted}"
            )

        if args.checkpoint_interval > 0 and processed % args.checkpoint_interval == 0:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            save_output(out_doc, output_path, should_resume, is_checkpoint=True)
            print(f"checkpoint saved at page {batch_end} -> {output_path}")

        batch_start = batch_end + 1

    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    save_output(out_doc, output_path, should_resume, is_checkpoint=False)
    out_doc.close()
    doc.close()

    print(f"done: saved {output_path}")
    print(f"pages processed: {processed}")
    print(f"text blocks inserted: {total_inserted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
