#!/usr/bin/env python3
import argparse
import importlib
import json
import os
import shutil
import sys
import tempfile


PACKAGES = {
    "pypdf": "pypdf",
    "pdfplumber": "pdfplumber",
    "fitz": "PyMuPDF",
    "PIL": "Pillow",
    "requests": "requests",
    "bs4": "beautifulsoup4",
    "selenium": "selenium",
    "websocket": "websocket-client",
}

COMMANDS = [
    "pdftoppm",
    "pdftotext",
    "tesseract",
    "micromamba",
    "mamba",
    "conda",
    "node",
    "qmd",
]


def package_status(module_name, display_name):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", None)
        if version is None and module_name == "fitz":
            version = getattr(module, "version", [None])[0]
        return {
            "name": display_name,
            "module": module_name,
            "available": True,
            "version": version,
        }
    except Exception as exc:
        return {
            "name": display_name,
            "module": module_name,
            "available": False,
            "error": str(exc),
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="print JSON only")
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "exit non-zero when PDF encryption checking or the core "
            "text/render path is unavailable"
        ),
    )
    args = parser.parse_args()

    temp_dir = tempfile.gettempdir()
    packages = [
        package_status(module, display)
        for module, display in PACKAGES.items()
    ]
    commands = []
    for command in COMMANDS:
        command_path = shutil.which(command)
        commands.append(
            {
                "name": command,
                "path": command_path,
                "available": command_path is not None,
            }
        )

    package_by_module = {item["module"]: item for item in packages}
    command_by_name = {item["name"]: item for item in commands}
    temp_writable = os.access(temp_dir, os.W_OK)
    pdf_text_ready = any(
        package_by_module[module]["available"]
        for module in ("pypdf", "pdfplumber")
    )
    pdf_encryption_check_ready = package_by_module["pypdf"]["available"]
    pdf_render_ready = (
        package_by_module["fitz"]["available"]
        or command_by_name["pdftoppm"]["available"]
    )
    capabilities = {
        "core_ready": (
            pdf_text_ready
            and pdf_encryption_check_ready
            and pdf_render_ready
            and temp_writable
        ),
        "pdf_text_ready": pdf_text_ready,
        "pdf_encryption_check_ready": pdf_encryption_check_ready,
        "pdf_render_ready": pdf_render_ready,
        "metadata_http_ready": (
            package_by_module["requests"]["available"]
            and package_by_module["bs4"]["available"]
        ),
        "authorized_browser_python_ready": (
            package_by_module["selenium"]["available"]
            and package_by_module["websocket"]["available"]
        ),
        "ocr_ready": command_by_name["tesseract"]["available"],
        "python_environment_manager_ready": any(
            command_by_name[name]["available"]
            for name in ("micromamba", "mamba", "conda")
        ),
        "qmd_cli_present": command_by_name["qmd"]["available"],
    }
    report = {
        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },
        "packages": packages,
        "commands": commands,
        "temp": {
            "dir": temp_dir,
            "writable": temp_writable,
        },
        "capabilities": capabilities,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Codex Literature Workflow environment check")
        print(f"Python: {sys.executable}")
        for item in report["packages"]:
            state = "ok" if item["available"] else "missing"
            version = f" {item.get('version')}" if item.get("version") else ""
            print(f"- {item['name']}: {state}{version}")
        for item in report["commands"]:
            state = item["path"] or "missing"
            print(f"- {item['name']}: {state}")
        print(f"Temp writable: {report['temp']['writable']} ({temp_dir})")
        print("Capabilities:")
        for name, available in capabilities.items():
            print(f"- {name}: {'yes' if available else 'no'}")

    return 1 if args.strict and not capabilities["core_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
