#!/usr/bin/env python3
import argparse
import json
import os
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
    "selenium",
    "websocket-client",
]

SOURCE_ROOT = Path(__file__).resolve().parents[1]


class TargetSafetyError(ValueError):
    """Raised before setup when a disposable target is unsafe to create."""


def absolute_path_without_resolving_symlinks(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return Path(os.path.abspath(os.fspath(path)))


def first_symlink_component(path: Path):
    for component in reversed((path, *path.parents)):
        if component.is_symlink():
            return component
    return None


def paths_overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def validate_new_target(venv_dir: Path) -> None:
    symlink = first_symlink_component(venv_dir)
    if symlink is not None:
        raise TargetSafetyError(
            f"refusing venv target with a final or ancestor symlink: {symlink}"
        )

    canonical_target = venv_dir.resolve(strict=False)
    if paths_overlap(canonical_target, SOURCE_ROOT):
        raise TargetSafetyError(
            "disposable venv target must not equal, contain, or be inside the "
            f"skill source: {SOURCE_ROOT}"
        )

    if os.path.lexists(venv_dir):
        raise TargetSafetyError(
            f"disposable venv target must not already exist: {venv_dir}"
        )


def prepare_new_target(venv_dir: Path) -> None:
    validate_new_target(venv_dir)
    try:
        venv_dir.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise TargetSafetyError(
            f"could not create the venv parent directory: {exc}"
        ) from exc

    # Parent creation may have exposed an existing symlink or a concurrent writer.
    validate_new_target(venv_dir)
    try:
        venv_dir.mkdir(mode=0o700, exist_ok=False)
    except FileExistsError as exc:
        raise TargetSafetyError(
            f"disposable venv target appeared before creation: {venv_dir}"
        ) from exc
    except OSError as exc:
        raise TargetSafetyError(f"could not create the venv target: {exc}") from exc

    symlink = first_symlink_component(venv_dir)
    if symlink is not None:
        raise TargetSafetyError(
            f"venv target became a symlink during creation: {symlink}"
        )


def bin_path(venv_dir: Path, name: str) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def create_venv(venv_dir: Path):
    try:
        builder = venv.EnvBuilder(with_pip=True, clear=False, symlinks=True)
        builder.create(str(venv_dir))
        return None, None
    except Exception as exc:
        ensurepip_error = {
            "type": exc.__class__.__name__,
            "message": str(exc),
        }
        try:
            fallback = venv.EnvBuilder(with_pip=False, clear=False, symlinks=True)
            fallback.create(str(venv_dir))
            return ensurepip_error, None
        except Exception as fallback_exc:
            return ensurepip_error, {
                "type": fallback_exc.__class__.__name__,
                "message": str(fallback_exc),
            }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", required=True, help="virtual environment path")
    parser.add_argument("--install", action="store_true", help="install recommended packages")
    parser.add_argument("--packages", nargs="*", default=PACKAGES, help="packages to install with --install")
    parser.add_argument("--json", action="store_true", help="print machine-readable result")
    args = parser.parse_args()
    if args.install and not args.packages:
        parser.error("--install requires at least one package")

    venv_dir = absolute_path_without_resolving_symlinks(args.venv)
    try:
        prepare_new_target(venv_dir)
    except TargetSafetyError as exc:
        if args.json:
            print(
                json.dumps(
                    {"venv": str(venv_dir), "safety_error": str(exc)},
                    indent=2,
                    ensure_ascii=False,
                )
            )
        print(f"error: {exc}", file=sys.stderr)
        return 2

    ensurepip_error, create_error = create_venv(venv_dir)

    python = bin_path(venv_dir, "python")
    pip = bin_path(venv_dir, "pip")
    python_available = python.exists()
    pip_available = pip.exists()
    installed = []
    install_error = None
    pip_stdout = ""
    pip_stderr = ""

    if args.install:
        if create_error:
            install_error = {
                "returncode": None,
                "command": None,
                "message": "virtual environment creation failed",
            }
        elif not pip_available:
            install_error = {
                "returncode": None,
                "command": None,
                "message": "pip is unavailable in this virtual environment; ensurepip failed",
            }
        else:
            cmd = [str(pip), "install", *args.packages]
            completed = subprocess.run(cmd, capture_output=True, text=True)
            pip_stdout = completed.stdout
            pip_stderr = completed.stderr
            if completed.returncode == 0:
                installed = list(args.packages)
            else:
                install_error = {
                    "returncode": completed.returncode,
                    "command": cmd,
                }

    result = {
        "venv": str(venv_dir),
        "python": str(python),
        "python_available": python_available,
        "pip": str(pip),
        "pip_available": pip_available,
        "ensurepip_error": ensurepip_error,
        "create_error": create_error,
        "install_requested": args.install,
        "packages": list(args.packages),
        "installed": installed,
        "install_error": install_error,
        "pip_stdout": pip_stdout,
        "pip_stderr": pip_stderr,
        "safety_error": None,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"venv: {venv_dir}")
        print(f"python: {python}")
        print(f"python_available: {python_available}")
        print(f"pip: {pip}")
        print(f"pip_available: {pip_available}")
        if ensurepip_error:
            print(f"ensurepip_error: {ensurepip_error}")
        if create_error:
            print(f"create_error: {create_error}")
        if pip_stdout:
            print(pip_stdout, file=sys.stderr, end="" if pip_stdout.endswith("\n") else "\n")
        if pip_stderr:
            print(pip_stderr, file=sys.stderr, end="" if pip_stderr.endswith("\n") else "\n")
        if args.install and install_error:
            print(f"install_error: {install_error}")
        elif args.install:
            print("installed:")
            for package in installed:
                print(f"- {package}")
        else:
            print("install: skipped")

    return 1 if create_error or not python_available or install_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
