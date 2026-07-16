#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from pathlib import Path


MAX_SELECTED_PAGES = 100
MAX_DPI = 600
RENDER_TIMEOUT_SECONDS = 120


def validate_output_directory(root, name):
    directory = root / name
    if directory.is_symlink():
        raise RuntimeError(f"refusing symlink output directory: {directory}")
    if directory.exists() and not directory.is_dir():
        raise RuntimeError(f"output directory path is not a directory: {directory}")
    resolved_parent = directory.parent.resolve()
    if resolved_parent != root and root not in resolved_parent.parents:
        raise RuntimeError(f"output directory escaped the requested root: {directory}")
    return directory


def ensure_output_directory(root, name):
    directory = validate_output_directory(root, name)
    directory.mkdir(parents=True, exist_ok=True)
    if directory.resolve() != directory:
        raise RuntimeError(f"output directory resolved unexpectedly: {directory}")
    return directory


def reject_input_output_alias(input_path, file_path):
    # Missing inputs still need the normal exit-2 report.  There is no source
    # inode to protect until the input is a real regular file.
    if input_path is None or not input_path.is_file():
        return

    if file_path == input_path:
        raise RuntimeError(
            f"refusing canonical input/output alias: {file_path}"
        )

    input_resolved = input_path.resolve()
    output_resolved = file_path.resolve()
    if output_resolved == input_resolved:
        raise RuntimeError(
            f"refusing symlink-resolved input/output alias: {file_path}"
        )

    if file_path.exists():
        input_stat = input_path.stat()
        output_stat = file_path.stat()
        if (input_stat.st_dev, input_stat.st_ino) == (
            output_stat.st_dev,
            output_stat.st_ino,
        ):
            raise RuntimeError(
                f"refusing inode/hardlink input/output alias: {file_path}"
            )


def safe_output_file(root, file_path, input_path=None):
    reject_input_output_alias(input_path, file_path)
    if file_path.is_symlink():
        raise RuntimeError(f"refusing symlink output file: {file_path}")
    resolved_parent = file_path.parent.resolve()
    if resolved_parent != root and root not in resolved_parent.parents:
        raise RuntimeError(f"output file escaped the requested root: {file_path}")
    if file_path.exists() and not file_path.is_file():
        raise RuntimeError(f"output file path is not a regular file: {file_path}")
    if file_path.exists() and file_path.stat().st_nlink > 1:
        raise RuntimeError(f"refusing hard-linked output file: {file_path}")
    return file_path


def text_output_path(out_dir, page_num):
    return out_dir / "texts" / f"p{page_num:03d}.txt"


def render_output_path(out_dir, page_num, dpi):
    return out_dir / "renders" / f"p{page_num:03d}_{dpi}dpi.jpg"


def preflight_outputs(pdf_path, out_dir, pages, dpi, no_render):
    """Validate the complete output plan before creating or writing anything."""
    validate_output_directory(out_dir, "texts")
    if not no_render:
        validate_output_directory(out_dir, "renders")

    targets = [out_dir / "probe_report.json"]
    targets.extend(text_output_path(out_dir, page_num) for page_num in pages)
    if not no_render:
        targets.extend(
            render_output_path(out_dir, page_num, dpi) for page_num in pages
        )
    for target in targets:
        safe_output_file(out_dir, target, pdf_path)


def write_report(report_path, report, out_dir, pdf_path):
    # Recheck at the actual write point as a defense against stale preflight
    # state and against direct callers that bypass main().
    safe_output_file(out_dir, report_path, pdf_path)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def inspect_pdf_encryption(pdf_path):
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path), strict=False)
    return {
        "encrypted": bool(reader.is_encrypted),
        "encryption_check": {"ok": True, "backend": "pypdf"},
    }


def parse_pages(value):
    pages = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            if part.count("-") != 1:
                raise ValueError(f"invalid page range: {part}")
            start, end = part.split("-", 1)
            start_num = int(start)
            end_num = int(end)
            if start_num < 1 or end_num < 1:
                raise ValueError("page numbers must be positive")
            if start_num > end_num:
                raise ValueError(f"page range start exceeds end: {part}")
            if end_num - start_num + 1 > MAX_SELECTED_PAGES:
                raise ValueError(
                    f"a page range may select at most {MAX_SELECTED_PAGES} pages"
                )
            pages.extend(range(start_num, end_num + 1))
        else:
            page_num = int(part)
            if page_num < 1:
                raise ValueError("page numbers must be positive")
            pages.append(page_num)
    pages = sorted(set(pages))
    if not pages:
        raise ValueError("at least one page must be selected")
    if len(pages) > MAX_SELECTED_PAGES:
        raise ValueError(f"select at most {MAX_SELECTED_PAGES} pages per probe")
    return pages


