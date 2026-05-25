#!/usr/bin/env python3
"""Extract a page range from a PDF and save to a new PDF.

Usage example:
  python extract_pdf_pages.py 1.pdf 2.pdf 179 242
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract selected pages from a PDF into a new PDF."
    )
    parser.add_argument("input_pdf", type=Path, help="Path to input PDF")
    parser.add_argument("output_pdf", type=Path, help="Path to output PDF")
    parser.add_argument("start_page", type=int, help="Start page number (1-based)")
    parser.add_argument("end_page", type=int, help="End page number (1-based, inclusive)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input_pdf.exists():
        print(f"Error: input file not found: {args.input_pdf}")
        return 1

    if args.start_page < 1 or args.end_page < 1:
        print("Error: page numbers must be >= 1")
        return 1

    if args.start_page > args.end_page:
        print("Error: start_page cannot be greater than end_page")
        return 1

    try:
        reader = PdfReader(str(args.input_pdf))
    except Exception as exc:  # pragma: no cover
        print(f"Error: failed to read input PDF: {exc}")
        return 1

    total_pages = len(reader.pages)
    if args.end_page > total_pages:
        print(
            f"Error: end_page ({args.end_page}) exceeds total pages ({total_pages})"
        )
        return 1

    writer = PdfWriter()
    # Convert to 0-based indexes for pypdf.
    for idx in range(args.start_page - 1, args.end_page):
        writer.add_page(reader.pages[idx])

    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)

    try:
        with args.output_pdf.open("wb") as out_file:
            writer.write(out_file)
    except Exception as exc:  # pragma: no cover
        print(f"Error: failed to write output PDF: {exc}")
        return 1

    extracted = args.end_page - args.start_page + 1
    print(
        f"Done: extracted {extracted} page(s) from page {args.start_page} to {args.end_page}."
    )
    print(f"Output: {args.output_pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
