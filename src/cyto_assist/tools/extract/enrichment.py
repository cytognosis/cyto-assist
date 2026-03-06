"""Post-extraction enrichment layer.

Enhances extracted content with:
  - Semantic Scholar API: citation count, venue, TLDR, influential citations
  - scispaCy NER: biomedical entity extraction (genes, diseases, drugs)
  - BibTeX generation and harmonization
  - Cross-validation and confidence scoring

Usage:
    from cytognosis_tools.extract.enrichment import enrich_content
    enriched = enrich_content(content, enable_ner=True, enable_s2=True)
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

from .types import (
    EntityMention,
    ExtractedContent,
    ReferenceEntry,
)

# ── Semantic Scholar API ──────────────────────────────────────────────────

S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,authors,year,venue,citationCount,influentialCitationCount,tldr,externalIds"


def _s2_request(url: str, timeout: int = 10) -> dict | None:
    """Make a request to the Semantic Scholar API."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Cytognosis/1.0 (mailto:mohammadi@cytognosis.org)",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠ S2 API error: {e}", file=sys.stderr)
        return None


def enrich_semantic_scholar(content: ExtractedContent) -> dict[str, Any]:
    """Enrich content with Semantic Scholar metadata.

    Returns a dict with S2-specific data (citation count, TLDR, venue, etc.)
    """
    enrichment: dict[str, Any] = {}

    doi = content.doi
    if not doi:
        return enrichment

    print(f"→ Querying Semantic Scholar for DOI: {doi}", file=sys.stderr)

    # Paper lookup
    url = f"{S2_API_BASE}/paper/DOI:{doi}?fields={S2_FIELDS}"
    data = _s2_request(url)

    if not data:
        return enrichment

    enrichment["s2_paper_id"] = data.get("paperId", "")
    enrichment["citation_count"] = data.get("citationCount", 0)
    enrichment["influential_citation_count"] = data.get("influentialCitationCount", 0)
    enrichment["s2_venue"] = data.get("venue", "")

    # TLDR (AI-generated summary)
    tldr = data.get("tldr")
    if tldr and isinstance(tldr, dict):
        enrichment["tldr"] = tldr.get("text", "")

    # External IDs
    ext_ids = data.get("externalIds", {})
    if ext_ids:
        if ext_ids.get("ArXiv") and not content.arxiv_id:
            content.arxiv_id = ext_ids["ArXiv"]
        if ext_ids.get("PubMed") and not content.pmid:
            content.pmid = ext_ids["PubMed"]
        if ext_ids.get("PubMedCentral") and not content.pmcid:
            content.pmcid = f"PMC{ext_ids['PubMedCentral']}"

    print(
        f"✓ S2: {enrichment.get('citation_count', 0)} citations, "
        f"{enrichment.get('influential_citation_count', 0)} influential",
        file=sys.stderr,
    )

    return enrichment


# ── scispaCy NER ──────────────────────────────────────────────────────────


def _is_scispacy_available() -> bool:
    """Check if scispaCy and a model are available."""
    try:
        import scispacy  # noqa: F401
        import spacy  # noqa: F401

        return True
    except ImportError:
        return False


def extract_entities_scispacy(
    text: str,
    model_name: str = "en_core_sci_sm",
    max_length: int = 100_000,
) -> list[EntityMention]:
    """Extract biomedical entities from text using scispaCy.

    Detects genes, diseases, drugs, chemicals, cell types, etc.

    Args:
        text: Input text
        model_name: spaCy model name (default: en_core_sci_sm)
        max_length: Maximum text length for NER (default: 100K chars)

    Returns:
        List of EntityMention instances
    """
    if not _is_scispacy_available():
        print(
            "⚠ scispaCy not available. Install with: "
            "pip install scispacy && pip install "
            "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz",
            file=sys.stderr,
        )
        return []

    import spacy

    try:
        nlp = spacy.load(model_name)
    except OSError:
        print(
            f"⚠ scispaCy model '{model_name}' not found. Install with: pip install <model-url>",
            file=sys.stderr,
        )
        return []

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    print(f"→ Running scispaCy NER ({model_name})...", file=sys.stderr)

    doc = nlp(text)
    entities = []
    seen = set()  # Deduplicate

    for ent in doc.ents:
        key = (ent.text.lower(), ent.label_)
        if key in seen:
            continue
        seen.add(key)

        entities.append(
            EntityMention(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
            )
        )

    print(f"✓ scispaCy: {len(entities)} unique entities extracted", file=sys.stderr)
    return entities


