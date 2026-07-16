#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS = (
    ROOT,
    ROOT / "companion-skills" / "research-lr-ra",
    ROOT / "companion-skills" / "zotero-linked-attachments",
)
FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
OPENAI_TOP_KEYS = {"interface", "policy"}
INTERFACE_KEYS = {"display_name", "short_description", "default_prompt"}


def read_yaml(path):
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot parse YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("YAML root must be a mapping")
    return value


def validate_skill(skill_dir):
    errors = []
    skill_md = skill_dir / "SKILL.md"
    metadata_path = skill_dir / "agents" / "openai.yaml"
    if not skill_md.is_file():
        return [f"{skill_md}: missing"]

    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", content, re.DOTALL)
    if not match:
        return [f"{skill_md}: invalid or missing YAML frontmatter"]
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"{skill_md}: invalid YAML frontmatter: {exc}"]
    if not isinstance(frontmatter, dict):
        return [f"{skill_md}: frontmatter must be a mapping"]

    unexpected = set(frontmatter) - FRONTMATTER_KEYS
    if unexpected:
        errors.append(f"{skill_md}: unexpected frontmatter keys: {sorted(unexpected)}")
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append(f"{skill_md}: name must be lowercase hyphen-case")
    elif len(name) > 64:
        errors.append(f"{skill_md}: name exceeds 64 characters")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_md}: description must be a nonempty string")
    elif len(description.strip()) > 1024 or "<" in description or ">" in description:
        errors.append(f"{skill_md}: description violates length/angle-bracket constraints")

    if not metadata_path.is_file():
        errors.append(f"{metadata_path}: missing")
        return errors
    try:
        metadata = read_yaml(metadata_path)
    except ValueError as exc:
        errors.append(f"{metadata_path}: {exc}")
        return errors
    unexpected_top = set(metadata) - OPENAI_TOP_KEYS
    if unexpected_top:
        errors.append(f"{metadata_path}: unexpected top-level keys: {sorted(unexpected_top)}")
    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{metadata_path}: interface must be a mapping")
        return errors
    unexpected_interface = set(interface) - INTERFACE_KEYS
    if unexpected_interface:
        errors.append(
            f"{metadata_path}: unexpected interface keys: {sorted(unexpected_interface)}"
        )
    for field in INTERFACE_KEYS:
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            errors.append(f"{metadata_path}: interface.{field} must be nonempty")
    short = interface.get("short_description", "")
    if isinstance(short, str) and not 25 <= len(short) <= 64:
        errors.append(f"{metadata_path}: short_description must be 25-64 characters")
    prompt = interface.get("default_prompt", "")
    if isinstance(name, str) and isinstance(prompt, str) and f"${name}" not in prompt:
        errors.append(f"{metadata_path}: default_prompt must mention ${name}")

    policy = metadata.get("policy")
    if policy is not None:
        if not isinstance(policy, dict):
            errors.append(f"{metadata_path}: policy must be a mapping")
        else:
            unexpected_policy = set(policy) - {"allow_implicit_invocation"}
            if unexpected_policy:
                errors.append(
                    f"{metadata_path}: unexpected policy keys: {sorted(unexpected_policy)}"
                )
            if "allow_implicit_invocation" in policy and not isinstance(
                policy["allow_implicit_invocation"], bool
            ):
                errors.append(
                    f"{metadata_path}: allow_implicit_invocation must be boolean"
                )
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate SKILL.md frontmatter and agents/openai.yaml metadata."
    )
    parser.add_argument("skills", nargs="*", help="skill directories; defaults to all bundled skills")
    args = parser.parse_args()
    skill_dirs = [Path(value).expanduser().resolve() for value in args.skills] or list(
        DEFAULT_SKILLS
    )
    errors = []
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    for skill_dir in skill_dirs:
        print(f"valid: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
