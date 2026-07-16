import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "setup_env.py"
SPEC = importlib.util.spec_from_file_location("setup_env_under_test", SCRIPT)
SETUP_ENV = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SETUP_ENV)


def run_setup(target, *extra):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--venv", str(target), "--json", *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def make_minimal_wheel(path: Path) -> None:
    dist_info = "codex_setup_probe-0.0.0.dist-info"
    records = [
        "codex_setup_probe/__init__.py",
        f"{dist_info}/METADATA",
        f"{dist_info}/WHEEL",
        f"{dist_info}/RECORD",
    ]
    with zipfile.ZipFile(path, "w") as wheel:
        wheel.writestr("codex_setup_probe/__init__.py", "VALUE = 'installed'\n")
        wheel.writestr(
            f"{dist_info}/METADATA",
            "Metadata-Version: 2.1\nName: codex-setup-probe\nVersion: 0.0.0\n",
        )
        wheel.writestr(
            f"{dist_info}/WHEEL",
            "Wheel-Version: 1.0\n"
            "Generator: codex-setup-env-safety-test\n"
            "Root-Is-Purelib: true\n"
            "Tag: py3-none-any\n",
        )
        wheel.writestr(
            f"{dist_info}/RECORD",
            "".join(f"{record},,\n" for record in records),
        )


class SetupEnvSafetyTests(unittest.TestCase):
    def setUp(self):
        safe_temp_root = Path(tempfile.gettempdir()).resolve()
        self.temp = tempfile.TemporaryDirectory(dir=safe_temp_root)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_rejects_existing_directory_and_preserves_sentinel(self):
        target = self.root / "existing-venv"
        target.mkdir()
        sentinel = target / "sentinel.txt"
        sentinel.write_text("do not overwrite\n", encoding="utf-8")

        result = run_setup(target)

        self.assertEqual(result.returncode, 2)
        self.assertIn("must not already exist", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not overwrite\n")

    def test_rejects_hard_link_target_without_mutating_source(self):
        source = self.root / "source.txt"
        source.write_text("hard-link sentinel\n", encoding="utf-8")
        target = self.root / "venv-hard-link"
        os.link(source, target)

        result = run_setup(target)

        self.assertEqual(result.returncode, 2)
        self.assertIn("must not already exist", result.stderr)
        self.assertEqual(source.read_text(encoding="utf-8"), "hard-link sentinel\n")
        self.assertEqual(os.stat(source).st_ino, os.stat(target).st_ino)

    def test_rejects_final_symlink(self):
        source = self.root / "source"
        source.mkdir()
        target = self.root / "venv-link"
        target.symlink_to(source, target_is_directory=True)

        result = run_setup(target)

        self.assertEqual(result.returncode, 2)
        self.assertIn("final or ancestor symlink", result.stderr)
        self.assertFalse((source / "pyvenv.cfg").exists())

    def test_rejects_ancestor_symlink(self):
        real_parent = self.root / "real-parent"
        real_parent.mkdir()
        linked_parent = self.root / "linked-parent"
        linked_parent.symlink_to(real_parent, target_is_directory=True)
        target = linked_parent / "venv"

        result = run_setup(target)

        self.assertEqual(result.returncode, 2)
        self.assertIn("final or ancestor symlink", result.stderr)
        self.assertFalse((real_parent / "venv").exists())

    def test_rejects_all_skill_source_overlap_relations(self):
        targets = {
            "equal": ROOT,
            "ancestor": ROOT.parent,
            "descendant": ROOT / ".setup-env-overlap-must-not-be-created",
        }
        for relation, target in targets.items():
            with self.subTest(relation=relation):
                with self.assertRaisesRegex(
                    SETUP_ENV.TargetSafetyError, "skill source"
                ):
                    SETUP_ENV.validate_new_target(target)

        self.assertFalse(targets["descendant"].exists())

    def test_new_target_can_create_and_install_in_one_call(self):
        target = self.root / "fresh-venv"
        wheel = self.root / "codex_setup_probe-0.0.0-py3-none-any.whl"
        make_minimal_wheel(wheel)

        result = run_setup(target, "--install", "--packages", str(wheel))

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIsNone(report["safety_error"])
        self.assertTrue(report["python_available"])
        self.assertTrue(report["pip_available"])
        self.assertEqual(report["installed"], [str(wheel)])
        self.assertTrue((target / "pyvenv.cfg").is_file())

        imported = subprocess.run(
            [report["python"], "-c", "import codex_setup_probe; print(codex_setup_probe.VALUE)"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertEqual(imported.stdout.strip(), "installed")


if __name__ == "__main__":
    unittest.main()
