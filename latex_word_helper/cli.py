from __future__ import annotations

import argparse
from pathlib import Path

from .docx import write_docx
from .report import write_manifest, write_markdown
from .scanner import scan_project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Word handoff package from a LaTeX paper project.")
    parser.add_argument("project", type=Path, help="Path to a LaTeX project directory.")
    parser.add_argument("--out", type=Path, default=Path("latex-word-handoff"), help="Output directory.")
    args = parser.parse_args(argv)

    project = scan_project(args.project)
    args.out.mkdir(parents=True, exist_ok=True)
    write_markdown(project, args.out / "conversion_plan.md")
    write_manifest(project, args.out / "conversion_manifest.json")
    write_docx(project, args.out / "journal_handoff.docx")
    print(f"Wrote {args.out / 'conversion_plan.md'}")
    print(f"Wrote {args.out / 'conversion_manifest.json'}")
    print(f"Wrote {args.out / 'journal_handoff.docx'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
