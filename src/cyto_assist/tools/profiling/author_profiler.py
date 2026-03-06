#!/usr/bin/env python3
"""Author Profiler — Build scholarly profiles with MeSH specialty inference.

Retrieves author metrics (h-index, citations, papers), computes paper
relevance scores, infers research specialties via MeSH annotation,
and analyzes temporal focus shifts.

Usage:
    python author_profiler.py profile --name "Michael I. Love"
    python author_profiler.py specialty --author-id "S2:3242" --mesh-year 2026
    python author_profiler.py metrics --orcid "0000-0001-8401-0545"
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests

S2_API = "https://api.semanticscholar.org/graph/v1"
OPENALEX_API = "https://api.openalex.org"
ORCID_API = "https://pub.orcid.org/v3.0"
CACHE_DIR = Path.home() / ".cache" / "cytognosis" / "author_profiles"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def search_author_s2(name: str) -> dict[str, Any] | None:
    """Search for an author on Semantic Scholar."""
    try:
        resp = requests.get(
            f"{S2_API}/author/search",
            params={"query": name, "limit": 1,
                    "fields": "name,paperCount,citationCount,hIndex"},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            if data.get("data"):
                return data["data"][0]
    except Exception:
        pass
    return None


def get_author_papers_s2(
    author_id: str, limit: int = 200
) -> list[dict[str, Any]]:
    """Get an author's papers from Semantic Scholar."""
    papers = []
    offset = 0
    while offset < limit:
        try:
            resp = requests.get(
                f"{S2_API}/author/{author_id}/papers",
                params={
                    "offset": offset,
                    "limit": min(100, limit - offset),
                    "fields": "title,year,citationCount,journal,authors,"
                              "publicationTypes,externalIds,abstract",
                },
                timeout=15,
            )
            if not resp.ok:
                break
            data = resp.json()
            batch = data.get("data", [])
            if not batch:
                break
            papers.extend(batch)
            offset += len(batch)
            if offset >= data.get("total", 0):
                break
            time.sleep(0.3)
        except Exception:
            break
    return papers


def compute_paper_relevance(
    paper: dict[str, Any],
    author_id: str,
    current_year: int = 2026,
) -> float:
    """Compute relevance score for a paper relative to an author.

    Combines:
        w_authorship: 1.0 (first/last), 0.5 (second/penultimate), 0.3 (other)
        w_citations:  normalized log(citations_per_year + 1)
        w_recency:    exponential decay based on years since publication

    Returns:
        Combined weight in [0, 1]
    """
    # Authorship weight
    authors = paper.get("authors", [])
    author_ids = [a.get("authorId", "") for a in authors]
    w_authorship = 0.3  # default: middle author

    if author_id in author_ids:
        idx = author_ids.index(author_id)
        n_authors = len(author_ids)
        if idx == 0 or idx == n_authors - 1:
            w_authorship = 1.0  # first or last
        elif idx == 1 or idx == n_authors - 2:
            w_authorship = 0.5  # second or penultimate
    elif str(author_id) in [str(a.get("authorId", "")) for a in authors]:
        w_authorship = 0.3

    # Citations per year
    year = paper.get("year", current_year)
    if year is None:
        year = current_year
    years_since = max(current_year - year, 1)
    citations = paper.get("citationCount", 0) or 0
    cpy = citations / years_since
    w_citations = min(math.log(cpy + 1) / 5.0, 1.0)  # normalize

    # Recency weight (exponential decay, half-life = 10 years)
    w_recency = math.exp(-0.07 * years_since)

    # Combined
    w_combined = w_authorship * 0.4 + w_citations * 0.4 + w_recency * 0.2

    return round(min(w_combined, 1.0), 4)


