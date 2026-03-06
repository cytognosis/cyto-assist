"""GROBID integration for scholarly PDF extraction.

GROBID (GeneRation Of BIbliographic Data) is the gold-standard ML-based tool
for extracting structured content from scientific PDFs. This module provides
a REST client that sends PDFs to a GROBID server and parses the TEI XML
response into our ExtractedContent format.

Requirements:
    GROBID server running (Docker recommended):
        docker run --rm -p 8070:8070 lfoppiano/grobid:0.8.2

Usage:
    from cytognosis_tools.extract.grobid import extract_pdf_grobid, is_grobid_available
    if is_grobid_available():
        content = extract_pdf_grobid("paper.pdf", output_dir)
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .types import (
    AuthorInfo,
    ExtractedContent,
    FigureInfo,
    ReferenceEntry,
    SectionBlock,
    TableInfo,
)

# ── GROBID Configuration ─────────────────────────────────────────────────

DEFAULT_GROBID_URL = "http://localhost:8070"

# TEI XML namespaces
TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def _tei_find(element, path: str):
    """Find element with TEI namespace."""
    return element.find(path, TEI_NS)


def _tei_findall(element, path: str):
    """Find all elements with TEI namespace."""
    return element.findall(path, TEI_NS)


def _tei_text(element, path: str, default: str = "") -> str:
    """Get text content of a TEI element."""
    el = _tei_find(element, path)
    if el is not None:
        return "".join(el.itertext()).strip()
    return default


def _get_all_text(element) -> str:
    """Get all text content from an element and its children."""
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


# ── GROBID Server Communication ──────────────────────────────────────────


def is_grobid_available(grobid_url: str = DEFAULT_GROBID_URL) -> bool:
    """Check if GROBID server is reachable."""
    try:
        import urllib.request

        req = urllib.request.Request(
            f"{grobid_url}/api/isalive",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def _call_grobid(
    pdf_path: str,
    endpoint: str = "/api/processFulltextDocument",
    grobid_url: str = DEFAULT_GROBID_URL,
    **params: str,
) -> str:
    """Send a PDF to GROBID and return the TEI XML response."""
    import urllib.request

    # Build multipart form data manually
    boundary = "----CytognosisGROBIDBoundary"
    body_parts = []

    # Add the PDF file
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    body_parts.append(f"--{boundary}".encode())
    body_parts.append(b'Content-Disposition: form-data; name="input"; filename="input.pdf"')
    body_parts.append(b"Content-Type: application/pdf")
    body_parts.append(b"")
    body_parts.append(pdf_data)

    # Add additional parameters
    for key, value in params.items():
        body_parts.append(f"--{boundary}".encode())
        body_parts.append(f'Content-Disposition: form-data; name="{key}"'.encode())
        body_parts.append(b"")
        body_parts.append(value.encode())

    body_parts.append(f"--{boundary}--".encode())
    body_parts.append(b"")

    body = b"\r\n".join(body_parts)

    req = urllib.request.Request(
        f"{grobid_url}{endpoint}",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/xml",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8")


# ── TEI XML Parsing ──────────────────────────────────────────────────────


def _parse_authors(header) -> list[AuthorInfo]:
    """Parse author information from TEI header."""
    authors = []
    for author_el in _tei_findall(
        header,
        ".//tei:sourceDesc/tei:biblStruct/tei:analytic/tei:author",
    ):
        persname = _tei_find(author_el, "tei:persName")
        if persname is None:
            continue

        forename_parts = []
        for fn in _tei_findall(persname, "tei:forename"):
            if fn.text:
                forename_parts.append(fn.text.strip())

        surname = _tei_text(persname, "tei:surname")
        name = f"{' '.join(forename_parts)} {surname}".strip()

        # Affiliation
        aff_el = _tei_find(author_el, "tei:affiliation")
        affiliation = ""
        if aff_el is not None:
            org_name = _tei_text(aff_el, "tei:orgName")
            affiliation = org_name

        # Email
        email = _tei_text(author_el, "tei:email")

        # Corresponding author (role attribute)
        role = author_el.get("role", "")
        is_corresponding = role == "corresp"

        authors.append(
            AuthorInfo(
                name=name,
                affiliation=affiliation,
                email=email,
                is_corresponding=is_corresponding,
            )
        )

    return authors


def _parse_abstract(header) -> str:
    """Parse abstract from TEI header."""
    abstract_el = _tei_find(
        header,
        ".//tei:profileDesc/tei:abstract",
    )
    if abstract_el is None:
        return ""

    # Collect all paragraph text
    paragraphs = []
    for p in _tei_findall(abstract_el, ".//tei:p"):
        text = _get_all_text(p)
        if text:
            paragraphs.append(text)

    if paragraphs:
        return "\n\n".join(paragraphs)

    # Fallback: get all text
    return _get_all_text(abstract_el)


def _parse_sections(body) -> list[SectionBlock]:
    """Parse document sections from TEI body."""
    if body is None:
        return []

    sections = []
    for div in _tei_findall(body, "tei:div"):
        head = _tei_find(div, "tei:head")
        if head is None:
            continue

        name = _get_all_text(head)
        # Remove number prefix (e.g., "1 Introduction" → "Introduction")
        name = re.sub(r"^\d+\.?\s*", "", name).strip()

        # Determine level from head's @n attribute
        n_attr = head.get("n", "")
        level = n_attr.count(".") + 1 if n_attr else 1

        # Collect paragraph text
        paragraphs = []
        for p in _tei_findall(div, "tei:p"):
            text = _get_all_text(p)
            if text:
                paragraphs.append(text)

        text = "\n\n".join(paragraphs)

        if name and text:
            sections.append(SectionBlock(name=name, text=text, level=level))

    return sections


def _parse_references(back) -> list[ReferenceEntry]:
    """Parse bibliographic references from TEI back matter."""
    if back is None:
        return []

    refs = []
    for bibl in _tei_findall(back, ".//tei:listBibl/tei:biblStruct"):
        ref = ReferenceEntry()

        # ID
        ref.bibtex_key = bibl.get("{http://www.w3.org/XML/1998/namespace}id", "")

        # Title
        analytic = _tei_find(bibl, "tei:analytic")
        if analytic is not None:
            ref.title = _tei_text(analytic, "tei:title")

            # Authors
            for author_el in _tei_findall(analytic, "tei:author"):
                persname = _tei_find(author_el, "tei:persName")
                if persname is not None:
                    forename = _tei_text(persname, "tei:forename")
                    surname = _tei_text(persname, "tei:surname")
                    ref.authors.append(f"{forename} {surname}".strip())

        # Monograph-level info (journal, year, volume, pages)
        monogr = _tei_find(bibl, "tei:monogr")
        if monogr is not None:
            ref.journal = _tei_text(monogr, "tei:title")

            imprint = _tei_find(monogr, "tei:imprint")
            if imprint is not None:
                date = _tei_find(imprint, "tei:date")
                if date is not None:
                    ref.year = date.get("when", "")[:4]

                vol = _tei_find(imprint, 'tei:biblScope[@unit="volume"]')
                if vol is not None and vol.text:
                    ref.volume = vol.text

                pages = _tei_find(imprint, 'tei:biblScope[@unit="page"]')
                if pages is not None:
                    ref.pages = f"{pages.get('from', '')}-{pages.get('to', '')}".strip("-")

        # DOI
        for idno in _tei_findall(bibl, ".//tei:idno"):
            if idno.get("type") == "DOI" and idno.text:
                ref.doi = idno.text.strip()

        if ref.title or ref.authors:
            refs.append(ref)

    return refs


def _parse_figures(body) -> list[FigureInfo]:
    """Parse figure information from TEI body."""
    if body is None:
        return []

    figures = []
    for fig in _tei_findall(body, ".//tei:figure"):
        fig_type = fig.get("type", "")
        if fig_type == "table":
            continue  # Skip tables, handled separately

        fig_id = fig.get("{http://www.w3.org/XML/1998/namespace}id", "")
        head = _tei_text(fig, "tei:head")
        label = _tei_text(fig, "tei:label")
        desc = _tei_text(fig, "tei:figDesc")

        caption = desc or head
        if label and caption:
            caption = f"{label}: {caption}"

        figures.append(
            FigureInfo(
                id=fig_id,
                caption=caption,
                label=label or head,
            )
        )

    return figures


def _parse_tables(body) -> list[TableInfo]:
    """Parse table information from TEI body."""
    if body is None:
        return []

    tables = []
    for fig in _tei_findall(body, ".//tei:figure"):
        if fig.get("type") != "table":
            continue

        fig_id = fig.get("{http://www.w3.org/XML/1998/namespace}id", "")
        head = _tei_text(fig, "tei:head")
        label = _tei_text(fig, "tei:label")
        desc = _tei_text(fig, "tei:figDesc")

        caption = desc or head
        if label and caption:
            caption = f"{label}: {caption}"

        tables.append(
            TableInfo(
                id=fig_id,
                caption=caption,
            )
        )

    return tables


# ── Main GROBID Extractor ────────────────────────────────────────────────


def extract_pdf_grobid(
    path: str,
    output_dir: Path,
    grobid_url: str = DEFAULT_GROBID_URL,
) -> dict[str, Any]:
    """Extract content from a PDF using GROBID.

    Args:
        path: Path to PDF file
        output_dir: Directory for exported artifacts
        grobid_url: GROBID server URL (default: http://localhost:8070)

    Returns:
        Legacy dict format (for compatibility with paper.py pipeline)
    """
    print(f"→ Sending to GROBID: {path}", file=sys.stderr)

    # Call GROBID
    tei_xml = _call_grobid(
        path,
        grobid_url=grobid_url,
        consolidateHeader="1",
        consolidateCitations="1",
        includeRawCitations="1",
        teiCoordinates="persName,figure,ref,biblStruct,formula",
    )

    # Parse TEI XML
    root = ET.fromstring(tei_xml)

    # Save raw TEI for debugging
    tei_path = output_dir / "grobid_output.tei.xml"
    tei_path.parent.mkdir(parents=True, exist_ok=True)
    tei_path.write_text(tei_xml, encoding="utf-8")

    content = ExtractedContent(
        source_path=path,
        source_format="pdf",
        extraction_backend="grobid",
    )

    # ── Header (metadata) ──
    header = _tei_find(root, ".//tei:teiHeader")
    if header is not None:
        # Title
        content.citation.title = _tei_text(
            header,
            ".//tei:titleStmt/tei:title",
        )

        # Authors
        content.citation.authors = _parse_authors(header)

        # Journal
        content.citation.journal = _tei_text(
            header,
            ".//tei:sourceDesc/tei:biblStruct/tei:monogr/tei:title",
        )

        # Date
        date_el = _tei_find(
            header,
            ".//tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date",
        )
        if date_el is not None:
            when = date_el.get("when", "")
            content.citation.year = when[:4] if when else ""

        # DOI
        for idno in _tei_findall(header, ".//tei:idno"):
            id_type = idno.get("type", "").lower()
            if id_type == "doi" and idno.text:
                content.doi = idno.text.strip()

        # Publisher
        content.citation.publisher = _tei_text(
            header,
            ".//tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:publisher",
        )

        # Abstract
        content.abstract = _parse_abstract(header)

    # ── Body (sections) ──
    body = _tei_find(root, ".//tei:text/tei:body")
    content.sections = _parse_sections(body)
    content.figures = _parse_figures(body)
    content.tables = _parse_tables(body)

    # ── Back matter (references) ──
    back = _tei_find(root, ".//tei:text/tei:back")
    content.references = _parse_references(back)
    content.reference_count = len(content.references)

    # ── Generate BibTeX file ──
    if content.references:
        bib_path = output_dir / "references.bib"
        bib_path.parent.mkdir(parents=True, exist_ok=True)
        bib_entries = [ref.to_bibtex() for ref in content.references]
        bib_path.write_text("\n\n".join(bib_entries) + "\n", encoding="utf-8")
        print(
            f"✓ Generated references.bib ({len(content.references)} entries)",
            file=sys.stderr,
        )

    # ── Detect special sections ──
    for section in content.sections:
        name_lower = section.name.lower()
        if "author contribution" in name_lower:
            content.author_contributions = section.text
        elif "acknowledgment" in name_lower or "acknowledgement" in name_lower:
            content.acknowledgments = section.text
        elif "funding" in name_lower:
            content.funding = section.text
        elif "competing interest" in name_lower or "conflict" in name_lower:
            content.competing_interests = section.text
        elif "data availability" in name_lower:
            content.data_availability = section.text
        elif "code availability" in name_lower:
            content.code_availability = section.text

    print(
        f"✓ GROBID extracted: {len(content.sections)} sections, "
        f"{len(content.references)} refs, "
        f"{len(content.figures)} figures, "
        f"{len(content.tables)} tables",
        file=sys.stderr,
    )

    return content.to_legacy_dict()
