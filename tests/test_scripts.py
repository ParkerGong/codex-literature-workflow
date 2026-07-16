import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


def run(*args, cwd=ROOT):
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def write_text_pdf(path):
    from pypdf import PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=400)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    resources = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): writer._add_object(font)}
            )
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 72 300 Td (Codex PDF probe text) Tj ET")
    page[NameObject("/Resources")] = resources
    page[NameObject("/Contents")] = writer._add_object(stream)
    with path.open("wb") as handle:
        writer.write(handle)


class MetadataTests(unittest.TestCase):
    def test_skill_frontmatter_and_interface_metadata(self):
        skills = (
            (ROOT, "codex-literature-workflow"),
            (ROOT / "companion-skills" / "research-lr-ra", "research-lr-ra"),
            (
                ROOT / "companion-skills" / "zotero-linked-attachments",
                "zotero-linked-attachments",
            ),
        )
        for skill, expected_name in skills:
            with self.subTest(skill=expected_name):
                content = (skill / "SKILL.md").read_text(encoding="utf-8")
                match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
                self.assertIsNotNone(match)
                frontmatter = match.group(1)
                keys = {
                    line.split(":", 1)[0].strip()
                    for line in frontmatter.splitlines()
                    if line and not line.startswith(" ")
                }
                self.assertEqual(keys, {"name", "description"})
                self.assertIn(f"name: {expected_name}", frontmatter)

                metadata = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
                self.assertTrue(metadata.startswith("interface:\n"))
                self.assertIn(f"${expected_name}", metadata)
                short = re.search(r'short_description: "([^"]+)"', metadata)
                self.assertIsNotNone(short)
                self.assertGreaterEqual(len(short.group(1)), 25)
                self.assertLessEqual(len(short.group(1)), 64)

    def test_environment_file_is_portable_from_another_working_directory(self):
        environment = (ROOT / "environment.yml").read_text(encoding="utf-8")
        self.assertNotIn("- -r requirements.txt", environment)
        for package in ("pypdf", "pdfplumber", "pymupdf", "requests", "selenium"):
            self.assertIn(f"- {package}", environment)


