#!/usr/bin/env python3
"""Import papers from Zotero (via BibTeX/CSL-JSON export) into AnyType.

This script reads BibTeX (.bib) or CSL-JSON (.json) exports from Zotero
(ideally produced by Better BibTeX) and creates Paper objects in AnyType
via the bridge.

Workflow:
    1. Zotero exports auto-updating .bib file (Better BibTeX)
    2. This script parses the .bib and creates/updates AnyType Paper objects
    3. anytype_bridge.py can then export those to Markdown for git tracking

Usage:
    python3 zotero_to_anytype.py --bib ~/Zotero/library.bib --space Research
    python3 zotero_to_anytype.py --bib ~/Zotero/library.bib --space Research --dry-run
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Any

import requests

# Reuse the AnyType client from bridge
sys.path.insert(0, str(Path(__file__).parent))
from anytype_bridge import AnyTypeClient, load_api_key

logger = logging.getLogger("zotero_to_anytype")

# ---------------------------------------------------------------------------
# BibTeX Parser (lightweight, no external deps)
# ---------------------------------------------------------------------------


def parse_bibtex(content: str) -> list[dict[str, str]]:
    """Parse BibTeX content into a list of entry dicts.

    Each entry has keys: entry_type, citation_key, and all BibTeX fields.
    This is a lightweight parser that handles the common cases from Better BibTeX.
    """
    entries: list[dict[str, str]] = []
    # Match @type{key, ... }
    pattern = re.compile(
        r"@(\w+)\s*\{\s*([^,]+)\s*,\s*(.*?)\n\}",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        entry_type = match.group(1).lower()
        citation_key = match.group(2).strip()
        fields_str = match.group(3)

        entry: dict[str, str] = {
            "entry_type": entry_type,
            "citation_key": citation_key,
        }

        # Parse key = {value} or key = "value" or key = number
        field_pattern = re.compile(
            r"(\w+)\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}"
            r'|"([^"]*)"'
            r"|(\d+))",
        )
        for field_match in field_pattern.finditer(fields_str):
            key = field_match.group(1).lower()
            value = (
                field_match.group(2)
                or field_match.group(3)
                or field_match.group(4)
                or ""
            )
            # Clean up LaTeX artifacts
            value = value.replace("\\&", "&")
            value = value.replace("\\%", "%")
            value = re.sub(r"\\textit\{([^}]*)\}", r"\1", value)
            value = re.sub(r"\\textbf\{([^}]*)\}", r"\1", value)
            value = re.sub(r"\{([^}]*)\}", r"\1", value)
            entry[key] = value.strip()

        entries.append(entry)

    return entries


def bibtex_to_anytype_data(entry: dict[str, str]) -> dict[str, Any]:
    """Convert a BibTeX entry to AnyType Paper object data."""
    # Build title (prefer title field)
    title = entry.get("title", entry.get("citation_key", "Untitled"))

    # Build properties
    properties: list[dict[str, Any]] = []

    if "doi" in entry:
        properties.append({"key": "doi", "text": entry["doi"]})
        properties.append(
            {
                "key": "source",
                "url": f"https://doi.org/{entry['doi']}",
            }
        )
    elif "url" in entry:
        properties.append({"key": "source", "url": entry["url"]})

    # Journal: check journaltitle (biblatex) then journal (bibtex)
    journal = entry.get("journaltitle") or entry.get("journal", "")
    if journal:
        properties.append({"key": "journal", "text": journal})

    # Year
    year_str = entry.get("year") or entry.get("date", "")[:4]
    if year_str and year_str.isdigit():
        properties.append({"key": "year", "number": int(year_str)})

    # Citation key
    properties.append(
        {"key": "citation_key", "text": entry["citation_key"]}
    )

    # Build abstract as body
    body_parts = []
    if "abstract" in entry:
        body_parts.append(f"## Abstract\n\n{entry['abstract']}")

    if "keywords" in entry:
        kw_list = [
            k.strip() for k in entry["keywords"].split(",") if k.strip()
        ]
        body_parts.append(
            "## Keywords\n\n" + ", ".join(kw_list)
        )

    # Author info in body
    if "author" in entry:
        authors = entry["author"].replace(" and ", ", ")
        body_parts.append(f"## Authors\n\n{authors}")

    data: dict[str, Any] = {
        "type_key": "paper",
        "name": title,
        "icon": {"format": "emoji", "emoji": "📄"},
        "properties": properties,
    }

    if body_parts:
        data["body"] = "\n\n".join(body_parts)

    return data


# ---------------------------------------------------------------------------
# Import Logic
# ---------------------------------------------------------------------------


def import_bib_to_anytype(
    client: AnyTypeClient,
    space_id: str,
    bib_path: Path,
    dry_run: bool = False,
    skip_existing: bool = True,
) -> tuple[int, int, int]:
    """Import BibTeX entries into AnyType Paper objects.

    Returns (created, skipped, errors) counts.
    """
    content = bib_path.read_text(encoding="utf-8")
    entries = parse_bibtex(content)
    logger.info("Parsed %d BibTeX entries from %s", len(entries), bib_path)

    # Get existing papers to check for duplicates by citation_key
    existing_keys: set[str] = set()
    if skip_existing:
        try:
            existing = client.search_space(space_id, types=["paper"])
            for obj in existing:
                for prop in obj.get("properties", []):
                    if (
                        prop.get("key") == "citation_key"
                        and prop.get("text")
                    ):
                        existing_keys.add(prop["text"])
        except requests.HTTPError:
            logger.warning("Could not fetch existing papers for dedup")

    created = 0
    skipped = 0
    errors = 0

    for entry in entries:
        # Skip non-paper types
        if entry["entry_type"] in (
            "string",
            "preamble",
            "comment",
        ):
            continue

        citation_key = entry.get("citation_key", "")
        title = entry.get("title", citation_key)

        if citation_key in existing_keys:
            logger.debug("Skipping existing: %s", citation_key)
            skipped += 1
            continue

        data = bibtex_to_anytype_data(entry)

        if dry_run:
            logger.info(
                "Would create: %s (%s)", title[:60], citation_key
            )
            created += 1
            continue

        try:
            result = client.create_object(space_id, data)
            new_id = result.get("id", "")
            logger.info(
                "Created: %s → %s", citation_key, new_id[:20]
            )
            created += 1
        except requests.HTTPError as e:
            logger.error(
                "Failed to create %s: %s", citation_key, e
            )
            errors += 1

    return created, skipped, errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Import Zotero BibTeX into AnyType Papers",
    )
    parser.add_argument(
        "--bib",
        type=Path,
        required=True,
        help="Path to .bib file (Better BibTeX export)",
    )
    parser.add_argument(
        "--space",
        required=True,
        help="AnyType space name",
    )
    parser.add_argument(
        "--api-key",
        help="AnyType API key (default: from ~/.agents/mcp.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without creating objects",
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Import even if citation_key already exists",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if not args.bib.exists():
        print(f"Error: BibTeX file not found: {args.bib}", file=sys.stderr)
        sys.exit(1)

    api_key = args.api_key or load_api_key()
    client = AnyTypeClient(api_key)

    space = client.find_space(args.space)
    if not space:
        available = [s["name"] for s in client.list_spaces()]
        print(
            f"Error: Space '{args.space}' not found. "
            f"Available: {available}",
            file=sys.stderr,
        )
        sys.exit(1)

    created, skipped, errors = import_bib_to_anytype(
        client,
        space["id"],
        args.bib,
        dry_run=args.dry_run,
        skip_existing=not args.no_skip_existing,
    )

    action = "Would create" if args.dry_run else "Created"
    print(
        f"{action}: {created} | Skipped: {skipped} | Errors: {errors}"
    )


if __name__ == "__main__":
    main()
