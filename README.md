# LaTeX To Word Journal Helper

A dependency-free Python helper for preparing a LaTeX paper project for journal workflows that require Microsoft Word deliverables.

It does not pretend to perfectly convert LaTeX into Word. Instead, it scans a LaTeX project and generates a practical handoff package: structure summary, figures/tables/equations/citations inventory, risk checklist, JSON manifest, and a lightweight `.docx` checklist.

## What It Generates

- `conversion_plan.md`: human-readable Word handoff checklist.
- `conversion_manifest.json`: machine-readable project inventory.
- `journal_handoff.docx`: simple Word checklist for coauthors or editors.

## Quick Start

```powershell
python -m latex_word_helper examples\synthetic_paper --out examples\output
```

Run tests and validation:

```powershell
python -m unittest discover -s tests
python scripts\validate_public_assets.py
```

## Checks Included

- Main `.tex` discovery.
- `\input{}` and `\include{}` traversal.
- Title, abstract, section, figure, table, equation, citation, and bibliography inventory.
- Label/reference cross-check.
- Figure file existence check.
- Word handoff risks: math conversion, figure placement, cross-references, bibliography handling, and style cleanup.

## Public-Safe Boundary

The example paper is synthetic. It does not represent a real manuscript, thesis chapter, journal submission, advisor draft, unpublished result, or private bibliography.

Do not publish real LaTeX projects unless the manuscript, figures, bibliography, and collaborators are already explicitly public.

## Suggested GitHub Topics

```text
latex
word
docx
academic-writing
journal
research-tools
python
manuscript
publishing
automation
```
