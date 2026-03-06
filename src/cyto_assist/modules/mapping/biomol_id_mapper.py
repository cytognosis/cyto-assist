#!/usr/bin/env python3
"""Biomolecular ID Mapper — Harmonize diverse biomolecular identifiers.

Maps between diverse identifiers for genes, proteins, variants, transcripts,
and chemicals to canonical standard IDs using MyGene.info, UniProt, Ensembl,
and PubChem APIs.

Canonical IDs:
    Gene:       HGNC Symbol (e.g., TP53)
    Protein:    UniProt Accession (e.g., P04637)
    Variant:    rsID (e.g., rs121913343)
    Transcript: Ensembl ID (e.g., ENST00000269305)
    Chemical:   ChEBI ID (e.g., CHEBI:15422)

Usage:
    python biomol_id_mapper.py map --type gene --id "7157"
    python biomol_id_mapper.py map --type gene --id "ENSG00000141510"
    python biomol_id_mapper.py batch-map --input entities.tsv --output mapped.tsv
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

import duckdb
import requests

CACHE_DIR = Path.home() / ".cache" / "cytognosis" / "biomol_ids"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API endpoints
MYGENE_URL = "https://mygene.info/v3"
UNIPROT_URL = "https://rest.uniprot.org"
ENSEMBL_URL = "https://rest.ensembl.org"
PUBCHEM_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


class IDCache:
    """Simple file-backed cache for ID mappings."""

    def __init__(self, name: str) -> None:
        self.path = CACHE_DIR / f"{name}_cache.json"
        self._data: dict[str, Any] = {}
        if self.path.exists():
            with open(self.path) as f:
                self._data = json.load(f)

    def get(self, key: str) -> Any | None:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def save(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self._data, f)

class BioregistryMapper:
    """Map any entity to its canonical identifier natively using the DuckDB bioregistry."""
    def __init__(self, db_path: str = "/home/mohammadi/bioregistry.db") -> None:
        self.db_path = db_path
        self.conn = duckdb.connect(self.db_path, read_only=True)

    def map(self, identifier: str, entity_type: str | None = None) -> dict[str, Any]:
        """Map identifier using v_translate_id or UMLS."""

        # Fast path if explicitly asking for UMLS text resolution (disease/term)
        if entity_type in ("disease", "term", "mesh", "concept"):
            umls_query = """
                SELECT CUI
                FROM umls_mrconso
                WHERE STR ILIKE ? AND LAT='ENG'
                ORDER BY ISPREF DESC, TS DESC
                LIMIT 1
            """
            try:
                cui_res = self.conn.execute(umls_query, [identifier]).fetchone()
                if cui_res:
                    return {
                        "input": identifier,
                        "canonical_id": cui_res[0],
                        "canonical_type": "CUI",
                        "matched_via": "UMLS_MRCONSO",
                        "source": "bioregistry"
                    }
            except Exception:
                pass

        # Default Ensembl-canonical Biomolecular routing
        query = """
            SELECT canonical_id, canonical_type, id_type
            FROM v_translate_id
            WHERE input_id = ?
            ORDER BY
              CASE
                WHEN canonical_id LIKE 'ENSG%' THEN 1
                WHEN canonical_id LIKE 'ENST%' THEN 2
                WHEN canonical_id LIKE 'ENSP%' THEN 3
                ELSE 4
              END ASC
            LIMIT 1
        """
        try:
            res = self.conn.execute(query, [identifier]).fetchone()
            if res:
                return {
                    "input": identifier,
                    "canonical_id": res[0],
                    "canonical_type": res[1],
                    "matched_via": res[2],
                    "source": "bioregistry"
                }
        except Exception:
            pass
        return {}


class GeneMapper:
    """Map gene identifiers to canonical HGNC Symbol via MyGene.info.

    Handles: Entrez ID, Ensembl gene ID, symbol, alias, RefSeq, UniGene.
    """

    def __init__(self) -> None:
        self.cache = IDCache("gene")

    def map_to_hgnc(self, identifier: str, species: str = "human") -> dict[str, Any]:
        """Map any gene identifier to HGNC Symbol."""
        cached = self.cache.get(identifier)
        if cached:
            return cached

        result = {"input": identifier, "hgnc_symbol": None, "entrez_id": None,
                  "ensembl_gene": None, "name": None, "source": "mygene"}

        try:
            # Try MyGene.info query
            resp = requests.get(
                f"{MYGENE_URL}/query",
                params={
                    "q": identifier,
                    "species": species,
                    "fields": "symbol,name,entrezgene,ensembl.gene,HGNC",
                    "size": 1,
                },
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                hits = data.get("hits", [])
                if hits:
                    hit = hits[0]
                    result["hgnc_symbol"] = hit.get("symbol")
                    result["entrez_id"] = str(hit.get("entrezgene", ""))
                    result["name"] = hit.get("name")
                    ensembl = hit.get("ensembl", {})
                    if isinstance(ensembl, list):
                        ensembl = ensembl[0]
                    result["ensembl_gene"] = (
                        ensembl.get("gene")
                        if isinstance(ensembl, dict)
                        else None
                    )
        except Exception as e:
            result["error"] = str(e)

        self.cache.set(identifier, result)
        return result

    def batch_map(self, identifiers: list[str], species: str = "human") -> list[dict[str, Any]]:
        """Batch map gene identifiers."""
        results = []
        # Use MyGene.info batch endpoint
        uncached = [i for i in identifiers if not self.cache.get(i)]
        if uncached:
            try:
                resp = requests.post(
                    f"{MYGENE_URL}/query",
                    json={
                        "q": uncached,
                        "scopes": "symbol,alias,entrezgene,ensembl.gene,refseq.rna",
                        "species": species,
                        "fields": "symbol,name,entrezgene,ensembl.gene",
                    },
                    timeout=30,
                )
                if resp.ok:
                    for hit in resp.json():
                        query = hit.get("query", "")
                        result = {
                            "input": query,
                            "hgnc_symbol": hit.get("symbol"),
                            "entrez_id": str(hit.get("entrezgene", "")),
                            "name": hit.get("name"),
                            "ensembl_gene": None,
                            "source": "mygene_batch",
                        }
                        ensembl = hit.get("ensembl", {})
                        if isinstance(ensembl, list):
                            ensembl = ensembl[0]
                        if isinstance(ensembl, dict):
                            result["ensembl_gene"] = ensembl.get("gene")
                        self.cache.set(query, result)
            except Exception:
                pass

        for ident in identifiers:
            cached = self.cache.get(ident)
            if cached:
                results.append(cached)
            else:
                results.append(self.map_to_hgnc(ident, species))

        self.cache.save()
        return results


class ProteinMapper:
    """Map protein identifiers to canonical UniProt Accession."""

    def __init__(self) -> None:
        self.cache = IDCache("protein")

    def map_to_uniprot(self, identifier: str) -> dict[str, Any]:
        """Map protein ID to UniProt accession."""
        cached = self.cache.get(identifier)
        if cached:
            return cached

        result = {"input": identifier, "uniprot_accession": None,
                  "protein_name": None, "gene_name": None, "source": "uniprot"}

        try:
            # UniProt search
            resp = requests.get(
                f"{UNIPROT_URL}/uniprotkb/search",
                params={
                    "query": identifier,
                    "format": "json",
                    "size": 1,
                    "fields": "accession,protein_name,gene_names,organism_name",
                },
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                results_list = data.get("results", [])
                if results_list:
                    hit = results_list[0]
                    result["uniprot_accession"] = hit.get("primaryAccession")
                    pname = hit.get("proteinDescription", {}).get("recommendedName", {})
                    if pname:
                        result["protein_name"] = pname.get("fullName", {}).get("value")
                    genes = hit.get("genes", [])
                    if genes:
                        result["gene_name"] = genes[0].get("geneName", {}).get("value")
        except Exception as e:
            result["error"] = str(e)

        self.cache.set(identifier, result)
        return result


class VariantMapper:
    """Map variant identifiers to canonical rsID."""

    def __init__(self) -> None:
        self.cache = IDCache("variant")

    def map_to_rsid(self, identifier: str) -> dict[str, Any]:
        """Map variant notation to rsID."""
        cached = self.cache.get(identifier)
        if cached:
            return cached

        result = {"input": identifier, "rsid": None, "source": "ensembl"}

        # If already an rsID, just return it
        if identifier.startswith("rs"):
            result["rsid"] = identifier
            self.cache.set(identifier, result)
            return result

        try:
            # Try Ensembl VEP
            resp = requests.get(
                f"{ENSEMBL_URL}/vep/human/hgvs/{identifier}",
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                if data and isinstance(data, list):
                    for entry in data:
                        colocated = entry.get("colocated_variants", [])
                        for var in colocated:
                            vid = var.get("id", "")
                            if vid.startswith("rs"):
                                result["rsid"] = vid
                                break
        except Exception as e:
            result["error"] = str(e)

        self.cache.set(identifier, result)
        return result


class ChemicalMapper:
    """Map chemical identifiers to canonical ChEBI ID."""

    def __init__(self) -> None:
        self.cache = IDCache("chemical")

    def map_to_chebi(self, identifier: str) -> dict[str, Any]:
        """Map chemical name/ID to ChEBI."""
        cached = self.cache.get(identifier)
        if cached:
            return cached

        result = {"input": identifier, "chebi_id": None,
                  "name": None, "source": "chebi"}

        # If already a ChEBI ID
        if identifier.upper().startswith("CHEBI:"):
            result["chebi_id"] = identifier
            self.cache.set(identifier, result)
            return result

        try:
            # Use OLS4 API to find ChEBI term
            resp = requests.get(
                "https://www.ebi.ac.uk/ols4/api/search",
                params={
                    "q": identifier,
                    "ontology": "chebi",
                    "exact": "true",
                    "rows": 1,
                },
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    obo_id = docs[0].get("obo_id", "")
                    result["chebi_id"] = obo_id
                    result["name"] = docs[0].get("label")
        except Exception as e:
            result["error"] = str(e)

        self.cache.set(identifier, result)
        return result


class UnifiedMapper:
    """Routes entity type to appropriate mapper."""

    def __init__(self) -> None:
        self.bioregistry = BioregistryMapper()
        self.gene = GeneMapper()
        self.protein = ProteinMapper()
        self.variant = VariantMapper()
        self.chemical = ChemicalMapper()

    def map(self, identifier: str, entity_type: str) -> dict[str, Any]:
        """Map an identifier to its canonical form natively via Bioregistry, falling back to APIs.

        Args:
            identifier: The raw identifier
            entity_type: One of 'gene', 'protein', 'variant', 'chemical'

        Returns:
            Mapping result dict with canonical ID
        """
        # 1. Native Bioregistry Lookup (Fast & Ensembl/UMLS-standardized)
        res = self.bioregistry.map(identifier, entity_type)
        if res:
            return res
        entity_type = entity_type.lower()

        if entity_type == "gene":
            return self.gene.map_to_hgnc(identifier)
        elif entity_type == "protein":
            return self.protein.map_to_uniprot(identifier)
        elif entity_type == "variant":
            return self.variant.map_to_rsid(identifier)
        elif entity_type in ("chemical", "drug"):
            return self.chemical.map_to_chebi(identifier)
        elif entity_type in ("disease", "term", "mesh", "concept"):
            # If bioregistry failed on a UMLS phrase... don't fall back to chemical parsing
            return {"input": identifier, "cui": None, "error": "Not found in UMLS"}
        else:
            return {"input": identifier, "error": f"Unknown type: {entity_type}"}

    def save_caches(self) -> None:
        """Persist all caches to disk."""
        self.gene.cache.save()
        self.protein.cache.save()
        self.variant.cache.save()
        self.chemical.cache.save()


# ── CLI ──────────────────────────────────────────────────────────────


def cmd_map(args: list[str]) -> int:
    """Map a single identifier."""
    import argparse

    parser = argparse.ArgumentParser(description="Map biomolecular ID")
    parser.add_argument("--type", "-t", required=True,
                        choices=["gene", "protein", "variant", "chemical"])
    parser.add_argument("--id", "-i", required=True, help="Identifier to map")
    parsed = parser.parse_args(args)

    mapper = UnifiedMapper()
    result = mapper.map(parsed.id, parsed.type)
    mapper.save_caches()

    for k, v in result.items():
        print(f"  {k}: {v}")

    return 0


def cmd_batch_map(args: list[str]) -> int:
    """Batch map identifiers from TSV."""
    import argparse

    parser = argparse.ArgumentParser(description="Batch map biomolecular IDs")
    parser.add_argument("--input", "-i", required=True, help="Input TSV")
    parser.add_argument("--output", "-o", required=True, help="Output TSV")
    parser.add_argument("--type-col", default="entity_type", help="Entity type column")
    parser.add_argument("--id-col", default="entity_id", help="Entity ID column")
    parsed = parser.parse_args(args)

    mapper = UnifiedMapper()

    with open(parsed.input) as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    print(f"Mapping {len(rows)} entities...")
    results = []
    for i, row in enumerate(rows):
        entity_type = row.get(parsed.type_col, "gene")
        entity_id = row.get(parsed.id_col, "")

        if not entity_id:
            continue

        result = mapper.map(entity_id, entity_type)
        row["canonical_id"] = (
            result.get("canonical_id")
            or result.get("hgnc_symbol")
            or result.get("uniprot_accession")
            or result.get("rsid")
            or result.get("chebi_id")
            or ""
        )
        results.append(row)

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(rows)} mapped")
            time.sleep(0.1)

    mapper.save_caches()

    if results:
        fieldnames = list(results[0].keys())
        with open(parsed.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Saved {len(results)} mapped entities to {parsed.output}")

    return 0


def cmd_validate(args: list[str]) -> int:
    """Validate ID mapping accuracy."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate ID mapping")
    _ = parser.parse_args(args)

    mapper = UnifiedMapper()

    test_cases = [
        ("gene", "7157", "ENSG00000141510"),      # Entrez ID → ENSG
        ("gene", "ENSG00000141510", "ENSG00000141510"),  # Ensembl → ENSG
        ("gene", "TP53", "ENSG00000141510"),       # Symbol → ENSG
        ("gene", "BRCA1", "ENSG00000012048"),     # Symbol → ENSG
        ("gene", "672", "ENSG00000012048"),       # Entrez for BRCA1
        ("protein", "P04637", "ENSP00000391127"), # UniProt → ENSP
        ("chemical", "aspirin", "CHEBI:134674"),   # Name to ChEBI
        ("variant", "rs121913343", "rs121913343"),  # Already rsID
        ("disease", "16,16-Dimethylprostaglandin E2", "C0000139"), # Exact string UMLS to CUI
        ("term", "Neoplasms", "C0027651"), # Exact string UMLS to CUI
    ]

    passed = 0
    for entity_type, input_id, expected in test_cases:
        result = mapper.map(input_id, entity_type)
        canonical = (
            result.get("canonical_id")
            or result.get("hgnc_symbol")
            or result.get("uniprot_accession")
            or result.get("rsid")
            or result.get("chebi_id")
        )
        status = "✅" if expected is None or canonical == expected else "❌"
        if status == "✅":
            passed += 1
        print(f"  {status} {entity_type}:{input_id} → {canonical} (expected: {expected})")
        time.sleep(0.3)

    mapper.save_caches()
    print(f"\n{passed}/{len(test_cases)} tests passed")
    return 0


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: biomol_id_mapper.py <command> [args]")
        print("Commands: map, batch-map, validate")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "map": cmd_map,
        "batch-map": cmd_batch_map,
        "validate": cmd_validate,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        return 1

    return commands[command](args)


if __name__ == "__main__":
    sys.exit(main())