class WorkspaceTests(unittest.TestCase):
    def test_init_is_idempotent_and_force_backs_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            script = ROOT / "scripts" / "init_workspace.py"
            dry_run = run(sys.executable, script, "--root", root, "--dry-run")
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertIn("planned:", dry_run.stdout)
            self.assertFalse(root.exists())
            first = run(sys.executable, script, "--root", root)
            self.assertEqual(first.returncode, 0, first.stderr)
            profile = root / "00_controller" / "project_profile.md"
            initial_profile = profile.read_text(encoding="utf-8")
            self.assertIn("long_task_goal: not-needed", initial_profile)
            self.assertIn("latest_git_checkpoint: disabled", initial_profile)
            ledger = (root / "00_controller" / "git_checkpoints.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("| disabled | enable only by user or host profile |", ledger)
            profile.write_text("user-owned\n", encoding="utf-8")

            second = run(sys.executable, script, "--root", root)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(profile.read_text(encoding="utf-8"), "user-owned\n")

            forced = run(sys.executable, script, "--root", root, "--force")
            self.assertEqual(forced.returncode, 0, forced.stderr)
            backups = list(
                (root / ".codex-literature-backups").glob(
                    "*/00_controller/project_profile.md"
                )
            )
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "user-owned\n")
            self.assertIn("project_profile: generic", profile.read_text(encoding="utf-8"))

    def test_init_rejects_broken_symlink_backup_ignore(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            script = ROOT / "scripts" / "init_workspace.py"
            first = run(sys.executable, script, "--root", root)
            self.assertEqual(first.returncode, 0, first.stderr)
            profile = root / "00_controller" / "project_profile.md"
            profile.write_text("user-owned\n", encoding="utf-8")

            backup_dir = root / ".codex-literature-backups"
            backup_dir.mkdir()
            escaped = Path(tmp) / "escaped.txt"
            (backup_dir / ".gitignore").symlink_to(escaped)
            forced = run(sys.executable, script, "--root", root, "--force")
            self.assertNotEqual(forced.returncode, 0)
            self.assertIn("symlink backup ignore", forced.stderr)
            self.assertFalse(escaped.exists())
            self.assertEqual(profile.read_text(encoding="utf-8"), "user-owned\n")

    def test_init_rejects_hard_linked_existing_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            script = ROOT / "scripts" / "init_workspace.py"
            first = run(sys.executable, script, "--root", root)
            self.assertEqual(first.returncode, 0, first.stderr)
            profile = root / "00_controller" / "project_profile.md"
            victim = Path(tmp) / "victim.md"
            profile.replace(victim)
            os.link(victim, profile)
            before = victim.read_text(encoding="utf-8")
            forced = run(sys.executable, script, "--root", root, "--force")
            self.assertNotEqual(forced.returncode, 0)
            self.assertIn("hard-linked file", forced.stderr)
            self.assertEqual(victim.read_text(encoding="utf-8"), before)

    def test_companion_installer_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = ROOT / "scripts" / "install_companion_skills.py"
            result = run(
                sys.executable,
                script,
                "--dest",
                Path(tmp) / "skills",
                "../research-lr-ra",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(tmp) / "research-lr-ra").exists())

    def test_companion_installer_dry_run_and_force_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = ROOT / "scripts" / "install_companion_skills.py"
            dest = Path(tmp) / "skills"
            dry_run = run(
                sys.executable,
                script,
                "--dest",
                dest,
                "--dry-run",
                "research-lr-ra",
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertFalse(dest.exists())

            first = run(
                sys.executable,
                script,
                "--dest",
                dest,
                "research-lr-ra",
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            installed = dest / "research-lr-ra"
            marker = installed / "user-marker.txt"
            marker.write_text("preserve me\n", encoding="utf-8")

            forced = run(
                sys.executable,
                script,
                "--dest",
                dest,
                "--force",
                "research-lr-ra",
            )
            self.assertEqual(forced.returncode, 0, forced.stderr)
            backups = list(
                (Path(tmp) / ".codex-literature-skill-backups").glob(
                    "*/research-lr-ra/user-marker.txt"
                )
            )
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "preserve me\n")

    def test_main_skill_installer_packages_only_runtime_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills" / "codex-literature-workflow"
            script = ROOT / "scripts" / "install_skill.py"
            dry_run = run(sys.executable, script, "--dest", dest, "--dry-run")
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertFalse(dest.exists())
            result = run(sys.executable, script, "--dest", dest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertTrue((dest / "references" / "architecture.md").is_file())
            self.assertEqual((dest / "VERSION").read_text(encoding="utf-8").strip(), "1.0.0")
            self.assertFalse((dest / "README.md").exists())
            self.assertFalse((dest / ".git").exists())

            marker = dest / "user-marker.txt"
            marker.write_text("preserve me\n", encoding="utf-8")
            forced = run(sys.executable, script, "--dest", dest, "--force")
            self.assertEqual(forced.returncode, 0, forced.stderr)
            backups = list(
                (dest.parent / ".codex-literature-skill-backups").glob(
                    "*/codex-literature-workflow/user-marker.txt"
                )
            )
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "preserve me\n")


class PdfTests(unittest.TestCase):
    def test_missing_pdf_exits_two_with_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe"
            result = run(
                sys.executable,
                ROOT / "scripts" / "pdf_probe.py",
                Path(tmp) / "missing.pdf",
                "--out",
                out,
            )
            self.assertEqual(result.returncode, 2)
            report = json.loads((out / "probe_report.json").read_text(encoding="utf-8"))
            self.assertFalse(report["input"]["ok"])

    def test_small_pdf_text_and_render_probe(self):
        try:
            import pypdf  # noqa: F401
        except ImportError:
            self.skipTest("pypdf is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "sample.pdf"
            write_text_pdf(pdf)
            out = Path(tmp) / "probe"
            result = run(
                sys.executable,
                ROOT / "scripts" / "pdf_probe.py",
                pdf,
                "--pages",
                "1",
                "--out",
                out,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((out / "probe_report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["text"]["ok"])
            self.assertTrue(report["text"]["text_layer_present"])
            self.assertTrue(report["render"]["ok"])

    def test_blank_pdf_is_not_reported_as_text_ready(self):
        try:
            from pypdf import PdfWriter
        except ImportError:
            self.skipTest("pypdf is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "blank.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=300, height=400)
            with pdf.open("wb") as handle:
                writer.write(handle)
            out = Path(tmp) / "probe"
            result = run(
                sys.executable,
                ROOT / "scripts" / "pdf_probe.py",
                pdf,
                "--out",
                out,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads((out / "probe_report.json").read_text(encoding="utf-8"))
            self.assertFalse(report["text"]["ok"])
            self.assertFalse(report["text"]["text_layer_present"])
            self.assertEqual(report["text"]["chars_total"], 0)
            self.assertTrue(report["render"]["ok"])

    def test_probe_rejects_symlink_report_without_overwrite(self):
        try:
            import pypdf  # noqa: F401
        except ImportError:
            self.skipTest("pypdf is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "sample.pdf"
            write_text_pdf(pdf)
            out = Path(tmp) / "probe"
            out.mkdir()
            victim = Path(tmp) / "victim.json"
            victim.write_text("user-owned\n", encoding="utf-8")
            (out / "probe_report.json").symlink_to(victim)
            result = run(
                sys.executable,
                ROOT / "scripts" / "pdf_probe.py",
                pdf,
                "--out",
                out,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("symlink output file", result.stderr)
            self.assertEqual(victim.read_text(encoding="utf-8"), "user-owned\n")

    def test_probe_rejects_hard_linked_report_without_overwrite(self):
        try:
            import pypdf  # noqa: F401
        except ImportError:
            self.skipTest("pypdf is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "sample.pdf"
            write_text_pdf(pdf)
            out = Path(tmp) / "probe"
            out.mkdir()
            victim = Path(tmp) / "victim.json"
            victim.write_text("user-owned\n", encoding="utf-8")
            os.link(victim, out / "probe_report.json")
            result = run(
                sys.executable,
                ROOT / "scripts" / "pdf_probe.py",
                pdf,
                "--out",
                out,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("hard-linked output file", result.stderr)
            self.assertEqual(victim.read_text(encoding="utf-8"), "user-owned\n")


@unittest.skipUnless(NODE, "Node.js is not installed")
class ZoteroScriptTests(unittest.TestCase):
    def test_builder_rejects_input_output_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "note.md"
            source.write_text("note\n", encoding="utf-8")
            mapping = Path(tmp) / "mapping.json"
            mapping.write_text(
                json.dumps([{"parentKey": "ABCDEFGH", "path": str(source)}]),
                encoding="utf-8",
            )
            result = run(
                NODE,
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "build_zotero_linked_attachment_js.mjs",
                mapping,
                mapping,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("must differ", result.stderr)

            hardlink = Path(tmp) / "mapping-hardlink.json"
            os.link(mapping, hardlink)
            before = mapping.read_text(encoding="utf-8")
            hardlink_result = run(
                NODE,
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "build_zotero_linked_attachment_js.mjs",
                mapping,
                hardlink,
            )
            self.assertEqual(hardlink_result.returncode, 2)
            self.assertRegex(hardlink_result.stderr, r"must differ|hard-linked output")
            self.assertEqual(mapping.read_text(encoding="utf-8"), before)

            victim = Path(tmp) / "victim.js"
            victim.write_text("user-owned\n", encoding="utf-8")
            symlink_output = Path(tmp) / "generated-symlink.js"
            symlink_output.symlink_to(victim)
            symlink_result = run(
                NODE,
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "build_zotero_linked_attachment_js.mjs",
                mapping,
                symlink_output,
            )
            self.assertEqual(symlink_result.returncode, 2)
            self.assertIn("symlink output", symlink_result.stderr)
            self.assertEqual(victim.read_text(encoding="utf-8"), "user-owned\n")

            hardlink_victim = Path(tmp) / "hardlink-victim.js"
            hardlink_victim.write_text("user-owned-hardlink\n", encoding="utf-8")
            hardlink_output = Path(tmp) / "generated-hardlink.js"
            os.link(hardlink_victim, hardlink_output)
            hardlink_output_result = run(
                NODE,
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "build_zotero_linked_attachment_js.mjs",
                mapping,
                hardlink_output,
            )
            self.assertEqual(hardlink_output_result.returncode, 2)
            self.assertIn("hard-linked output", hardlink_output_result.stderr)
            self.assertEqual(
                hardlink_victim.read_text(encoding="utf-8"), "user-owned-hardlink\n"
            )

            escaped = Path(tmp) / "escaped.js"
            broken_output = Path(tmp) / "generated-broken-symlink.js"
            broken_output.symlink_to(escaped)
            broken_result = run(
                NODE,
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "build_zotero_linked_attachment_js.mjs",
                mapping,
                broken_output,
            )
            self.assertEqual(broken_result.returncode, 2)
            self.assertIn("symlink output", broken_result.stderr)
            self.assertFalse(escaped.exists())

    def test_verifier_rejects_conflicting_content_types_before_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "note.md"
            source.write_text("note\n", encoding="utf-8")
            mapping = Path(tmp) / "mapping.json"
            mapping.write_text(
                json.dumps(
                    [
                        {
                            "parentKey": "ABCDEFGH",
                            "path": str(source),
                            "contentType": "text/markdown",
                        },
                        {
                            "parentKey": "ABCDEFGH",
                            "path": str(source),
                            "contentType": "text/plain",
                        },
                    ]
                ),
                encoding="utf-8",
            )
            result = run(
                NODE,
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "verify_zotero_linked_attachments.mjs",
                mapping,
                "--api",
                "http://127.0.0.1:1/api/users/0",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Conflicting duplicate mapping", result.stderr)

    def test_verifier_paginates_without_total_results_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "note.md"
            source.write_text("note\n", encoding="utf-8")
            mapping = Path(tmp) / "mapping.json"
            mapping.write_text(
                json.dumps(
                    [
                        {
                            "parentKey": "ABCDEFGH",
                            "path": str(source),
                            "contentType": "text/markdown",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            verifier = (
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "verify_zotero_linked_attachments.mjs"
            )
            harness = Path(tmp) / "pagination.mjs"
            harness.write_text(
                "\n".join(
                    [
                        'import { pathToFileURL } from "node:url";',
                        f"const sourceURL = {json.dumps(source.resolve().as_uri())};",
                        f"const verifier = {json.dumps(str(verifier))};",
                        f"const mapping = {json.dumps(str(mapping))};",
                        "globalThis.fetch = async (url) => {",
                        "  const parsed = new URL(String(url));",
                        '  if (parsed.pathname.endsWith("/items/ABCDEFGH/children")) {',
                        '    const start = Number(parsed.searchParams.get("start") || "0");',
                        "    const filler = Array.from({ length: 100 }, (_, i) => ({",
                        "      key: `IGN${i}` , data: { itemType: \"note\", parentItem: \"ABCDEFGH\" },",
                        "    }));",
                        "    const target = [{ key: \"ATTACH01\", data: {",
                        '      itemType: "attachment", parentItem: "ABCDEFGH",',
                        '      linkMode: "linked_file", contentType: "text/markdown",',
                        '      path: "attachments:note.md"',
                        "    }}];",
                        "    return new Response(JSON.stringify(start === 0 ? filler : target), {",
                        '      status: 200, headers: { "Content-Type": "application/json" }',
                        "    });",
                        "  }",
                        '  if (parsed.pathname.endsWith("/items/ATTACH01/file/view/url")) {',
                        "    return new Response(sourceURL, { status: 200 });",
                        "  }",
                        '  return new Response("not found", { status: 404, statusText: "Not Found" });',
                        "};",
                        'process.argv = [process.execPath, verifier, mapping, "--api", "http://mock/api/users/0"];',
                        "await import(pathToFileURL(verifier).href);",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            result = run(NODE, harness)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])

    def test_verifier_stops_when_endpoint_repeats_full_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "note.md"
            source.write_text("note\n", encoding="utf-8")
            mapping = Path(tmp) / "mapping.json"
            mapping.write_text(
                json.dumps(
                    [
                        {
                            "parentKey": "ABCDEFGH",
                            "path": str(source),
                            "contentType": "text/markdown",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            verifier = (
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "verify_zotero_linked_attachments.mjs"
            )
            harness = Path(tmp) / "repeated-page.mjs"
            harness.write_text(
                "\n".join(
                    [
                        'import { pathToFileURL } from "node:url";',
                        f"const verifier = {json.dumps(str(verifier))};",
                        f"const mapping = {json.dumps(str(mapping))};",
                        "let childrenRequests = 0;",
                        "const repeatedPage = Array.from({ length: 100 }, (_, i) => ({",
                        "  key: `IGN${i}`, data: { itemType: \"note\", parentItem: \"ABCDEFGH\" },",
                        "}));",
                        "globalThis.fetch = async (url) => {",
                        "  const parsed = new URL(String(url));",
                        '  if (parsed.pathname.endsWith("/items/ABCDEFGH/children")) {',
                        "    childrenRequests += 1;",
                        "    if (childrenRequests > 3) throw new Error(\"test guard: verifier did not stop\");",
                        "    return new Response(JSON.stringify(repeatedPage), {",
                        '      status: 200, headers: { "Content-Type": "application/json" }',
                        "    });",
                        "  }",
                        '  return new Response("not found", { status: 404, statusText: "Not Found" });',
                        "};",
                        'process.argv = [process.execPath, verifier, mapping, "--api", "http://mock/api/users/0"];',
                        "await import(pathToFileURL(verifier).href);",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            result = run(NODE, harness)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["failures"][0]["reason"], "api-or-verification-error")
            self.assertIn("pagination made no progress", payload["failures"][0]["error"])
            self.assertNotIn("test guard", payload["failures"][0]["error"])

    def test_verifier_resolves_relative_attachment_and_checks_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "note.md"
            source.write_text("note\n", encoding="utf-8")
            mapping = Path(tmp) / "mapping.json"
            mapping.write_text(
                json.dumps(
                    [
                        {
                            "parentKey": "ABCDEFGH",
                            "path": str(source),
                            "contentType": "text/markdown",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            verifier = (
                ROOT
                / "companion-skills"
                / "zotero-linked-attachments"
                / "scripts"
                / "verify_zotero_linked_attachments.mjs"
            )

            def mocked_run(parent_item):
                harness = Path(tmp) / f"verify-{parent_item}.mjs"
                harness.write_text(
                    "\n".join(
                        [
                            'import { pathToFileURL } from "node:url";',
                            f"const sourceURL = {json.dumps(source.resolve().as_uri())};",
                            f"const verifier = {json.dumps(str(verifier))};",
                            f"const mapping = {json.dumps(str(mapping))};",
                            "globalThis.fetch = async (url) => {",
                            "  const value = String(url);",
                            '  if (value.includes("/items/ABCDEFGH/children")) {',
                            "    return new Response(JSON.stringify([{",
                            '      key: "ATTACH01",',
                            "      data: {",
                            '        itemType: "attachment",',
                            f"        parentItem: {json.dumps(parent_item)},",
                            '        linkMode: "linked_file",',
                            '        contentType: "text/markdown",',
                            '        path: "attachments:note.md",',
                            "      },",
                            "    }]), { status: 200, headers: {",
                            '      "Content-Type": "application/json",',
                            '      "Total-Results": "1",',
                            "    }});",
                            "  }",
                            '  if (value.includes("/items/ATTACH01/file/view/url")) {',
                            '    return new Response(sourceURL, { status: 200, headers: { "Content-Type": "text/plain" }});',
                            "  }",
                            '  return new Response("not found", { status: 404, statusText: "Not Found" });',
                            "};",
                            'process.argv = [process.execPath, verifier, mapping, "--api", "http://mock/api/users/0"];',
                            "await import(pathToFileURL(verifier).href);",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )
                return run(NODE, harness)

            valid = mocked_run("ABCDEFGH")
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertTrue(json.loads(valid.stdout)["ok"])

            invalid = mocked_run("WRONGPAR")
            self.assertEqual(invalid.returncode, 1)
            self.assertFalse(json.loads(invalid.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
