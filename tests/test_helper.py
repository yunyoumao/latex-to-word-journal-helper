from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from latex_word_helper.docx import write_docx
from latex_word_helper.report import write_manifest, write_markdown
from latex_word_helper.scanner import scan_project


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "synthetic_paper"


class LatexWordHelperTests(unittest.TestCase):
    def test_scan_project(self) -> None:
        project = scan_project(SAMPLE)
        self.assertEqual(project.main_tex, "main.tex")
        self.assertEqual(project.title, "Synthetic Journal Conversion Example")
        self.assertEqual(len(project.sections), 3)
        self.assertEqual(project.equations, 1)
        self.assertEqual(project.tables, 1)
        self.assertIn("sec:missing", project.missing_references)
        self.assertEqual(project.missing_figures, [])

    def test_outputs(self) -> None:
        project = scan_project(SAMPLE)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_markdown(project, out / "plan.md")
            write_manifest(project, out / "manifest.json")
            write_docx(project, out / "handoff.docx")
            self.assertIn("Manual Conversion Checklist", (out / "plan.md").read_text(encoding="utf-8"))
            with zipfile.ZipFile(out / "handoff.docx") as docx:
                self.assertIn("word/document.xml", docx.namelist())


if __name__ == "__main__":
    unittest.main()
