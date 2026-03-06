"""Shared types for the extraction pipeline.

All extractors produce an `ExtractedContent` instance, ensuring consistent
output structure regardless of input format or backend.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ReferenceEntry:
    """A single bibliographic reference."""

    bibtex_key: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str = ""
    journal: str = ""
    volume: str = ""
    pages: str = ""
    doi: str = ""
    pmid: str = ""
    raw_text: str = ""

    def to_bibtex(self) -> str:
        """Convert to a BibTeX entry string."""
        key = self.bibtex_key or self.doi or "unknown"
        parts = [f"@article{{{key},"]
        if self.title:
            parts.append(f"  title = {{{self.title}}},")
        if self.authors:
            parts.append(f"  author = {{{' and '.join(self.authors)}}},")
        if self.year:
            parts.append(f"  year = {{{self.year}}},")
        if self.journal:
            parts.append(f"  journal = {{{self.journal}}},")
        if self.volume:
            parts.append(f"  volume = {{{self.volume}}},")
        if self.pages:
            parts.append(f"  pages = {{{self.pages}}},")
        if self.doi:
            parts.append(f"  doi = {{{self.doi}}},")
        parts.append("}")
        return "\n".join(parts)


@dataclass
class FigureInfo:
    """An extracted figure/image."""

    id: str = ""
    caption: str = ""
    path: str = ""
    page: int = 0
    label: str = ""  # e.g., "Figure 1", "Fig. 2a"


@dataclass
class TableInfo:
    """An extracted table."""

    id: str = ""
    caption: str = ""
    path: str = ""  # path to exported CSV
    page: int = 0
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)


@dataclass
class SectionBlock:
    """A document section with optional nesting."""

    name: str = ""
    text: str = ""
    level: int = 1  # 1=section, 2=subsection, 3=subsubsection
    subsections: list[SectionBlock] = field(default_factory=list)


@dataclass
class AuthorInfo:
    """Author with optional affiliation and role metadata."""

    name: str = ""
    affiliation: str = ""
    email: str = ""
    orcid: str = ""
    is_corresponding: bool = False
    equal_contribution: bool = False
    role: str = ""  # "first", "senior", "middle"


@dataclass
class EntityMention:
    """A named entity mention extracted via NER."""

    text: str = ""
    label: str = ""  # GENE, DISEASE, CHEMICAL, CELL_TYPE, etc.
    start: int = 0
    end: int = 0
    source_section: str = ""


@dataclass
class CitationInfo:
    """Full citation metadata."""

    title: str = ""
    authors: list[AuthorInfo] = field(default_factory=list)
    authors_str: str = ""  # legacy flat string
    year: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""


@dataclass
class QualityReport:
    """Extraction quality assessment."""

    overall_score: float = 0.0  # 0-1
    field_scores: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)


@dataclass
class ExtractedContent:
    """Top-level container for all extracted content.

    This is the canonical output format for all extractors.
    """

    # ── Identifiers ──
    doi: str = ""
    pmid: str = ""
    pmcid: str = ""
    arxiv_id: str = ""

    # ── Citation ──
    citation: CitationInfo = field(default_factory=CitationInfo)

    # ── Content ──
    abstract: str = ""
    sections: list[SectionBlock] = field(default_factory=list)
    author_contributions: str = ""
    acknowledgments: str = ""
    funding: str = ""
    competing_interests: str = ""
    data_availability: str = ""
    code_availability: str = ""

    # ── Figures & Tables ──
    figures: list[FigureInfo] = field(default_factory=list)
    tables: list[TableInfo] = field(default_factory=list)

    # ── References ──
    references: list[ReferenceEntry] = field(default_factory=list)
    reference_count: int = 0

    # ── Associated Materials ──
    code_repositories: list[dict[str, str]] = field(default_factory=list)
    data_repositories: list[dict[str, str]] = field(default_factory=list)
    supplementary_files: list[str] = field(default_factory=list)

    # ── NER Entities (from scispaCy) ──
    entities: list[EntityMention] = field(default_factory=list)

    # ── Quality ──
    quality: QualityReport = field(default_factory=QualityReport)

    # ── Metadata ──
    source_path: str = ""
    source_format: str = ""
    extraction_backend: str = ""  # "pymupdf", "grobid", "docling", etc.

    # ── Legacy compatibility ──

    def to_legacy_dict(self) -> dict[str, Any]:
        """Convert to the legacy dict format used by paper.py v1."""
        result: dict[str, Any] = {
            "identifiers": {},
            "citation": {},
            "content": {},
            "figures": {},
            "references": {},
            "associated": {},
        }

        # Identifiers
        if self.doi:
            result["identifiers"]["doi"] = self.doi
        if self.pmid:
            result["identifiers"]["pmid"] = self.pmid
        if self.pmcid:
            result["identifiers"]["pmcid"] = self.pmcid
        if self.arxiv_id:
            result["identifiers"]["arxiv_id"] = self.arxiv_id

        # Citation
        if self.citation.title:
            result["citation"]["title"] = self.citation.title
        if self.citation.authors_str:
            result["citation"]["authors"] = self.citation.authors_str
        elif self.citation.authors:
            result["citation"]["authors"] = ", ".join(a.name for a in self.citation.authors)
        if self.citation.year:
            result["citation"]["year"] = self.citation.year
        if self.citation.journal:
            result["citation"]["journal"] = self.citation.journal
        if self.citation.volume:
            result["citation"]["volume"] = self.citation.volume
        if self.citation.pages:
            result["citation"]["pages"] = self.citation.pages
        if self.citation.publisher:
            result["citation"]["publisher"] = self.citation.publisher

        # Content
        if self.abstract:
            result["content"]["abstract"] = self.abstract
        if self.sections:
            result["content"]["sections"] = json.dumps(
                [{"name": s.name, "text": s.text} for s in self.sections], indent=2
            )
        if self.author_contributions:
            result["content"]["author_contributions"] = self.author_contributions
        if self.acknowledgments:
            result["content"]["acknowledgments"] = self.acknowledgments
        if self.funding:
            result["content"]["funding"] = self.funding
        if self.competing_interests:
            result["content"]["competing_interests"] = self.competing_interests

        # Figures
        if self.figures:
            result["figures"]["figure_list"] = json.dumps(
                [asdict(f) for f in self.figures], indent=2
            )
        if self.tables:
            result["figures"]["table_list"] = json.dumps(
                [{"id": t.id, "caption": t.caption, "path": t.path} for t in self.tables],
                indent=2,
            )

        # References
        if self.reference_count:
            result["references"]["reference_count"] = self.reference_count

        # Associated
        if self.code_repositories:
            result["associated"]["code_repositories"] = json.dumps(self.code_repositories, indent=2)
        if self.data_repositories:
            result["associated"]["data_repositories"] = json.dumps(self.data_repositories, indent=2)

        return result

    @classmethod
    def from_legacy_dict(cls, data: dict[str, Any]) -> ExtractedContent:
        """Create from the legacy dict format (for backward compatibility)."""
        content = cls()

        # Identifiers
        ids = data.get("identifiers", {})
        content.doi = ids.get("doi", "")
        content.pmid = ids.get("pmid", "")
        content.pmcid = ids.get("pmcid", "")
        content.arxiv_id = ids.get("arxiv_id", "")

        # Citation
        cit = data.get("citation", {})
        content.citation = CitationInfo(
            title=cit.get("title", ""),
            authors_str=cit.get("authors", ""),
            year=cit.get("year", ""),
            journal=cit.get("journal", ""),
            volume=cit.get("volume", ""),
            pages=cit.get("pages", ""),
            publisher=cit.get("publisher", ""),
        )

        # Content
        cont = data.get("content", {})
        content.abstract = cont.get("abstract", "")
        content.author_contributions = cont.get("author_contributions", "")
        content.acknowledgments = cont.get("acknowledgments", "")
        content.funding = cont.get("funding", "")
        content.competing_interests = cont.get("competing_interests", "")

        # Sections (stored as JSON string in legacy)
        sections_json = cont.get("sections", "")
        if sections_json:
            try:
                raw_sections = json.loads(sections_json)
                content.sections = [
                    SectionBlock(name=s.get("name", ""), text=s.get("text", ""))
                    for s in raw_sections
                ]
            except (json.JSONDecodeError, TypeError):
                pass

        # References
        refs = data.get("references", {})
        content.reference_count = refs.get("reference_count", 0)

        return content

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a clean dict (for YAML/JSON export)."""
        return asdict(self)
