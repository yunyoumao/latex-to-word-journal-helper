from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class LatexProject:
    root: str
    main_tex: str
    files: list[str]
    title: str
    abstract: str
    sections: list[str]
    figures: list[str]
    tables: int
    equations: int
    citations: list[str]
    bibliography_files: list[str]
    labels: list[str]
    references: list[str]
    missing_references: list[str]
    missing_figures: list[str]
    risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
