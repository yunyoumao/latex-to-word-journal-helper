from __future__ import annotations

import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "dist", "build"}
TEXT_EXTENSIONS = {".md", ".py", ".tex", ".bib", ".svg", ".json", ".txt", ".yml", ".yaml"}
FORBIDDEN_NAMES = {"." + "codex", "." + "claude", "AGENTS" + ".md", "CLAUDE" + ".md"}

EXPECTED_FILES = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "latex_word_helper/scanner.py",
    "latex_word_helper/docx.py",
    "examples/synthetic_paper/main.tex",
    "examples/output/conversion_plan.md",
    "examples/output/conversion_manifest.json",
    "examples/output/journal_handoff.docx",
    "docs/workflow.md",
]

PATTERNS = {
    "local path": re.compile(r"(D:\\OneDrive|C:\\Users\\yunyo|I:\\data)", re.IGNORECASE),
    "old email": re.compile(r"yunyou" + r"maomaomao|lipeize1997" + r"@126\.com", re.IGNORECASE),
    "private company": re.compile(r"Air" + r"Liquide", re.IGNORECASE),
    "phone number": re.compile(r"(?<![\d.-])1[3-9]\d{9}(?![\d.-])"),
    "credential": re.compile(
        r"(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
        r"AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|xox[baprs]-[0-9A-Za-z-]+|"
        r"OPENAI_API_KEY\s*=|api[_-]?key\s*[:=]|access[_-]?token\s*[:=]|"
        r"auth[_-]?token\s*[:=]|secret\s*[:=]|password\s*[:=])",
        re.IGNORECASE,
    ),
    "identity keyword": re.compile(
        r"(" + "户" + "口" + r"|" + "籍" + "贯" + r"|" + "护" + "照" + r"|pass" + r"port)",
        re.IGNORECASE,
    ),
}


def iter_public_files():
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file():
            yield path


def read_text(path: Path) -> str | None:
    if path.suffix.lower() in TEXT_EXTENSIONS or path.name in {".gitignore", ".gitattributes", "LICENSE"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    return None


def validate_docx(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with zipfile.ZipFile(path) as docx:
            names = set(docx.namelist())
            for required in {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}:
                if required not in names:
                    errors.append(f"DOCX missing {required}")
    except zipfile.BadZipFile:
        errors.append(f"Invalid DOCX zip: {path.relative_to(ROOT).as_posix()}")
    return errors


def main() -> int:
    errors: list[str] = []

    for expected in EXPECTED_FILES:
        path = ROOT / expected
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"Missing or empty expected file: {expected}")

    docx_path = ROOT / "examples" / "output" / "journal_handoff.docx"
    if docx_path.exists():
        errors.extend(validate_docx(docx_path))

    for path in iter_public_files():
        rel = path.relative_to(ROOT).as_posix()
        if any(part in FORBIDDEN_NAMES for part in path.relative_to(ROOT).parts):
            errors.append(f"Forbidden public path: {rel}")

        text = read_text(path)
        if text is None:
            continue

        for name in FORBIDDEN_NAMES:
            if name in text and rel != ".gitignore":
                errors.append(f"Forbidden workspace marker {name!r} in {rel}")

        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                errors.append(f"Potential {label} in {rel}")

        emails = re.findall(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
        unexpected = [email for email in emails if not email.lower().endswith(("@example.com", "@example.org", "@example.net"))]
        if unexpected:
            errors.append(f"Unexpected email-like text in {rel}: {unexpected[:3]}")

    if errors:
        print("Public asset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Public asset validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