def extract_text_pypdf(pdf_path, pages, out_dir):
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    text_dir = ensure_output_directory(out_dir, "texts")
    rows = []
    for page_num in pages:
        if page_num < 1 or page_num > len(reader.pages):
            rows.append({"page": page_num, "ok": False, "error": "page out of range"})
            continue
        text = reader.pages[page_num - 1].extract_text() or ""
        path = safe_output_file(
            out_dir, text_output_path(out_dir, page_num), pdf_path
        )
        path.write_text(text, encoding="utf-8")
        rows.append({"page": page_num, "ok": True, "chars": len(text), "text_path": str(path)})
    return len(reader.pages), rows


def extract_text_pdfplumber(pdf_path, pages, out_dir):
    import pdfplumber

    text_dir = ensure_output_directory(out_dir, "texts")
    rows = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        page_count = len(pdf.pages)
        for page_num in pages:
            if page_num < 1 or page_num > page_count:
                rows.append({"page": page_num, "ok": False, "error": "page out of range"})
                continue
            text = pdf.pages[page_num - 1].extract_text() or ""
            path = safe_output_file(
                out_dir, text_output_path(out_dir, page_num), pdf_path
            )
            path.write_text(text, encoding="utf-8")
            rows.append({"page": page_num, "ok": True, "chars": len(text), "text_path": str(path)})
    return page_count, rows


def extract_text(pdf_path, pages, out_dir):
    errors = []
    for backend, function in (
        ("pypdf", extract_text_pypdf),
        ("pdfplumber", extract_text_pdfplumber),
    ):
        try:
            page_count, rows = function(pdf_path, pages, out_dir)
            return page_count, rows, backend, errors
        except Exception as exc:
            errors.append({"backend": backend, "error": str(exc)})
    raise RuntimeError("; ".join(f"{item['backend']}: {item['error']}" for item in errors))


def render_pages_fitz(pdf_path, pages, out_dir, dpi):
    import fitz

    render_dir = ensure_output_directory(out_dir, "renders")
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
        path = safe_output_file(
            out_dir, render_output_path(out_dir, page_num, dpi), pdf_path
        )
        pix.save(str(path), jpg_quality=84)
        rows.append({
            "page": page_num,
            "ok": True,
            "render_path": str(path),
            "bytes": path.stat().st_size,
            "width": pix.width,
            "height": pix.height,
        })
    doc.close()
    return rows


def render_pages_poppler(pdf_path, pages, out_dir, dpi, page_count=None):
    executable = shutil.which("pdftoppm")
    if not executable:
        raise RuntimeError("pdftoppm is unavailable")

    render_dir = ensure_output_directory(out_dir, "renders")
    rows = []
    for page_num in pages:
        if page_count is not None and page_num > page_count:
            rows.append({"page": page_num, "ok": False, "error": "page out of range"})
            continue
        path = safe_output_file(
            out_dir, render_output_path(out_dir, page_num, dpi), pdf_path
        )
        prefix = path.with_suffix("")
        cmd = [
            executable,
            "-f",
            str(page_num),
            "-l",
            str(page_num),
            "-r",
            str(dpi),
            "-jpeg",
            "-singlefile",
            str(pdf_path),
            str(prefix),
        ]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT_SECONDS,
        )
        if completed.returncode != 0 or not path.is_file():
            message = completed.stderr.strip() or completed.stdout.strip() or "pdftoppm failed"
            rows.append({"page": page_num, "ok": False, "error": message})
            continue

        width = None
        height = None
        try:
            from PIL import Image

            with Image.open(path) as image:
                width, height = image.size
        except Exception:
            pass
        rows.append({
            "page": page_num,
            "ok": True,
            "render_path": str(path),
            "bytes": path.stat().st_size,
            "width": width,
            "height": height,
        })
    return rows


def render_pages(pdf_path, pages, out_dir, dpi, page_count=None):
    errors = []
    for backend, function in (
        ("pymupdf", lambda: render_pages_fitz(pdf_path, pages, out_dir, dpi)),
        ("pdftoppm", lambda: render_pages_poppler(pdf_path, pages, out_dir, dpi, page_count)),
    ):
        try:
            return function(), backend, errors
        except Exception as exc:
            errors.append({"backend": backend, "error": str(exc)})
    raise RuntimeError("; ".join(f"{item['backend']}: {item['error']}" for item in errors))


