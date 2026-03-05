"""HTML content extraction from publisher websites and local HTML files.

Supports static HTML extraction via BeautifulSoup4 + trafilatura,
with publisher-specific selectors for Nature, Science, Cell, bioRxiv,
PubMed, arXiv, and other scholarly sources.

Usage:
    from cytognosis_tools.extract.html import extract_html
    content = extract_html("https://www.nature.com/articles/s41586-024-07159-1", output_dir)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .types import (
    AuthorInfo,
    ExtractedContent,
    FigureInfo,
    SectionBlock,
)

# ── Optional imports ──────────────────────────────────────────────────────


def _try_import(module_name: str):
    try:
        return __import__(module_name)
    except ImportError:
        return None


bs4 = _try_import("bs4")
requests_mod = _try_import("requests")
trafilatura_mod = _try_import("trafilatura")


# ── Publisher Detection ───────────────────────────────────────────────────

PUBLISHER_PATTERNS: dict[str, list[str]] = {
    "nature": ["nature.com"],
    "science": ["science.org", "sciencemag.org"],
    "cell": ["cell.com", "sciencedirect.com"],
    "biorxiv": ["biorxiv.org"],
    "medrxiv": ["medrxiv.org"],
    "pubmed": ["pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov/pubmed"],
    "arxiv": ["arxiv.org"],
    "plos": ["plos.org", "journals.plos.org"],
    "pmc": ["ncbi.nlm.nih.gov/pmc"],
    "wiley": ["onlinelibrary.wiley.com"],
    "springer": ["link.springer.com", "springerlink.com"],
    "frontiers": ["frontiersin.org"],
    "mdpi": ["mdpi.com"],
    "elife": ["elifesciences.org"],
}


def detect_publisher(url: str) -> str:
    """Detect publisher from URL."""
    domain = urlparse(url).netloc.lower()
    for publisher, patterns in PUBLISHER_PATTERNS.items():
        for pattern in patterns:
            if pattern in domain:
                return publisher
    return "unknown"


# ── Meta Tag Extraction ───────────────────────────────────────────────────


def _extract_meta_tags(soup) -> dict[str, str | list[str]]:
    """Extract scholarly metadata from HTML <meta> tags.

    Most publishers use standard citation_* or DC.* meta tags:
    - citation_title, citation_author, citation_doi, citation_date
    - DC.title, DC.creator, DC.identifier, DC.date
    """
    meta: dict[str, str | list[str]] = {}

    # Single-value tags
    single_tags = {
        "title": [
            "citation_title",
            "DC.title",
            "og:title",
            "twitter:title",
        ],
        "doi": [
            "citation_doi",
            "DC.identifier",
            "prism.doi",
        ],
        "journal": [
            "citation_journal_title",
            "citation_journal_abbrev",
            "DC.source",
            "prism.publicationName",
        ],
        "date": [
            "citation_date",
            "citation_publication_date",
            "citation_online_date",
            "DC.date",
            "prism.publicationDate",
        ],
        "volume": ["citation_volume", "prism.volume"],
        "issue": ["citation_issue", "prism.number"],
        "firstpage": ["citation_firstpage", "prism.startingPage"],
        "lastpage": ["citation_lastpage", "prism.endingPage"],
        "publisher": ["citation_publisher", "DC.publisher"],
        "issn": ["citation_issn", "prism.issn"],
        "pmid": ["citation_pmid"],
        "arxiv_id": ["citation_arxiv_id"],
        "abstract": ["DC.description", "og:description"],
        "language": ["citation_language", "DC.language"],
    }

    for field_name, tag_names in single_tags.items():
        for tag_name in tag_names:
            tag = soup.find("meta", attrs={"name": tag_name})
            if not tag:
                tag = soup.find("meta", attrs={"property": tag_name})
            if tag and tag.get("content"):
                meta[field_name] = tag["content"].strip()
                break

    # Multi-value tags (authors)
    authors = []
    for tag in soup.find_all("meta", attrs={"name": "citation_author"}):
        if tag.get("content"):
            authors.append(tag["content"].strip())
    if not authors:
        for tag in soup.find_all("meta", attrs={"name": "DC.creator"}):
            if tag.get("content"):
                authors.append(tag["content"].strip())
    if authors:
        meta["authors"] = authors

    # Author affiliations (sometimes paired with citation_author_institution)
    affiliations = []
    for tag in soup.find_all("meta", attrs={"name": "citation_author_institution"}):
        if tag.get("content"):
            affiliations.append(tag["content"].strip())
    if affiliations:
        meta["affiliations"] = affiliations

    # PDF URL
    pdf_tag = soup.find("meta", attrs={"name": "citation_pdf_url"})
    if pdf_tag and pdf_tag.get("content"):
        meta["pdf_url"] = pdf_tag["content"].strip()

    return meta


# ── Publisher-Specific Extractors ─────────────────────────────────────────


def _extract_nature(soup, content: ExtractedContent) -> None:
    """Extract content from Nature family journals."""
    # Abstract
    abstract_div = soup.find("div", id="Abs1-content") or soup.find(
        "section", attrs={"data-title": "Abstract"}
    )
    if abstract_div:
        content.abstract = abstract_div.get_text(separator="\n", strip=True)

    # Sections (article body)
    body = soup.find("div", class_="c-article-body") or soup.find("article")
    if body:
        for section in body.find_all("section", recursive=False):
            heading = section.find(["h2", "h3"])
            if heading:
                name = heading.get_text(strip=True)
                # Skip references section
                if name.lower() in ("references", "bibliography"):
                    continue
                text = section.get_text(separator="\n", strip=True)
                # Remove the heading text from the body
                text = text.replace(name, "", 1).strip()
                content.sections.append(SectionBlock(name=name, text=text))

    # Figures
    for fig in soup.find_all("figure"):
        fig_id = fig.get("id", "")
        img = fig.find("img")
        caption_el = fig.find("figcaption")
        content.figures.append(
            FigureInfo(
                id=fig_id,
                caption=caption_el.get_text(strip=True) if caption_el else "",
                path=img.get("src", "") if img else "",
                label=fig_id,
            )
        )


def _extract_biorxiv(soup, content: ExtractedContent) -> None:
    """Extract content from bioRxiv/medRxiv."""
    # Abstract
    abstract_div = soup.find("div", class_="abstract")
    if abstract_div:
        # Remove the "Abstract" heading
        heading = abstract_div.find(["h2", "h3"])
        if heading:
            heading.decompose()
        content.abstract = abstract_div.get_text(separator="\n", strip=True)

    # Full text sections
    body = soup.find("div", class_="article") or soup.find("div", id="article-content")
    if body:
        for section in body.find_all("div", class_="section"):
            heading = section.find(["h2", "h3"])
            if heading:
                name = heading.get_text(strip=True)
                if name.lower() in ("references", "bibliography", "abstract"):
                    continue
                text = section.get_text(separator="\n", strip=True)
                text = text.replace(name, "", 1).strip()
                content.sections.append(SectionBlock(name=name, text=text))


def _extract_pmc(soup, content: ExtractedContent) -> None:
    """Extract content from PubMed Central full-text articles."""
    # Abstract
    abstract_div = soup.find("div", class_="tsec") or soup.find("div", id="abstract")
    if abstract_div:
        content.abstract = abstract_div.get_text(separator="\n", strip=True)

    # Sections
    body = soup.find("div", class_="jig-ncbiinpagenav")
    if body:
        for sec in body.find_all("div", class_="tsec"):
            heading = sec.find(["h2", "h3"])
            if heading:
                name = heading.get_text(strip=True)
                if name.lower() in ("references", "abstract"):
                    continue
                text = sec.get_text(separator="\n", strip=True)
                text = text.replace(name, "", 1).strip()
                content.sections.append(SectionBlock(name=name, text=text))


def _extract_pubmed(soup, content: ExtractedContent) -> None:
    """Extract content from PubMed abstract pages."""
    # Abstract
    abstract_div = soup.find("div", class_="abstract-content")
    if abstract_div:
        content.abstract = abstract_div.get_text(separator="\n", strip=True)


def _extract_arxiv(soup, content: ExtractedContent) -> None:
    """Extract content from arXiv abstract pages."""
    # Abstract
    abstract_block = soup.find("blockquote", class_="abstract")
    if abstract_block:
        # Remove "Abstract:" prefix
        abstract_text = abstract_block.get_text(separator="\n", strip=True)
        abstract_text = re.sub(r"^Abstract:\s*", "", abstract_text, flags=re.IGNORECASE)
        content.abstract = abstract_text


def _extract_generic(soup, content: ExtractedContent) -> None:
    """Generic HTML extraction using trafilatura for unknown publishers."""
    if trafilatura_mod is None:
        # Fallback: extract main content area
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
            or soup.find("body")
        )
        if main:
            # Extract sections from headings
            for heading in main.find_all(["h2", "h3"]):
                name = heading.get_text(strip=True)
                # Collect text until next heading
                text_parts = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ("h2", "h3"):
                        break
                    text_parts.append(sibling.get_text(separator="\n", strip=True))
                if text_parts:
                    content.sections.append(SectionBlock(name=name, text="\n".join(text_parts)))


# ── Main HTML Extractor ───────────────────────────────────────────────────


def extract_html(path: str, output_dir: Path) -> dict[str, Any]:
    """Extract content from an HTML file or URL.

    Args:
        path: URL (http/https) or local file path to an HTML file
        output_dir: Directory for exported artifacts (figures, tables)

    Returns:
        Legacy dict format (for compatibility with paper.py pipeline)
    """
    if bs4 is None:
        print(
            "ERROR: BeautifulSoup4 not installed. Install with: pip install beautifulsoup4",
            file=sys.stderr,
        )
        sys.exit(1)

    from bs4 import BeautifulSoup

    # ── Fetch content ──
    if path.startswith("http://") or path.startswith("https://"):
        if requests_mod is None:
            print(
                "ERROR: requests not installed. Install with: pip install requests",
                file=sys.stderr,
            )
            sys.exit(1)
        import requests

        resp = requests.get(
            path,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; CytognosisBot/1.0; +https://cytognosis.org)"
                ),
                "Accept": "text/html,application/xhtml+xml",
            },
            timeout=30,
        )
        resp.raise_for_status()
        html_text = resp.text
        publisher = detect_publisher(path)
    else:
        html_text = Path(path).read_text(encoding="utf-8", errors="replace")
        publisher = "unknown"

    soup = BeautifulSoup(html_text, "html.parser")

    # ── Build ExtractedContent ──
    content = ExtractedContent(
        source_path=path,
        source_format="html",
        extraction_backend=f"bs4+{publisher}",
    )

    # ── Meta tag extraction (works for all publishers) ──
    meta = _extract_meta_tags(soup)

    if meta.get("title"):
        content.citation.title = str(meta["title"])
    if meta.get("doi"):
        doi_str = str(meta["doi"])
        # Clean DOI (sometimes includes full URL)
        doi_match = re.search(r"(10\.\d{4,}/[^\s]+)", doi_str)
        if doi_match:
            content.doi = doi_match.group(1).rstrip(".")
        else:
            content.doi = doi_str
    if meta.get("pmid"):
        content.pmid = str(meta["pmid"])
    if meta.get("journal"):
        content.citation.journal = str(meta["journal"])
    if meta.get("date"):
        year_match = re.search(r"((?:19|20)\d{2})", str(meta["date"]))
        if year_match:
            content.citation.year = year_match.group(1)
    if meta.get("volume"):
        content.citation.volume = str(meta["volume"])
    if meta.get("publisher"):
        content.citation.publisher = str(meta["publisher"])
    if meta.get("abstract") and not content.abstract:
        content.abstract = str(meta["abstract"])

    # Authors from meta tags
    if isinstance(meta.get("authors"), list):
        affiliations_list = (
            meta["affiliations"] if isinstance(meta.get("affiliations"), list) else []
        )
        for i, author_name in enumerate(meta["authors"]):
            aff = affiliations_list[i] if i < len(affiliations_list) else ""
            content.citation.authors.append(AuthorInfo(name=author_name, affiliation=aff))

    # Pages from firstpage/lastpage
    fp = meta.get("firstpage", "")
    lp = meta.get("lastpage", "")
    if fp:
        content.citation.pages = f"{fp}-{lp}" if lp else str(fp)

    # ── Publisher-specific extraction ──
    publisher_extractors = {
        "nature": _extract_nature,
        "biorxiv": _extract_biorxiv,
        "medrxiv": _extract_biorxiv,  # same format
        "pmc": _extract_pmc,
        "pubmed": _extract_pubmed,
        "arxiv": _extract_arxiv,
    }

    extractor = publisher_extractors.get(publisher, _extract_generic)
    extractor(soup, content)

    # ── Trafilatura fallback for body text ──
    if not content.sections and not content.abstract and trafilatura_mod is not None:
        import trafilatura

        extracted = trafilatura.extract(
            html_text,
            include_comments=False,
            include_tables=True,
        )
        if extracted:
            content.sections.append(SectionBlock(name="Main Content", text=extracted))

    # ── Fallback: title from <title> tag ──
    if not content.citation.title:
        title_tag = soup.find("title")
        if title_tag:
            content.citation.title = title_tag.get_text(strip=True)

    # ── Return as legacy dict for pipeline compatibility ──
    return content.to_legacy_dict()
