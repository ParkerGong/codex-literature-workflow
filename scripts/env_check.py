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

COMMANDS = ["pdftoppm", "pdftotext", "tesseract"]


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
    args = parser.parse_args()

    temp_dir = tempfile.gettempdir()
    report = {
        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },
        "packages": [
            package_status(module, display)
            for module, display in PACKAGES.items()
        ],
        "commands": [
            {"name": command, "path": shutil.which(command), "available": shutil.which(command) is not None}
            for command in COMMANDS
        ],
        "temp": {
            "dir": temp_dir,
            "writable": os.access(temp_dir, os.W_OK),
        },
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Codex Obsidian Read environment check")
        print(f"Python: {sys.executable}")
        for item in report["packages"]:
            state = "ok" if item["available"] else "missing"
            version = f" {item.get('version')}" if item.get("version") else ""
            print(f"- {item['name']}: {state}{version}")
        for item in report["commands"]:
            state = item["path"] or "missing"
            print(f"- {item['name']}: {state}")
        print(f"Temp writable: {report['temp']['writable']} ({temp_dir})")


if __name__ == "__main__":
    main()
