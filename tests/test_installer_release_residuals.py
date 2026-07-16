import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_INSTALLER = ROOT / "scripts" / "install_skill.py"
COMPANION_INSTALLER = ROOT / "scripts" / "install_companion_skills.py"
SKILL_NAME = "codex-literature-workflow"


def run(*args, env=None):
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


class MainInstallerBackupLocationTests(unittest.TestCase):
    def test_custom_destination_keeps_backup_in_its_direct_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "arbitrary" / "nested" / SKILL_NAME
            first = run(sys.executable, MAIN_INSTALLER, "--dest", destination)
            self.assertEqual(first.returncode, 0, first.stderr)
            (destination / "custom-marker.txt").write_text(
                "preserve me\n", encoding="utf-8"
            )

            forced = run(
                sys.executable,
                MAIN_INSTALLER,
                "--dest",
                destination,
                "--force",
            )
            self.assertEqual(forced.returncode, 0, forced.stderr)
            backups = list(
                (
                    destination.parent / ".codex-literature-skill-backups"
                ).glob(f"*/{SKILL_NAME}/custom-marker.txt")
            )
            self.assertEqual(len(backups), 1)
            self.assertEqual(
                backups[0].read_text(encoding="utf-8"), "preserve me\n"
            )
            self.assertFalse(
                (
                    destination.parent.parent
                    / ".codex-literature-skill-backups"
                ).exists()
            )

    def test_default_destination_preserves_codex_home_backup_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            codex_root = Path(tmp) / "codex-home"
            destination = codex_root / "skills" / SKILL_NAME
            env = os.environ.copy()
            env["CODEX_HOME"] = str(codex_root)

            first = run(sys.executable, MAIN_INSTALLER, env=env)
            self.assertEqual(first.returncode, 0, first.stderr)
            (destination / "default-marker.txt").write_text(
                "preserve me\n", encoding="utf-8"
            )
            forced = run(sys.executable, MAIN_INSTALLER, "--force", env=env)
            self.assertEqual(forced.returncode, 0, forced.stderr)

            backups = list(
                (codex_root / ".codex-literature-skill-backups").glob(
                    f"*/{SKILL_NAME}/default-marker.txt"
                )
            )
            self.assertEqual(len(backups), 1)
            self.assertFalse(
                (codex_root / "skills" / ".codex-literature-skill-backups").exists()
            )


class CompanionInstallerDeduplicationTests(unittest.TestCase):
    def test_repeated_names_are_processed_once_in_first_seen_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "skills"
            result = run(
                sys.executable,
                COMPANION_INSTALLER,
                "--dest",
                destination,
                "research-lr-ra",
                "zotero-linked-attachments",
                "research-lr-ra",
                "zotero-linked-attachments",
                "research-lr-ra",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            installed_lines = [
                line
                for line in result.stdout.splitlines()
                if line.startswith("- ") and ": requested " not in line
            ]
            self.assertEqual(
                installed_lines,
                [
                    f"- {destination.resolve() / 'research-lr-ra'}",
                    f"- {destination.resolve() / 'zotero-linked-attachments'}",
                ],
            )
            self.assertIn("duplicate_requests_ignored:", result.stdout)
            self.assertIn(
                "- research-lr-ra: requested 3 times; processing once",
                result.stdout,
            )
            self.assertIn(
                "- zotero-linked-attachments: requested 2 times; processing once",
                result.stdout,
            )
            self.assertTrue((destination / "research-lr-ra" / "SKILL.md").is_file())
            self.assertTrue(
                (destination / "zotero-linked-attachments" / "SKILL.md").is_file()
            )


if __name__ == "__main__":
    unittest.main()
