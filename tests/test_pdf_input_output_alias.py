import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pdf_probe.py"
ENV_SCRIPT = ROOT / "scripts" / "env_check.py"


def run_probe(pdf, out, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(pdf), "--out", str(out), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def load_probe_module():
    spec = importlib.util.spec_from_file_location("pdf_probe_alias_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_env_check_module():
    spec = importlib.util.spec_from_file_location("env_check_contract_test", ENV_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_text_pdf(path, *, encrypted=False):
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
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): writer._add_object(font)}
            )
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 72 300 Td (Encrypted but extractable) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream)
    if encrypted:
        writer.encrypt(user_password="", owner_password="owner-secret")
    with path.open("wb") as handle:
        writer.write(handle)


class PdfInputOutputAliasTests(unittest.TestCase):
    def test_rejects_direct_report_alias_before_any_output_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe"
            out.mkdir()
            pdf = out / "probe_report.json"
            original = b"not-a-pdf-but-user-owned\n"
            pdf.write_bytes(original)

            result = run_probe(pdf, out, "--no-render")

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("input/output alias", result.stderr)
            self.assertEqual(pdf.read_bytes(), original)
            self.assertFalse((out / "texts").exists())

    def test_rejects_symlink_resolved_text_alias_before_partial_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "source.pdf"
            original = b"user-owned-pdf-placeholder\n"
            pdf.write_bytes(original)
            out = Path(tmp) / "probe"
            text_dir = out / "texts"
            text_dir.mkdir(parents=True)
            (text_dir / "p001.txt").symlink_to(pdf)

            result = run_probe(pdf, out, "--no-render")

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("input/output alias", result.stderr)
            self.assertEqual(pdf.read_bytes(), original)
            self.assertFalse((out / "probe_report.json").exists())

    def test_rejects_hardlink_render_alias_before_partial_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "source.pdf"
            original = b"user-owned-pdf-placeholder\n"
            pdf.write_bytes(original)
            out = Path(tmp) / "probe"
            render_dir = out / "renders"
            render_dir.mkdir(parents=True)
            os.link(pdf, render_dir / "p001_144dpi.jpg")

            result = run_probe(pdf, out)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("input/output alias", result.stderr)
            self.assertEqual(pdf.read_bytes(), original)
            self.assertFalse((out / "probe_report.json").exists())
            self.assertFalse((out / "texts").exists())

    def test_write_point_rechecks_alias_after_preflight(self):
        probe = load_probe_module()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe"
            out.mkdir()
            pdf = out / "probe_report.json"
            original = b"not-a-pdf-but-user-owned\n"
            pdf.write_bytes(original)

            argv = [str(SCRIPT), str(pdf), "--out", str(out), "--no-render"]
            with mock.patch.object(probe, "preflight_outputs", return_value=None):
                with mock.patch.object(
                    probe,
                    "inspect_pdf_encryption",
                    return_value={
                        "encrypted": True,
                        "encryption_check": {"ok": True, "backend": "mock"},
                    },
                ):
                    with mock.patch.object(sys, "argv", argv):
                        with redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit) as raised:
                                probe.main()

            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(pdf.read_bytes(), original)

    def test_missing_pdf_still_exits_two_and_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "missing.pdf"
            out = Path(tmp) / "probe"

            result = run_probe(pdf, out)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            report = json.loads(
                (out / "probe_report.json").read_text(encoding="utf-8")
            )
            self.assertFalse(report["input"]["ok"])
            self.assertEqual(report["input"]["error"], "PDF file does not exist")
            self.assertIsNone(report["input"]["encrypted"])
            self.assertTrue(report["input"]["encryption_check"]["skipped"])

    def test_empty_password_encrypted_text_pdf_is_stopped(self):
        try:
            import pypdf  # noqa: F401
        except ImportError:
            self.skipTest("pypdf is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "encrypted.pdf"
            write_text_pdf(pdf, encrypted=True)
            out = Path(tmp) / "probe"

            result = run_probe(pdf, out, "--no-render")

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(
                (out / "probe_report.json").read_text(encoding="utf-8")
            )
            self.assertTrue(report["input"]["ok"])
            self.assertTrue(report["input"]["encrypted"])
            self.assertEqual(report["input"]["status"], "encrypted")
            self.assertFalse(report["text"]["ok"])
            self.assertFalse((out / "texts").exists())


class EnvironmentEncryptionGateTests(unittest.TestCase):
    def test_strict_core_is_false_with_pdfplumber_but_without_pypdf(self):
        env_check = load_env_check_module()

        def package_status(module_name, display_name):
            return {
                "name": display_name,
                "module": module_name,
                "available": module_name in {"pdfplumber", "fitz"},
            }

        argv = [str(ENV_SCRIPT), "--json", "--strict"]
        stdout = io.StringIO()
        with mock.patch.object(env_check, "package_status", side_effect=package_status):
            with mock.patch.object(
                env_check.shutil,
                "which",
                side_effect=lambda command: (
                    "/mock/bin/pdftoppm" if command == "pdftoppm" else None
                ),
            ):
                with mock.patch.object(env_check.os, "access", return_value=True):
                    with mock.patch.object(sys, "argv", argv):
                        with redirect_stdout(stdout):
                            return_code = env_check.main()

        report = json.loads(stdout.getvalue())
        capabilities = report["capabilities"]
        self.assertTrue(capabilities["pdf_text_ready"])
        self.assertTrue(capabilities["pdf_render_ready"])
        self.assertFalse(capabilities["pdf_encryption_check_ready"])
        self.assertFalse(capabilities["core_ready"])
        self.assertEqual(return_code, 1)


if __name__ == "__main__":
    unittest.main()
