#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def parse_pages(value):
    pages = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))


def extract_text_pypdf(pdf_path, pages, out_dir):
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    text_dir = out_dir / "texts"
    text_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for page_num in pages:
        if page_num < 1 or page_num > len(reader.pages):
            rows.append({"page": page_num, "ok": False, "error": "page out of range"})
            continue
        text = reader.pages[page_num - 1].extract_text() or ""
        path = text_dir / f"p{page_num:03d}.txt"
        path.write_text(text, encoding="utf-8")
        rows.append({"page": page_num, "ok": True, "chars": len(text), "text_path": str(path)})
    return len(reader.pages), rows


def render_pages_fitz(pdf_path, pages, out_dir, dpi):
    import fitz
    from PIL import Image

    render_dir = out_dir / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    rows = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    for page_num in pages:
        if page_num < 1 or page_num > doc.page_count:
            rows.append({"page": page_num, "ok": False, "error": "page out of range"})
            continue
        page = doc.load_page(page_num - 1)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        path = render_dir / f"p{page_num:03d}_{dpi}dpi.jpg"
        pix.save(str(path), jpg_quality=84)
        with Image.open(path) as image:
            width, height = image.size
        rows.append({
            "page": page_num,
            "ok": True,
            "render_path": str(path),
            "bytes": path.stat().st_size,
            "width": width,
            "height": height,
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("--pages", default="1", help="1-based pages, e.g. 1,3,9-11")
    parser.add_argument("--out", required=True)
    parser.add_argument("--dpi", type=int, default=144)
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = parse_pages(args.pages)

    report = {
        "pdf": str(pdf_path),
        "pages_requested": pages,
        "text": {"ok": False},
        "render": {"ok": False, "skipped": args.no_render},
    }

    try:
        page_count, text_rows = extract_text_pypdf(pdf_path, pages, out_dir)
        report["page_count"] = page_count
        report["text"] = {"ok": True, "pages": text_rows}
    except Exception as exc:
        report["text"] = {"ok": False, "error": str(exc)}

    if not args.no_render:
        try:
            render_rows = render_pages_fitz(pdf_path, pages, out_dir, args.dpi)
            report["render"] = {"ok": True, "dpi": args.dpi, "pages": render_rows}
        except Exception as exc:
            report["render"] = {"ok": False, "error": str(exc)}

    report_path = out_dir / "probe_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