def infer_specialty_from_abstracts(
    papers: list[dict[str, Any]],
    weights: list[float],
    mesh_tree: Any = None,
    bin_years: int = 60,
) -> dict[str, Any]:
    """Infer research specialty from paper abstracts using MeSH.

    Aggregates MeSH annotations across papers, weighted by relevance,
    with temporal binning.

    Args:
        papers: List of paper dicts (must have 'abstract', 'year')
        weights: Paper relevance weights
        mesh_tree: Optional MeSHTree instance
        bin_years: Months per time bin (default 60 = 5 years)

    Returns:
        Dict with overall and per-bin MeSH specialties
    """
    if mesh_tree is None:
        return {"error": "MeSH tree not available"}

    bin_size = bin_years // 12  # convert months to years

    # Temporal bins
    bins: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for paper, weight in zip(papers, weights, strict=True):
        abstract = paper.get("abstract", "")
        year = paper.get("year")
        if not abstract or not year:
            continue

        # Annotate with MeSH
        annotations = mesh_tree.annotate(abstract, threshold=0.1, top_k=10)

        # Determine bin
        bin_start = (year // bin_size) * bin_size
        bin_label = f"{bin_start}-{bin_start + bin_size - 1}"

        for ui, info in annotations.items():
            mesh_weight = info["weight"]
            bins[bin_label][ui] = bins[bin_label].get(ui, 0) + mesh_weight * weight

    # Sort each bin's terms
    result: dict[str, Any] = {"bins": {}}
    overall: dict[str, float] = defaultdict(float)

    for bin_label in sorted(bins.keys()):
        sorted_terms = sorted(bins[bin_label].items(), key=lambda x: x[1], reverse=True)
        result["bins"][bin_label] = sorted_terms[:20]

        for ui, w in sorted_terms:
            overall[ui] += w

    result["overall"] = sorted(overall.items(), key=lambda x: x[1], reverse=True)[:30]

    # Latest bin
    if bins:
        latest_bin = sorted(bins.keys())[-1]
        result["latest_focus"] = sorted(
            bins[latest_bin].items(), key=lambda x: x[1], reverse=True
        )[:20]

    return result


def build_profile(name: str) -> dict[str, Any]:
    """Build a complete author profile."""
    profile: dict[str, Any] = {"name": name}

    # Search Semantic Scholar
    author = search_author_s2(name)
    if not author:
        profile["error"] = "Author not found"
        return profile

    author_id = author.get("authorId", "")
    profile["s2_id"] = author_id
    profile["paper_count"] = author.get("paperCount", 0)
    profile["citation_count"] = author.get("citationCount", 0)
    profile["h_index"] = author.get("hIndex", 0)

    # Get papers
    papers = get_author_papers_s2(author_id, limit=200)
    profile["papers_retrieved"] = len(papers)

    # Compute relevance weights
    weights = [
        compute_paper_relevance(p, author_id) for p in papers
    ]
    profile["top_papers"] = []
    for paper, weight in sorted(
        zip(papers, weights, strict=True), key=lambda x: x[1], reverse=True
    )[:10]:
        profile["top_papers"].append({
            "title": paper.get("title", "")[:80],
            "year": paper.get("year"),
            "citations": paper.get("citationCount", 0),
            "relevance": weight,
        })

    return profile


# ── CLI ──────────────────────────────────────────────────────────────


def cmd_profile(args: list[str]) -> int:
    """Build author profile."""
    import argparse

    parser = argparse.ArgumentParser(description="Author profile")
    parser.add_argument("--name", "-n", required=True, help="Author name")
    parser.add_argument("--output", help="Output JSON")
    parsed = parser.parse_args(args)

    profile = build_profile(parsed.name)

    print(f"\nAuthor: {profile['name']}")
    print(f"  S2 ID: {profile.get('s2_id', 'N/A')}")
    print(f"  Papers: {profile.get('paper_count', 0):,}")
    print(f"  Citations: {profile.get('citation_count', 0):,}")
    print(f"  h-index: {profile.get('h_index', 0)}")
    print(f"  Retrieved: {profile.get('papers_retrieved', 0)} papers")

    print("\nTop 10 papers by relevance:")
    for p in profile.get("top_papers", []):
        print(f"  [{p['year']}] {p['title']} (cit: {p['citations']}, rel: {p['relevance']})")

    if parsed.output:
        with open(parsed.output, "w") as f:
            json.dump(profile, f, indent=2)

    return 0


def cmd_specialty(args: list[str]) -> int:
    """Infer author specialty using MeSH annotations on their papers."""
    import argparse
    from cyto_assist.modules.annotation.mesh_annotator import MeSHTree, download_mesh, MESH_DIR

    parser = argparse.ArgumentParser(description="Author MeSH specialty")
    parser.add_argument("--name", "-n", help="Author name")
    parser.add_argument("--author-id", help="Semantic Scholar author ID")
    parser.add_argument("--mesh-year", type=int, default=2026)
    parsed = parser.parse_args(args)

    if not parsed.name and not parsed.author_id:
        print("Provide --name or --author-id")
        return 1

    author_id = parsed.author_id
    if not author_id:
        author = search_author_s2(parsed.name)
        if not author:
            print("Author not found.")
            return 1
        author_id = author.get("authorId")
        print(f"Found author: {author.get('name')} (ID: {author_id})")

    print(f"Fetching papers for {author_id}...")
    papers = get_author_papers_s2(author_id, limit=300)
    print(f"Retrieved {len(papers)} papers.")

    weights = [compute_paper_relevance(p, author_id) for p in papers]

    xml_path = MESH_DIR / f"desc{parsed.mesh_year}.xml"
    if not xml_path.exists():
        download_mesh(parsed.mesh_year)

    print("Loading MeSH Tree...")
    mesh = MeSHTree(xml_path)

    print("Inferring specialties from abstracts...")
    specialties = infer_specialty_from_abstracts(papers, weights, mesh_tree=mesh, bin_years=60)

    if "error" in specialties:
        print(f"Error: {specialties['error']}")
        return 1

    print("\n--- Overall Specialty ---")
    for ui, w in specialties.get("overall", [])[:15]:
        name = mesh.descriptors.get(ui, {}).get("name", ui)
        print(f"  {name:40} {w:.2f}")

    print("\n--- Latest Focus ---")
    for ui, w in specialties.get("latest_focus", [])[:15]:
        name = mesh.descriptors.get(ui, {}).get("name", ui)
        print(f"  {name:40} {w:.2f}")

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: author_profiler.py <command> [args]")
        print("Commands: profile, specialty")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]
    commands = {
        "profile": cmd_profile,
        "specialty": cmd_specialty,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        return 1

    return commands[command](args)


if __name__ == "__main__":
    sys.exit(main())