def enrich_ner(content: ExtractedContent) -> None:
    """Add NER entities to an ExtractedContent instance."""
    # Combine abstract + section text for NER
    text_parts = []
    if content.abstract:
        text_parts.append(content.abstract)
    for section in content.sections:
        if section.text:
            text_parts.append(section.text)

    if not text_parts:
        return

    full_text = "\n\n".join(text_parts)
    entities = extract_entities_scispacy(full_text)

    # Tag entities with their source section
    char_offset = 0
    section_names = ["abstract"] + [s.name for s in content.sections]
    section_lengths = [len(content.abstract)] + [len(s.text) for s in content.sections]

    for entity in entities:
        cumulative = 0
        for sec_name, sec_len in zip(section_names, section_lengths):
            if entity.start < cumulative + sec_len + 2:  # +2 for \n\n
                entity.source_section = sec_name
                break
            cumulative += sec_len + 2

    content.entities = entities


# ── BibTeX Generation ─────────────────────────────────────────────────────


def generate_bibtex(
    references: list[ReferenceEntry],
    output_path: Path,
) -> None:
    """Generate a .bib file from extracted reference entries.

    Args:
        references: List of ReferenceEntry instances
        output_path: Path to write the .bib file
    """
    if not references:
        return

    entries = []
    for i, ref in enumerate(references):
        # Generate a key if missing
        if not ref.bibtex_key:
            first_author = ref.authors[0].split()[-1] if ref.authors else "unknown"
            year = ref.year or "nodate"
            ref.bibtex_key = f"{first_author.lower()}{year}_{i + 1}"

        entries.append(ref.to_bibtex())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    print(
        f"✓ Generated {output_path} ({len(entries)} entries)",
        file=sys.stderr,
    )


# ── Unified Enrichment Pipeline ───────────────────────────────────────────


def enrich_content(
    data: dict[str, Any],
    output_dir: Path | None = None,
    enable_s2: bool = True,
    enable_ner: bool = False,
) -> dict[str, Any]:
    """Enrich extracted content with additional metadata and analysis.

    This operates on the legacy dict format for pipeline compatibility.

    Args:
        data: Legacy dict from extraction pipeline
        output_dir: Directory for output files (BibTeX, etc.)
        enable_s2: Enable Semantic Scholar API enrichment
        enable_ner: Enable scispaCy NER (requires scispacy installed)

    Returns:
        Enriched data dict with additional fields
    """
    # Convert to typed format for enrichment
    content = ExtractedContent.from_legacy_dict(data)

    # ── Semantic Scholar ──
    if enable_s2 and content.doi:
        s2_data = enrich_semantic_scholar(content)
        if s2_data:
            # Store S2 enrichment in a dedicated section
            if "enrichment" not in data:
                data["enrichment"] = {}
            data["enrichment"]["semantic_scholar"] = s2_data

            # Backfill missing identifiers
            if content.pmid and not data.get("identifiers", {}).get("pmid"):
                data.setdefault("identifiers", {})["pmid"] = content.pmid
            if content.arxiv_id and not data.get("identifiers", {}).get("arxiv_id"):
                data.setdefault("identifiers", {})["arxiv_id"] = content.arxiv_id

        # Rate limiting
        time.sleep(0.5)

    # ── scispaCy NER ──
    if enable_ner:
        enrich_ner(content)
        if content.entities:
            entity_summary: dict[str, list[str]] = {}
            for ent in content.entities:
                entity_summary.setdefault(ent.label, []).append(ent.text)
            if "enrichment" not in data:
                data["enrichment"] = {}
            data["enrichment"]["entities"] = {
                label: sorted(set(texts)) for label, texts in entity_summary.items()
            }

    # ── BibTeX generation ──
    if output_dir and content.references:
        generate_bibtex(content.references, output_dir / "references.bib")

    return data
