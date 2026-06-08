#!/usr/bin/env python3
import argparse
import os
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPANION_ROOT = REPO_ROOT / "companion-skills"
DEFAULT_SKILLS = ("research-lr-ra", "zotero-linked-attachments")


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install vendored companion skills into $CODEX_HOME/skills."
    )
    parser.add_argument(
        "--dest",
        default=str(codex_home() / "skills"),
        help="Destination skills directory. Defaults to $CODEX_HOME/skills.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing installed companion skill directories.",
    )
    parser.add_argument(
        "skills",
        nargs="*",
        default=list(DEFAULT_SKILLS),
        help="Companion skill names to install.",
    )
    args = parser.parse_args()

    dest_root = Path(args.dest).expanduser().resolve()
    dest_root.mkdir(parents=True, exist_ok=True)

    installed = []
    skipped = []
    for skill_name in args.skills:
        src = COMPANION_ROOT / skill_name
        dst = dest_root / skill_name
        if not src.is_dir():
            raise SystemExit(f"Missing companion skill source: {src}")
        if dst.exists():
            if not args.force:
                skipped.append(str(dst))
                continue
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        installed.append(str(dst))

    print("installed:")
    for path in installed:
        print(f"- {path}")
    print("skipped:")
    for path in skipped:
        print(f"- {path}")


if __name__ == "__main__":
    main()
