from __future__ import annotations

import html
import zipfile
from pathlib import Path

from .models import LatexProject


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

APP = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
  xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>latex-to-word-journal-helper</Application>
</Properties>
"""

CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:dcmitype="http://purl.org/dc/dcmitype/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>LaTeX To Word Handoff Checklist</dc:title>
  <dc:creator>latex-to-word-journal-helper</dc:creator>
</cp:coreProperties>
"""


def paragraph(text: str, style: str = "") -> str:
    style_xml = f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>" if style else ""
    return f"<w:p>{style_xml}<w:r><w:t>{html.escape(text)}</w:t></w:r></w:p>"


def document_xml(project: LatexProject) -> str:
    lines = [
        paragraph("LaTeX To Word Handoff Checklist", "Title"),
        paragraph(f"Title: {project.title or 'Not detected'}"),
        paragraph(f"Main TeX: {project.main_tex}"),
        paragraph("Inventory", "Heading1"),
        paragraph(f"TeX files: {len(project.files)}"),
        paragraph(f"Sections: {len(project.sections)}"),
        paragraph(f"Figures: {len(project.figures)}"),
        paragraph(f"Tables: {project.tables}"),
        paragraph(f"Equation environments: {project.equations}"),
        paragraph(f"Citation keys: {len(project.citations)}"),
        paragraph("Risks", "Heading1"),
    ]
    lines.extend(paragraph(f"- {risk}") for risk in (project.risks or ["No major risks detected."]))
    lines.extend(
        [
            paragraph("Manual Checks", "Heading1"),
            paragraph("- Confirm journal Word template and reference style."),
            paragraph("- Rebuild equation numbering and cross-references in Word."),
            paragraph("- Place figures near first mention and verify resolution."),
            paragraph("- Recheck bibliography order, punctuation, and DOI display."),
        ]
    )
    body = "".join(lines)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
  </w:body>
</w:document>
"""


def write_docx(project: LatexProject, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", CONTENT_TYPES)
        docx.writestr("_rels/.rels", RELS)
        docx.writestr("docProps/app.xml", APP)
        docx.writestr("docProps/core.xml", CORE)
        docx.writestr("word/document.xml", document_xml(project))
