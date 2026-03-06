"""Batch extraction and quality scoring.

Provides parallel batch processing of multiple documents and
extraction quality assessment.

Usage:
    batch_extract(".sandbox/data/papers/", ".sandbox/results/batch/")
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# ── Batch Extraction ──────────────────────────────────────────────────────


def _extract_single(
    input_path: str,
    output_dir: str,
    resolve_ids: bool = True,
    enrich: bool = False,
) -> dict[str, Any]:
    """Extract a single document (for parallel execution)."""
    from .html import extract_html
    from .paper import detect_format, export_content_yml, extract_docx, extract_latex, extract_markdown, extract_pdf
    from .paper import resolve_ids as do_resolve

    fmt = detect_format(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    extractors = {
        "pdf": extract_pdf,
        "docx": extract_docx,
        "latex": extract_latex,
        "markdown": extract_markdown,
        "html": extract_html,
    }

    if fmt not in extractors:
        return {"path": input_path, "status": "error", "error": f"Unsupported format: {fmt}"}

    try:
        data = extractors[fmt](input_path, out)
        data["_source"] = input_path

        if resolve_ids:
            do_resolve(data)

        if enrich:
            from .enrichment import enrich_content

            data = enrich_content(data, out, enable_s2=True)

        export_content_yml(data, out / "content.yml")

        return {
            "path": input_path,
            "status": "success",
            "format": fmt,
            "doi": data.get("identifiers", {}).get("doi", ""),
            "title": data.get("citation", {}).get("title", "")[:80],
        }
    except Exception as e:
        return {"path": input_path, "status": "error", "error": str(e)[:200]}


def batch_extract(
    input_dir: str,
    output_dir: str,
    resolve_ids: bool = True,
    enrich: bool = False,
    max_workers: int = 4,
    extensions: tuple[str, ...] = (".pdf", ".docx", ".tex", ".md", ".html"),
) -> dict[str, Any]:
    """Extract content from all documents in a directory.

    Args:
        input_dir: Directory containing input documents
        output_dir: Root output directory (subdirs created per file)
        resolve_ids: Resolve DOI/PMID via APIs
        enrich: Enrich with Semantic Scholar
        max_workers: Number of parallel workers
        extensions: File extensions to process

    Returns:
        Summary dict with results and statistics
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Find all matching files
    files = []
    for ext in extensions:
        files.extend(input_path.glob(f"*{ext}"))

    if not files:
        print(f"⚠ No matching files found in {input_dir}", file=sys.stderr)
        return {"total": 0, "success": 0, "failed": 0, "results": []}

    print(f"→ Batch extracting {len(files)} files (workers: {max_workers})", file=sys.stderr)

    results = []
    start_time = time.time()

    # Use sequential processing to avoid subprocess issues
    for f in files:
        fname = f.stem
        out = str(output_path / fname)
        result = _extract_single(str(f), out, resolve_ids, enrich)
        results.append(result)
        status = "✓" if result["status"] == "success" else "✗"
        print(f"  {status} {f.name}", file=sys.stderr)

    elapsed = time.time() - start_time
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "error")

    summary = {
        "total": len(files),
        "success": success,
        "failed": failed,
        "elapsed_seconds": round(elapsed, 1),
        "results": results,
    }

    # Write summary report
    report_path = output_path / "batch_report.yml"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        yaml.dump(summary, f, default_flow_style=False, width=120)

    print(
        f"\n✓ Batch complete: {success}/{len(files)} succeeded, {failed} failed, {elapsed:.1f}s",
        file=sys.stderr,
    )

    return summary


# ── Quality Scoring ───────────────────────────────────────────────────────


def score_extraction(content_yml_path: str) -> dict[str, Any]:
    """Score the quality of an extraction result.

    Checks for completeness and consistency of extracted fields.

    Args:
        content_yml_path: Path to a content.yml file

    Returns:
        Quality report dict
    """
    with open(content_yml_path) as f:
        data = yaml.safe_load(f) or {}

    scores: dict[str, float] = {}
    warnings: list[str] = []
    missing: list[str] = []

    # ── Required fields ──
    ids = data.get("identifiers", {})
    citation = data.get("citation", {})
    content = data.get("content", {})

    # DOI (critical)
    if ids.get("doi"):
        scores["doi"] = 1.0
    else:
        scores["doi"] = 0.0
        missing.append("doi")

    # Title
    title = citation.get("title", "")
    if title and len(title) > 10:
        scores["title"] = 1.0
    elif title:
        scores["title"] = 0.5
        warnings.append(f"Short title: {title[:30]}")
    else:
        scores["title"] = 0.0
        missing.append("title")

    # Authors
    authors = citation.get("authors", "")
    if authors and len(authors) > 5:
        scores["authors"] = 1.0
    elif authors:
        scores["authors"] = 0.5
    else:
        scores["authors"] = 0.0
        missing.append("authors")

    # Abstract
    abstract = content.get("abstract", "")
    if abstract and len(abstract) > 100:
        scores["abstract"] = 1.0
    elif abstract:
        scores["abstract"] = 0.5
        warnings.append("Short abstract")
    else:
        scores["abstract"] = 0.0
        missing.append("abstract")

    # Sections
    sections_json = content.get("sections", "")
    if sections_json:
        try:
            sections = json.loads(sections_json)
            if len(sections) >= 3:
                scores["sections"] = 1.0
            elif len(sections) >= 1:
                scores["sections"] = 0.5
                warnings.append(f"Only {len(sections)} sections")
            else:
                scores["sections"] = 0.0
                missing.append("sections")
        except (json.JSONDecodeError, TypeError):
            scores["sections"] = 0.3
            warnings.append("Sections not valid JSON")
    else:
        scores["sections"] = 0.0
        missing.append("sections")

    # Year
    if citation.get("year"):
        scores["year"] = 1.0
    else:
        scores["year"] = 0.0
        missing.append("year")

    # Journal
    if citation.get("journal"):
        scores["journal"] = 1.0
    else:
        scores["journal"] = 0.0
        missing.append("journal")

    # References
    refs = data.get("references", {})
    ref_count = refs.get("reference_count", 0)
    if ref_count > 5:
        scores["references"] = 1.0
    elif ref_count > 0:
        scores["references"] = 0.5
    else:
        scores["references"] = 0.0
        missing.append("references")

    # ── Overall score ──
    weights = {
        "doi": 3.0,
        "title": 3.0,
        "authors": 2.0,
        "abstract": 3.0,
        "sections": 2.0,
        "year": 1.0,
        "journal": 1.0,
        "references": 1.0,
    }

    weighted_sum = sum(scores.get(k, 0) * w for k, w in weights.items())
    total_weight = sum(weights.values())
    overall = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "overall_score": round(overall, 3),
        "field_scores": scores,
        "warnings": warnings,
        "missing_fields": missing,
        "grade": (
            "A"
            if overall >= 0.9
            else "B"
            if overall >= 0.75
            else "C"
            if overall >= 0.5
            else "D"
            if overall >= 0.25
            else "F"
        ),
    }
