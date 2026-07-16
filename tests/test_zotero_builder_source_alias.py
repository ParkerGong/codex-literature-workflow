import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
BUILDER = (
    ROOT
    / "companion-skills"
    / "zotero-linked-attachments"
    / "scripts"
    / "build_zotero_linked_attachment_js.mjs"
)


def run_builder(mapping, output):
    return subprocess.run(
        [NODE, str(BUILDER), str(mapping), str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


@unittest.skipUnless(NODE, "Node.js is not installed")
class ZoteroBuilderSourceAliasTests(unittest.TestCase):
    def write_mapping(self, path, source):
        path.write_text(
            json.dumps([{"parentKey": "ABCDEFGH", "path": str(source)}]),
            encoding="utf-8",
        )

    def test_rejects_direct_attachment_source_output_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "generated.js"
            output.write_text("user-owned attachment source\n", encoding="utf-8")
            mapping = root / "mapping.json"
            self.write_mapping(mapping, output)

            result = run_builder(mapping, output)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Attachment source and generated-script output paths must differ", result.stderr)
            self.assertEqual(
                output.read_text(encoding="utf-8"), "user-owned attachment source\n"
            )

    def test_rejects_symlinked_attachment_source_output_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "generated.js"
            output.write_text("user-owned symlink target\n", encoding="utf-8")
            source = root / "source-link.md"
            source.symlink_to(output)
            mapping = root / "mapping.json"
            self.write_mapping(mapping, source)

            result = run_builder(mapping, output)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Attachment source and generated-script output paths must differ", result.stderr)
            self.assertTrue(source.is_symlink())
            self.assertEqual(output.read_text(encoding="utf-8"), "user-owned symlink target\n")

    def test_rejects_hard_linked_attachment_source_output_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.md"
            source.write_text("user-owned hardlink source\n", encoding="utf-8")
            output = root / "generated.js"
            os.link(source, output)
            mapping = root / "mapping.json"
            self.write_mapping(mapping, source)

            result = run_builder(mapping, output)

            self.assertEqual(result.returncode, 2)
            self.assertIn("hard-linked output", result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), "user-owned hardlink source\n")
            self.assertEqual(output.read_text(encoding="utf-8"), "user-owned hardlink source\n")


if __name__ == "__main__":
    unittest.main()
