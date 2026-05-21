from __future__ import annotations

import json
from pathlib import Path

from .models import LatexProject


def write_manifest(project: LatexProject, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(project: LatexProject, path: Path) -> None:
    lines = [
        "# LaTeX To Word Handoff Plan",
        "",
        f"Title: {project.title or 'Not detected'}",
        f"Main TeX: `{project.main_tex}`",
        "",
        "## Structure",
        "",
        f"- TeX files scanned: {len(project.files)}",
        f"- Sections: {len(project.sections)}",
        f"- Figures: {len(project.figures)}",
        f"- Tables: {project.tables}",
        f"- Equation environments: {project.equations}",
        f"- Citation keys: {len(project.citations)}",
        "",
        "## Sections",
        "",
    ]
    lines.extend([f"- {section}" for section in project.sections] or ["- No sections detected."])

    lines.extend(["", "## Figures", ""])
    lines.extend([f"- `{figure}`" for figure in project.figures] or ["- No figures detected."])

    lines.extend(["", "## Cross-reference Check", ""])
    if project.missing_references:
        lines.extend([f"- Missing label for reference `{ref}`" for ref in project.missing_references])
    else:
        lines.append("- No missing labels detected.")

    lines.extend(["", "## Figure File Check", ""])
    if project.missing_figures:
        lines.extend([f"- Missing figure file `{figure}`" for figure in project.missing_figures])
    else:
        lines.append("- No missing figure files detected.")

    lines.extend(["", "## Word Handoff Risks", ""])
    lines.extend([f"- {risk}" for risk in project.risks] or ["- No major risks detected."])

    lines.extend(
        [
            "",
            "## Manual Conversion Checklist",
            "",
            "- Confirm journal Word template and reference style.",
            "- Convert title, abstract, section headings, captions, and references.",
            "- Rebuild equation numbering and cross-references in Word.",
            "- Place figures near first mention and verify resolution.",
            "- Recheck bibliography order, punctuation, and DOI display.",
            "- Run final spelling, reference, and layout checks before submission.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
