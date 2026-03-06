#!/usr/bin/env python3
"""Entity Harmonization — Map extracted entities to standard ontologies.

Maps biomedical entities from paper parsing and PKG data to standardized
ontology terms via:
1. Direct ID matching (MeSH → MONDO via xrefs, CL → Cell Ontology)
2. String matching (fuzzy entity name → ontology term label)
3. OLS4 API lookup for unmatched entities

Usage:
    python entity_harmonizer.py map-mesh MESH_ID       # Map MeSH to MONDO
    python entity_harmonizer.py map-name "entity name"  # Fuzzy match to ontology
    python entity_harmonizer.py batch INPUT.tsv OUT.tsv  # Batch harmonization
    python entity_harmonizer.py profile PKG_ENTITIES     # Profile PKG entity coverage
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import requests

# ── Configuration ────────────────────────────────────────────────────────────

OLS4_API = "https://www.ebi.ac.uk/ols4/api"
CACHE_DIR = Path.home() / ".cache" / "cytognosis" / "ontology_mappings"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# PKG entity type → target ontology mapping
ENTITY_ONTOLOGY_MAP = {
    "disease": {"ontology": "mondo", "id_prefix": "MONDO:"},
    "gene": {"ontology": None, "id_prefix": "NCBIGene:"},
    "drug": {"ontology": "chebi", "id_prefix": "CHEBI:"},
    "species": {"ontology": "ncbitaxon", "id_prefix": "NCBITaxon:"},
    "cell_type": {"ontology": "cl", "id_prefix": "CL:"},
    "cell_line": {"ontology": "clo,efo,ncit", "id_prefix": "EFO:"},
    "tissue": {"ontology": "uberon", "id_prefix": "UBERON:"},
}

# MeSH → MONDO xref patterns (from MONDO OWL)
MESH_MONDO_CACHE_FILE = CACHE_DIR / "mesh_to_mondo.json"


def _ols4_search(
    query: str,
    ontology: str | None = None,
    exact: bool = False,
) -> list[dict[str, Any]]:
    """Search OLS4 API for a term."""
    params: dict[str, Any] = {"q": query, "rows": 10}
    if ontology:
        params["ontology"] = ontology
    if exact:
        params["exact"] = "true"

    try:
        resp = requests.get(f"{OLS4_API}/search", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("response", {}).get("docs", [])
    except requests.RequestException as e:
        print(f"  ⚠️ OLS4 API error: {e}")
        return []


def _ols4_term(ontology: str, iri: str) -> dict[str, Any] | None:
    """Get full term details from OLS4."""
    try:
        resp = requests.get(
            f"{OLS4_API}/ontologies/{ontology}/terms",
            params={"iri": iri},
            timeout=10,
        )
        resp.raise_for_status()
        terms = resp.json().get("_embedded", {}).get("terms", [])
        return terms[0] if terms else None
    except requests.RequestException:
        return None


def map_mesh_to_mondo(mesh_id: str) -> dict[str, Any]:
    """Map a MeSH ID to MONDO via OLS4 cross-references.

    Args:
        mesh_id: MeSH descriptor ID (e.g., 'D012559' or 'meshD012559')

    Returns:
        Dict with mondo_id, label, definition, xrefs
    """
    # Normalize
    mesh_id = mesh_id.replace("mesh", "").replace("MeSH:", "")

    # Search OLS4 MONDO for this MeSH xref
    results = _ols4_search(f"MESH:{mesh_id}", ontology="mondo")

    for doc in results:
        obo_id = doc.get("obo_id", "")
        if obo_id.startswith("MONDO:"):
            return {
                "mesh_id": f"MeSH:{mesh_id}",
                "mondo_id": obo_id,
                "label": doc.get("label", ""),
                "description": doc.get("description", [""])[0] if doc.get("description") else "",
                "iri": doc.get("iri", ""),
                "exact_match": doc.get("is_exact", False),
            }

    return {
        "mesh_id": f"MeSH:{mesh_id}",
        "mondo_id": None,
        "label": None,
        "description": None,
        "error": "No MONDO mapping found",
    }


def map_name_to_ontology(
    name: str,
    entity_type: str | None = None,
) -> list[dict[str, Any]]:
    """Map an entity name to ontology terms via fuzzy search.

    Args:
        name: Entity mention (e.g., 'schizophrenia', 'TP53')
        entity_type: Optional PKG entity type to select target ontology

    Returns:
        List of candidate matches with scores
    """
    ontology = None
    if entity_type and entity_type in ENTITY_ONTOLOGY_MAP:
        ontology = ENTITY_ONTOLOGY_MAP[entity_type]["ontology"]

    results = _ols4_search(name, ontology=ontology)

    candidates = []
    for doc in results:
        candidates.append({
            "query": name,
            "entity_type": entity_type,
            "obo_id": doc.get("obo_id", ""),
            "label": doc.get("label", ""),
            "ontology": doc.get("ontology_name", ""),
            "description": (doc.get("description", [""])[0]
                          if doc.get("description") else ""),
            "is_exact": name.lower() == doc.get("label", "").lower(),
        })

    return candidates


def batch_harmonize(
    input_path: str,
    output_path: str,
    entity_type_col: str = "Type",
    mention_col: str = "Mention",
    entity_id_col: str = "EntityId",
) -> None:
    """Batch harmonize entities from a TSV file.

    Reads entities, maps to ontology terms, writes enriched output.
    Caches results to avoid redundant API calls.
    """
    cache_file = CACHE_DIR / "batch_cache.json"
    cache: dict[str, Any] = {}
    if cache_file.exists():
        cache = json.loads(cache_file.read_text())

    input_p = Path(input_path)
    output_p = Path(output_path)

    with open(input_p) as fin, open(output_p, "w", newline="") as fout:
        reader = csv.DictReader(fin, delimiter="\t")
        fieldnames = list(reader.fieldnames or []) + [
            "mapped_ontology_id",
            "mapped_label",
            "mapping_method",
        ]
        writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()

        count = 0
        mapped = 0
        for row in reader:
            entity_id = row.get(entity_id_col, "")
            mention = row.get(mention_col, "")
            etype = row.get(entity_type_col, "")

            # Check cache
            cache_key = f"{entity_id}:{mention}"
            if cache_key in cache:
                row.update(cache[cache_key])
                writer.writerow(row)
                mapped += 1
                count += 1
                continue

            # Try ID mapping first
            mapping_result = {"mapped_ontology_id": "", "mapped_label": "",
                            "mapping_method": ""}

            if etype == "disease" and entity_id.startswith("mesh"):
                result = map_mesh_to_mondo(entity_id)
                if result.get("mondo_id"):
                    mapping_result = {
                        "mapped_ontology_id": result["mondo_id"],
                        "mapped_label": result["label"],
                        "mapping_method": "mesh_xref",
                    }
                    mapped += 1

            # Fallback: name search
            if not mapping_result["mapped_ontology_id"] and mention:
                candidates = map_name_to_ontology(mention, etype)
                if candidates and candidates[0].get("is_exact"):
                    mapping_result = {
                        "mapped_ontology_id": candidates[0]["obo_id"],
                        "mapped_label": candidates[0]["label"],
                        "mapping_method": "exact_name",
                    }
                    mapped += 1

            cache[cache_key] = mapping_result
            row.update(mapping_result)
            writer.writerow(row)
            count += 1

            if count % 100 == 0:
                print(f"  Processed {count}, mapped {mapped}")
                # Save cache periodically
                cache_file.write_text(json.dumps(cache, indent=2))

        # Final cache save
        cache_file.write_text(json.dumps(cache, indent=2))
        print(f"\n✅ Complete: {count} entities, {mapped} mapped ({mapped/max(count,1)*100:.1f}%)")


def cmd_profile() -> None:
    """Profile PKG entity coverage against ontologies."""
    import duckdb

    pkg_dir = Path("/home/mohammadi/datasets/network/public/kg/PMK")
    con = duckdb.connect(":memory:")

    print("=" * 60)
    print("PKG Entity Coverage Profile")
    print("=" * 60)

    # Entity ID prefix distribution
    result = con.execute(f"""
        SELECT
            CASE
                WHEN EntityId LIKE 'mesh%' THEN 'MeSH'
                WHEN EntityId LIKE 'NCBIGene%' THEN 'NCBIGene'
                WHEN EntityId LIKE 'NCBITaxon%' THEN 'NCBITaxon'
                WHEN EntityId LIKE 'CHEBI%' THEN 'ChEBI'
                WHEN EntityId LIKE 'CL%' THEN 'CL'
                WHEN EntityId LIKE 'cellosaurus%' THEN 'Cellosaurus'
                ELSE 'Other'
            END AS id_source,
            count(*) AS cnt
        FROM read_csv_auto('{pkg_dir}/C23_BioEntities.tsv',
            delim='\\t', header=true, quote='', strict_mode=false)
        GROUP BY id_source
        ORDER BY cnt DESC
    """).fetchall()

    print(f"\n{'ID Source':<20} {'Count':>10} {'Target Ontology'}")
    print("-" * 55)
    ontology_map = {
        "MeSH": "→ MONDO (diseases), ChEBI (drugs)",
        "NCBIGene": "→ NCBI Gene",
        "NCBITaxon": "→ NCBI Taxonomy",
        "ChEBI": "→ ChEBI",
        "CL": "→ Cell Ontology",
        "Cellosaurus": "→ Cellosaurus",
    }
    for row in result:
        target = ontology_map.get(row[0], "")
        print(f"  {row[0]:<18} {row[1]:>10,}  {target}")

    con.close()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    cmd = sys.argv[1]

    if cmd == "map-mesh":
        if len(sys.argv) < 3:
            print("Usage: entity_harmonizer.py map-mesh MESH_ID")
            return 1
        result = map_mesh_to_mondo(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "map-name":
        if len(sys.argv) < 3:
            print("Usage: entity_harmonizer.py map-name 'entity name'")
            return 1
        name = sys.argv[2]
        etype = sys.argv[3] if len(sys.argv) > 3 else None
        results = map_name_to_ontology(name, etype)
        for r in results:
            exact = "✅" if r["is_exact"] else "  "
            print(f"  {exact} {r['obo_id']}: {r['label']} ({r['ontology']})")

    elif cmd == "batch":
        if len(sys.argv) < 4:
            print("Usage: entity_harmonizer.py batch INPUT.tsv OUTPUT.tsv")
            return 1
        batch_harmonize(sys.argv[2], sys.argv[3])

    elif cmd == "profile":
        cmd_profile()

    else:
        print(f"Unknown command: {cmd}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