def rows_ok(rows):
    return bool(rows) and all(row.get("ok") for row in rows)


def text_rows_ok(rows):
    return rows_ok(rows) and sum(row.get("chars", 0) for row in rows) > 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("--pages", default="1", help="1-based pages, e.g. 1,3,9-11")
    parser.add_argument("--out", required=True)
    parser.add_argument("--dpi", type=int, default=144)
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()

    try:
        pages = parse_pages(args.pages)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    if args.dpi < 36:
        parser.error("--dpi must be at least 36")
    if args.dpi > MAX_DPI:
        parser.error(f"--dpi must not exceed {MAX_DPI}")

    pdf_path = Path(args.pdf).expanduser().resolve()
    logical_out = Path(args.out).expanduser()
    if logical_out.is_symlink():
        parser.error(f"refusing symlink --out directory: {logical_out}")
    if logical_out.exists() and not logical_out.is_dir():
        parser.error(f"--out is not a directory: {logical_out}")
    out_dir = logical_out.resolve()
    try:
        preflight_outputs(pdf_path, out_dir, pages, args.dpi, args.no_render)
    except RuntimeError as exc:
        parser.error(str(exc))
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "probe_report.json"

    report = {
        "pdf": str(pdf_path),
        "pages_requested": pages,
        "text": {"ok": False},
        "render": {"ok": False, "skipped": args.no_render},
    }

    if not pdf_path.is_file():
        report["input"] = {
            "ok": False,
            "error": "PDF file does not exist",
            "encrypted": None,
            "encryption_check": {
                "ok": False,
                "skipped": True,
                "reason": "PDF file does not exist",
            },
        }
        try:
            write_report(report_path, report, out_dir, pdf_path)
        except RuntimeError as exc:
            parser.error(str(exc))
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 2

    report["input"] = {"ok": True, "bytes": pdf_path.stat().st_size}
    try:
        report["input"].update(inspect_pdf_encryption(pdf_path))
    except Exception as exc:
        report["input"].update({
            "encrypted": None,
            "status": "encryption-check-failed",
            "encryption_check": {"ok": False, "error": str(exc)},
        })
        report["text"]["reason"] = "PDF encryption status could not be verified"
        report["render"] = {
            "ok": False,
            "skipped": True,
            "reason": "PDF encryption status could not be verified",
        }
        try:
            write_report(report_path, report, out_dir, pdf_path)
        except RuntimeError as write_exc:
            parser.error(str(write_exc))
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    if report["input"]["encrypted"]:
        report["input"]["status"] = "encrypted"
        report["text"]["reason"] = "encrypted PDF requires manual handling"
        report["render"] = {
            "ok": False,
            "skipped": True,
            "reason": "encrypted PDF requires manual handling",
        }
        try:
            write_report(report_path, report, out_dir, pdf_path)
        except RuntimeError as exc:
            parser.error(str(exc))
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    report["input"]["status"] = "ready"
    page_count = None

    try:
        page_count, text_rows, backend, fallback_errors = extract_text(pdf_path, pages, out_dir)
        report["page_count"] = page_count
        chars_total = sum(row.get("chars", 0) for row in text_rows)
        report["text"] = {
            "ok": text_rows_ok(text_rows),
            "backend": backend,
            "fallback_errors": fallback_errors,
            "chars_total": chars_total,
            "text_layer_present": chars_total > 0,
            "pages": text_rows,
        }
        if chars_total == 0:
            report["text"]["reason"] = "no extractable text on selected pages"
    except Exception as exc:
        report["text"] = {"ok": False, "error": str(exc)}

    if not args.no_render:
        try:
            render_rows, backend, fallback_errors = render_pages(
                pdf_path, pages, out_dir, args.dpi, page_count
            )
            report["render"] = {
                "ok": rows_ok(render_rows),
                "backend": backend,
                "fallback_errors": fallback_errors,
                "dpi": args.dpi,
                "pages": render_rows,
            }
        except Exception as exc:
            report["render"] = {"ok": False, "error": str(exc)}

    try:
        write_report(report_path, report, out_dir, pdf_path)
    except RuntimeError as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    success = report["text"]["ok"] and (args.no_render or report["render"]["ok"])
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
