import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "codex-literature-workflow"
COMPANION_NAME = "research-lr-ra"


def load_script(module_name, relative_path):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MainInstallerOverlapTests(unittest.TestCase):
    def setUp(self):
        self.installer = load_script(
            "install_skill_overlap_test", "scripts/install_skill.py"
        )

    def test_rejects_all_overlap_relations_in_dry_run_and_real_modes(self):
        for relation in ("same", "destination-inside", "source-inside"):
            for dry_run in (True, False):
                with self.subTest(relation=relation, dry_run=dry_run):
                    with tempfile.TemporaryDirectory() as tmp:
                        base = Path(tmp)
                        if relation == "same":
                            source = base / SKILL_NAME
                            destination = source
                            source.mkdir()
                        elif relation == "destination-inside":
                            source = base / "source-checkout"
                            destination = source / SKILL_NAME
                            source.mkdir()
                        else:
                            destination = base / SKILL_NAME
                            source = destination / "source-checkout"
                            source.mkdir(parents=True)

                        marker = source / "source-marker.txt"
                        marker.write_text("unchanged\n", encoding="utf-8")
                        destination_existed = destination.exists()
                        argv = ["install_skill.py", "--dest", str(destination)]
                        if dry_run:
                            argv.append("--dry-run")

                        with mock.patch.object(
                            self.installer, "REPO_ROOT", source
                        ), mock.patch.object(sys, "argv", argv):
                            with self.assertRaisesRegex(
                                SystemExit, "overlapping install paths"
                            ):
                                self.installer.main()

                        self.assertEqual(
                            destination.exists(), destination_existed
                        )
                        self.assertEqual(
                            marker.read_text(encoding="utf-8"), "unchanged\n"
                        )


class CompanionInstallerOverlapTests(unittest.TestCase):
    def setUp(self):
        self.installer = load_script(
            "install_companion_overlap_test",
            "scripts/install_companion_skills.py",
        )

    def test_rejects_all_overlap_relations_in_dry_run_and_real_modes(self):
        for relation in ("same", "destination-inside", "source-inside"):
            for dry_run in (True, False):
                with self.subTest(relation=relation, dry_run=dry_run):
                    with tempfile.TemporaryDirectory() as tmp:
                        base = Path(tmp)
                        if relation == "same":
                            companion_root = base / "companions"
                            destination_root = companion_root
                        elif relation == "destination-inside":
                            companion_root = base / "companions"
                            destination_root = (
                                companion_root / COMPANION_NAME / "nested-skills"
                            )
                        else:
                            destination_root = base / "skills"
                            companion_root = (
                                destination_root / COMPANION_NAME / "vendored"
                            )

                        source = companion_root / COMPANION_NAME
                        source.mkdir(parents=True)
                        (source / "SKILL.md").write_text(
                            "---\nname: research-lr-ra\ndescription: test\n---\n",
                            encoding="utf-8",
                        )
                        marker = source / "source-marker.txt"
                        marker.write_text("unchanged\n", encoding="utf-8")
                        destination_root_existed = destination_root.exists()
                        argv = [
                            "install_companion_skills.py",
                            "--dest",
                            str(destination_root),
                        ]
                        if dry_run:
                            argv.append("--dry-run")
                        argv.append(COMPANION_NAME)

                        with mock.patch.object(
                            self.installer, "COMPANION_ROOT", companion_root
                        ), mock.patch.object(sys, "argv", argv):
                            with self.assertRaisesRegex(
                                SystemExit, "overlapping install paths"
                            ):
                                self.installer.main()

                        self.assertEqual(
                            destination_root.exists(), destination_root_existed
                        )
                        self.assertEqual(
                            marker.read_text(encoding="utf-8"), "unchanged\n"
                        )

    def test_preflights_every_source_before_installing_any_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            destination_root = base / "skills"
            companion_root = (
                destination_root / "zotero-linked-attachments" / "vendored"
            )
            for skill_name in ("research-lr-ra", "zotero-linked-attachments"):
                source = companion_root / skill_name
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(
                    f"---\nname: {skill_name}\ndescription: test\n---\n",
                    encoding="utf-8",
                )

            safe_destination = destination_root / "research-lr-ra"
            argv = [
                "install_companion_skills.py",
                "--dest",
                str(destination_root),
                "research-lr-ra",
                "zotero-linked-attachments",
            ]
            with mock.patch.object(
                self.installer, "COMPANION_ROOT", companion_root
            ), mock.patch.object(sys, "argv", argv):
                with self.assertRaisesRegex(SystemExit, "overlapping install paths"):
                    self.installer.main()

            self.assertFalse(safe_destination.exists())


if __name__ == "__main__":
    unittest.main()
