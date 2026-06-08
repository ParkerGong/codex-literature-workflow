#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import venv
from pathlib import Path


PACKAGES = [
    "pypdf",
    "pdfplumber",
    "pymupdf",
    "pillow",
    "requests",
    "beautifulsoup4",
]


def bin_path(venv_dir: Path, name: str) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def create_venv(venv_dir: Path):
    try:
        builder = venv.EnvBuilder(with_pip=True, clear=False, symlinks=True)
        builder.create(str(venv_dir))
        return None
    except Exception as exc:
        fallback = venv.EnvBuilder(with_pip=False, clear=False, symlinks=True)
        fallback.create(str(venv_dir))
        return {
            "type": exc.__class__.__name__,
            "message": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", required=True, help="virtual environment path")
    parser.add_argument("--install", action="store_true", help="install recommended packages")
    parser.add_argument("--packages", nargs="*", default=PACKAGES, help="packages to install with --install")
    parser.add_argument("--json", action="store_true", help="print machine-readable result")
    args = parser.parse_args()

    venv_dir = Path(args.venv).expanduser().resolve()
    venv_dir.parent.mkdir(parents=True, exist_ok=True)
    ensurepip_error = create_venv(venv_dir)

    python = bin_path(venv_dir, "python")
    pip = bin_path(venv_dir, "pip")
    pip_available = pip.exists()
    installed = []
    install_error = None

    if args.install:
        if not pip_available:
            install_error = {
                "returncode": None,
                "command": None,
                "message": "pip is unavailable in this virtual environment; ensurepip failed",
            }
        else:
            cmd = [str(pip), "install", *args.packages]
            try:
                subprocess.run(cmd, check=True)
                installed = list(args.packages)
            except subprocess.CalledProcessError as exc:
                install_error = {
                    "returncode": exc.returncode,
                    "command": cmd,
                }

    result = {
        "venv": str(venv_dir),
        "python": str(python),
        "pip": str(pip),
        "pip_available": pip_available,
        "ensurepip_error": ensurepip_error,
        "install_requested": args.install,
        "packages": list(args.packages),
        "installed": installed,
        "install_error": install_error,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"venv: {venv_dir}")
        print(f"python: {python}")
        print(f"pip: {pip}")
        print(f"pip_available: {pip_available}")
        if ensurepip_error:
            print(f"ensurepip_error: {ensurepip_error}")
        if args.install and install_error:
            print(f"install_error: {install_error}")
        elif args.install:
            print("installed:")
            for package in installed:
                print(f"- {package}")
        else:
            print("install: skipped")

    return 1 if install_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
