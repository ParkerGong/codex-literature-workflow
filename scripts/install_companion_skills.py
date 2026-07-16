#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPANION_ROOT = REPO_ROOT / "companion-skills"
DEFAULT_SKILLS = ("research-lr-ra", "zotero-linked-attachments")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def validate_non_overlapping_paths(source: Path, destination: Path) -> None:
    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        reason = "source and destination are the same directory"
    elif destination.is_relative_to(source):
        reason = "destination is inside source"
    elif source.is_relative_to(destination):
        reason = "source is inside destination"
    else:
        return
    raise SystemExit(
        "Refusing overlapping install paths: "
        f"source={source}; destination={destination}; reason={reason}"
    )


def available_skills() -> tuple[str, ...]:
    return tuple(
        sorted(
            path.name
            for path in COMPANION_ROOT.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        )
    )


def validate_skill_name(skill_name: str, available: tuple[str, ...]) -> None:
    if not SKILL_NAME_PATTERN.fullmatch(skill_name):
        raise SystemExit(
            f"Invalid companion skill name: {skill_name!r}. "
            "Use a vendored lowercase hyphen-case basename."
        )
    if skill_name not in available:
        choices = ", ".join(available)
        raise SystemExit(f"Unknown companion skill: {skill_name}. Available: {choices}")


def deduplicate_skill_names(
    skill_names: list[str],
) -> tuple[tuple[str, ...], tuple[tuple[str, int], ...]]:
    """Keep first-seen order and return repeated names with total request counts."""
    counts: dict[str, int] = {}
    unique: list[str] = []
    for skill_name in skill_names:
        counts[skill_name] = counts.get(skill_name, 0) + 1
        if counts[skill_name] == 1:
            unique.append(skill_name)
    duplicates = tuple(
        (skill_name, counts[skill_name])
        for skill_name in unique
        if counts[skill_name] > 1
    )
    return tuple(unique), duplicates


def print_duplicate_report(duplicates: tuple[tuple[str, int], ...]) -> None:
    if not duplicates:
        return
    print("duplicate_requests_ignored:")
    for skill_name, request_count in duplicates:
        print(f"- {skill_name}: requested {request_count} times; processing once")


def main() -> int:
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
        help="Replace existing skills after moving them to a timestamped backup.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print actions without writing files.",
    )
    parser.add_argument(
        "skills",
        nargs="*",
        default=list(DEFAULT_SKILLS),
        help="Companion skill names to install.",
    )
    args = parser.parse_args()

    skill_names, duplicates = deduplicate_skill_names(args.skills)
    available = available_skills()
    for skill_name in skill_names:
        validate_skill_name(skill_name, available)

    dest_root = Path(args.dest).expanduser().resolve()
    if dest_root.exists() and not dest_root.is_dir():
        raise SystemExit(f"Destination is not a directory: {dest_root}")

    installed = []
    skipped = []
    backed_up = []
    planned = []
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_container = dest_root.parent / ".codex-literature-skill-backups"
    backup_root = backup_container / timestamp
    operations = []

    # Validate every requested destination before replacing the first skill.
    for skill_name in skill_names:
        src = (COMPANION_ROOT / skill_name).resolve()
        dst_candidate = dest_root / skill_name
        if dst_candidate.is_symlink():
            raise SystemExit(f"Refusing to replace symlink destination: {dst_candidate}")
        dst = dst_candidate.resolve()
        if src.parent != COMPANION_ROOT.resolve():
            raise SystemExit(f"Companion source escaped the vendored root: {src}")
        if dst.parent != dest_root:
            raise SystemExit(f"Companion destination escaped the skills root: {dst}")
        validate_non_overlapping_paths(src, dst)
        if not src.is_dir():
            raise SystemExit(f"Missing companion skill source: {src}")
        if dst.exists() and not dst.is_dir():
            raise SystemExit(f"Refusing to replace non-directory destination: {dst}")
        if dst.exists():
            if not args.force:
                skipped.append(str(dst))
                continue
            backup_path = backup_root / skill_name
            planned.append(f"backup {dst} -> {backup_path}")
            operations.append((src, dst, backup_path))
            continue
        planned.append(f"install {src} -> {dst}")
        operations.append((src, dst, None))

    if any(backup_path is not None for _, _, backup_path in operations):
        if backup_container.is_symlink():
            raise SystemExit(f"Refusing to use symlink backup directory: {backup_container}")
        if backup_container.exists() and not backup_container.is_dir():
            raise SystemExit(f"Backup path is not a directory: {backup_container}")
        if backup_container.resolve(strict=False).parent != dest_root.parent:
            raise SystemExit(f"Backup directory escaped the destination root: {backup_container}")

    if not args.dry_run:
        dest_root.mkdir(parents=True, exist_ok=True)
        for src, dst, backup_path in operations:
            staging = Path(
                tempfile.mkdtemp(prefix=f".{dst.name}-staging-", dir=str(dest_root))
            )
            staging.rmdir()
            try:
                shutil.copytree(
                    src,
                    staging,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
                )
                if backup_path is not None:
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    dst.rename(backup_path)
                    backed_up.append(str(backup_path))
                staging.rename(dst)
            except Exception:
                if staging.exists():
                    shutil.rmtree(staging)
                if backup_path is not None and backup_path.exists() and not dst.exists():
                    backup_path.rename(dst)
                    backed_up.remove(str(backup_path))
                raise
            installed.append(str(dst))

    if args.dry_run:
        print("planned:")
        for action in planned:
            print(f"- {action}")
        print("skipped:")
        for path in skipped:
            print(f"- {path}")
        print_duplicate_report(duplicates)
    else:
        print("installed:")
        for path in installed:
            print(f"- {path}")
        print("skipped:")
        for path in skipped:
            print(f"- {path}")
        print("backed_up:")
        for path in backed_up:
            print(f"- {path}")
        print_duplicate_report(duplicates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
