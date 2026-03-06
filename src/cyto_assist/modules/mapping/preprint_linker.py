#!/usr/bin/env python3
"""Preprint Linker — Link preprints to their final publications.

Uses bioRxiv/medRxiv API, Crossref, and Semantic Scholar to find
preprint↔publication relationships. Creates PREPRINT_OF / PUBLISHED_AS
edges in the knowledge graph.

Usage:
    python preprint_linker.py link --doi "10.1101/2020.01.10.927806"
    python preprint_linker.py batch-link --input dois.txt --output links.json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import requests

BIORXIV_API = "https://api.biorxiv.org"
S2_API = "https://api.semanticscholar.org/graph/v1"
CROSSREF_API = "https://api.crossref.org/works"


def link_preprint_to_publication(doi: str) -> dict[str, Any]:
    """Find a preprint's final publication or vice versa.

    Args:
        doi: DOI of either the preprint or the publication

    Returns:
        Dict with preprint_doi, publication_doi, relationship, source
    """
    result: dict[str, Any] = {
        "input_doi": doi,
        "preprint_doi": None,
        "publication_doi": None,
        "preprint_server": None,
        "journal": None,
        "relationship": None,
        "source": None,
    }

    # Check if this is a bioRxiv/medRxiv DOI
    is_preprint = "10.1101/" in doi

    if is_preprint:
        result["preprint_doi"] = doi
        result["preprint_server"] = "bioRxiv/medRxiv"

        # Try bioRxiv API
        try:
            # Extract the DOI suffix
            suffix = doi.replace("10.1101/", "")
            resp = requests.get(
                f"{BIORXIV_API}/details/biorxiv/{suffix}",
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                collection = data.get("collection", [])
                for entry in collection:
                    pub_doi = entry.get("published_doi")
                    if pub_doi:
                        result["publication_doi"] = pub_doi
                        result["journal"] = entry.get("published_journal", "")
                        result["relationship"] = "preprint_published_as"
                        result["source"] = "biorxiv_api"
                        return result
        except Exception:
            pass

        # Try medRxiv API
        try:
            suffix = doi.replace("10.1101/", "")
            resp = requests.get(
                f"{BIORXIV_API}/details/medrxiv/{suffix}",
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                collection = data.get("collection", [])
                for entry in collection:
                    pub_doi = entry.get("published_doi")
                    if pub_doi:
                        result["publication_doi"] = pub_doi
                        result["preprint_server"] = "medRxiv"
                        result["journal"] = entry.get("published_journal", "")
                        result["relationship"] = "preprint_published_as"
                        result["source"] = "medrxiv_api"
                        return result
        except Exception:
            pass

    # Try Semantic Scholar for either direction
    try:
        resp = requests.get(
            f"{S2_API}/paper/DOI:{doi}",
            params={"fields": "externalIds,title,journal,publicationTypes"},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            ext_ids = data.get("externalIds", {})
            arxiv_id = ext_ids.get("ArXiv")

            if not is_preprint and arxiv_id:
                result["publication_doi"] = doi
                result["preprint_doi"] = f"arxiv:{arxiv_id}"
                result["preprint_server"] = "arXiv"
                result["relationship"] = "publication_has_preprint"
                result["source"] = "semantic_scholar"
    except Exception:
        pass

    # Try Crossref for related works
    if not result["publication_doi"] and not result["preprint_doi"]:
        try:
            resp = requests.get(
                f"{CROSSREF_API}/{doi}",
                headers={"User-Agent": "Cytognosis/1.0 (mailto:shahin@cytognosis.org)"},
                timeout=10,
            )
            if resp.ok:
                data = resp.json().get("message", {})
                relations = data.get("relation", {})
                for _rel_type, rels in relations.items():
                    for rel in rels:
                        rel_doi = rel.get("id", "")
                        if "10.1101/" in rel_doi:
                            result["preprint_doi"] = rel_doi
                            result["publication_doi"] = doi
                            result["preprint_server"] = "bioRxiv/medRxiv"
                            result["relationship"] = "publication_has_preprint"
                            result["source"] = "crossref"
                            return result
        except Exception:
            pass

    return result


# ── CLI ──────────────────────────────────────────────────────────────


def cmd_link(args: list[str]) -> int:
    """Link a single DOI."""
    import argparse

    parser = argparse.ArgumentParser(description="Link preprint↔publication")
    parser.add_argument("--doi", required=True, help="DOI to look up")
    parsed = parser.parse_args(args)

    result = link_preprint_to_publication(parsed.doi)
    for k, v in result.items():
        if v:
            print(f"  {k}: {v}")

    if result["publication_doi"] and result["preprint_doi"]:
        print(f"\n✅ Linked: {result['preprint_doi']} → {result['publication_doi']}")
    else:
        print(f"\n⚠️ No link found for {parsed.doi}")

    return 0


def cmd_batch_link(args: list[str]) -> int:
    """Batch link DOIs."""
    import argparse

    parser = argparse.ArgumentParser(description="Batch link preprints")
    parser.add_argument("--input", "-i", required=True, help="File with DOIs (one per line)")
    parser.add_argument("--output", "-o", required=True, help="Output JSON")
    parsed = parser.parse_args(args)

    dois = Path(parsed.input).read_text().strip().split("\n")
    results = []

    for doi in dois:
        doi = doi.strip()
        if not doi:
            continue
        result = link_preprint_to_publication(doi)
        results.append(result)
        linked = "✅" if result.get("publication_doi") and result.get("preprint_doi") else "—"
        print(f"  {linked} {doi}")
        time.sleep(0.5)

    with open(parsed.output, "w") as f:
        json.dump(results, f, indent=2)

    linked_count = sum(
        1 for r in results
        if r.get("publication_doi") and r.get("preprint_doi")
    )
    print(f"\n✅ {linked_count}/{len(results)} DOIs linked, saved to {parsed.output}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: preprint_linker.py <command> [args]")
        print("Commands: link, batch-link")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]
    commands = {"link": cmd_link, "batch-link": cmd_batch_link}

    if command not in commands:
        print(f"Unknown command: {command}")
        return 1

    return commands[command](args)


if __name__ == "__main__":
    sys.exit(main())
