from __future__ import annotations

import re
from pathlib import Path

from .models import LatexProject


COMMAND_ARG_RE = r"\{([^{}]*)\}"
INPUT_RE = re.compile(r"\\(?:input|include)" + COMMAND_ARG_RE)
TITLE_RE = re.compile(r"\\title" + COMMAND_ARG_RE, re.DOTALL)
SECTION_RE = re.compile(r"\\(?:section|subsection|subsubsection)\*?" + COMMAND_ARG_RE)
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?" + COMMAND_ARG_RE)
CITE_RE = re.compile(r"\\(?:cite|citep|citet|parencite|textcite)(?:\[[^\]]*\]){0,2}" + COMMAND_ARG_RE)
BIB_RE = re.compile(r"\\bibliography" + COMMAND_ARG_RE)
LABEL_RE = re.compile(r"\\label" + COMMAND_ARG_RE)
REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref)" + COMMAND_ARG_RE)
ABSTRACT_RE = re.compile(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", re.DOTALL)
EQUATION_RE = re.compile(r"\\begin\{(?:equation|align|gather|multline)\*?\}|\\\[(.*?)\\\]", re.DOTALL)
TABLE_RE = re.compile(r"\\begin\{table\*?\}")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        current = []
        escaped = False
        for char in line:
            if char == "%" and not escaped:
                break
            current.append(char)
            escaped = char == "\\" and not escaped
        lines.append("".join(current))
    return "\n".join(lines)


def find_main_tex(root: Path) -> Path:
    candidates = sorted(root.glob("*.tex"))
    for candidate in candidates:
        text = candidate.read_text(encoding="utf-8", errors="replace")
        if "\\documentclass" in text:
            return candidate
    if candidates:
        return candidates[0]
    raise FileNotFoundError(f"No .tex files found in {root}")


def resolve_tex_path(root: Path, current: Path, name: str) -> Path:
    raw = Path(name)
    if raw.suffix != ".tex":
        raw = raw.with_suffix(".tex")
    candidate = (current.parent / raw).resolve()
    if candidate.exists():
        return candidate
    return (root / raw).resolve()


def collect_tex_files(root: Path, main_tex: Path) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []

    def visit(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen or not resolved.exists():
            return
        seen.add(resolved)
        ordered.append(resolved)
        text = strip_comments(resolved.read_text(encoding="utf-8", errors="replace"))
        for match in INPUT_RE.finditer(text):
            visit(resolve_tex_path(root, resolved, match.group(1)))

    visit(main_tex)
    return ordered


def flatten_text(paths: list[Path]) -> str:
    return "\n".join(strip_comments(path.read_text(encoding="utf-8", errors="replace")) for path in paths)


def split_csv_args(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        result.extend(part.strip() for part in value.split(",") if part.strip())
    return result


def resolve_figure(root: Path, figure: str) -> bool:
    raw = Path(figure)
    candidates = [root / raw]
    if raw.suffix == "":
        candidates.extend(root / raw.with_suffix(ext) for ext in [".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg"])
    return any(candidate.exists() for candidate in candidates)


def scan_project(root: Path) -> LatexProject:
    root = root.resolve()
    main_tex = find_main_tex(root)
    tex_files = collect_tex_files(root, main_tex)
    text = flatten_text(tex_files)

    title_match = TITLE_RE.search(text)
    abstract_match = ABSTRACT_RE.search(text)
    title = " ".join(title_match.group(1).split()) if title_match else ""
    abstract = " ".join(abstract_match.group(1).split()) if abstract_match else ""
    sections = [" ".join(match.group(1).split()) for match in SECTION_RE.finditer(text)]
    figures = [match.group(1).strip() for match in GRAPHICS_RE.finditer(text)]
    citations = sorted(set(split_csv_args([match.group(1) for match in CITE_RE.finditer(text)])))
    bibliography_files = split_csv_args([match.group(1) for match in BIB_RE.finditer(text)])
    labels = sorted(set(match.group(1).strip() for match in LABEL_RE.finditer(text)))
    references = sorted(set(match.group(1).strip() for match in REF_RE.finditer(text)))
    missing_references = sorted(ref for ref in references if ref not in labels)
    missing_figures = sorted(figure for figure in figures if not resolve_figure(root, figure))

    risks = []
    if figures:
        risks.append("Recheck every figure placement and caption after Word layout.")
    if citations:
        risks.append("Convert bibliography with the journal's required Word/Citation style.")
    if EQUATION_RE.search(text):
        risks.append("Manually verify equations after Word conversion.")
    if missing_references:
        risks.append("Fix unresolved cross-references before sending a Word draft.")
    if missing_figures:
        risks.append("Resolve missing figure files before conversion.")

    return LatexProject(
        root=str(root),
        main_tex=str(main_tex.relative_to(root)),
        files=[str(path.relative_to(root)) for path in tex_files],
        title=title,
        abstract=abstract,
        sections=sections,
        figures=figures,
        tables=len(TABLE_RE.findall(text)),
        equations=len(EQUATION_RE.findall(text)),
        citations=citations,
        bibliography_files=bibliography_files,
        labels=labels,
        references=references,
        missing_references=missing_references,
        missing_figures=missing_figures,
        risks=risks,
    )
