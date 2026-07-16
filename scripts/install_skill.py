#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "codex-literature-workflow"
PACKAGE_ENTRIES = (
    "SKILL.md",
    "agents",
    "scripts",
    "references",
    "companion-skills",
    "environment.yml",
    "requirements.txt",
    "requirements-dev.txt",
    "VERSION",
    "LICENSE",
)


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_destination() -> Path:
    return codex_home() / "skills" / SKILL_NAME


def backup_container_for_destination(destination: Path) -> tuple[Path, Path]:
    """Return the backup container and the directory it must remain within."""
    resolved_default = default_destination().resolve()
    if destination == resolved_default:
        backup_scope = resolved_default.parent.parent
    else:
        # A custom destination has no implied ``<root>/skills/<skill>`` layout.
        # Keep its backups beside that destination instead of escaping one level.
        backup_scope = destination.parent
    return backup_scope / ".codex-literature-skill-backups", backup_scope


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


def copy_package(staging: Path) -> None:
    staging.mkdir(parents=True, exist_ok=False)
    for name in PACKAGE_ENTRIES:
        source = REPO_ROOT / name
        if not source.exists():
            raise FileNotFoundError(f"Required package entry is missing: {source}")
        target = staging / name
        if source.is_dir():
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
        else:
            shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Install {SKILL_NAME} into the local Codex skills directory."
    )
    parser.add_argument(
        "--dest",
        default=str(default_destination()),
        help=f"Destination skill directory. Defaults to $CODEX_HOME/skills/{SKILL_NAME}.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing installation after moving it to a timestamped backup.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the action without writing files.",
    )
    args = parser.parse_args()

    logical_dest = Path(args.dest).expanduser()
    if logical_dest.is_symlink():
        raise SystemExit(f"Refusing to replace symlink destination: {logical_dest}")
    dest = logical_dest.resolve()
    validate_non_overlapping_paths(REPO_ROOT, dest)
    if dest.name != SKILL_NAME:
        raise SystemExit(f"Destination directory must be named {SKILL_NAME}: {dest}")
    if dest.exists() and not dest.is_dir():
        raise SystemExit(f"Destination is not a directory: {dest}")
    for name in PACKAGE_ENTRIES:
        if not (REPO_ROOT / name).exists():
            raise SystemExit(f"Required package entry is missing: {REPO_ROOT / name}")

    if dest.exists() and not args.force:
        print(f"skipped: {dest}")
        print("reason: destination exists; use --force for a backed-up replacement")
        return 0

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_container, backup_scope = backup_container_for_destination(dest)
    backup = backup_container / timestamp / SKILL_NAME
    if dest.exists():
        if backup_container.is_symlink():
            raise SystemExit(f"Refusing to use symlink backup directory: {backup_container}")
        if backup_container.exists() and not backup_container.is_dir():
            raise SystemExit(f"Backup path is not a directory: {backup_container}")
        if backup_container.resolve(strict=False).parent != backup_scope:
            raise SystemExit(
                f"Backup directory escaped its permitted scope: {backup_container}"
            )
        validate_non_overlapping_paths(REPO_ROOT, backup_container)
    action = "replace" if dest.exists() else "install"
    print(f"planned: {action} {REPO_ROOT} -> {dest}")
    if dest.exists():
        print(f"planned_backup: {dest} -> {backup}")
    if args.dry_run:
        return 0

    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{SKILL_NAME}-staging-", dir=str(dest.parent))
    )
    # mkdtemp creates the directory; copy_package expects to create it.
    staging.rmdir()
    try:
        copy_package(staging)
        if dest.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            dest.rename(backup)
        staging.rename(dest)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if backup.exists() and not dest.exists():
            backup.rename(dest)
        raise

    print(f"installed: {dest}")
    if backup.exists():
        print(f"backed_up: {backup}")
    print(f"next: invoke ${SKILL_NAME} in a new Codex task")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
