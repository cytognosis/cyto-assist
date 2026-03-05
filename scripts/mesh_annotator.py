#!/usr/bin/env python3
"""MeSH Annotator — Download, parse, and annotate papers with MeSH terms.

Downloads MeSH descriptors from NLM, builds the poly-hierarchy as a DAG,
and uses the hierarchical annotation model (dag_annotator) to assign
weighted MeSH term annotations to papers.

Validates predictions against PubMed's own MeSH annotations.

Usage:
    python mesh_annotator.py download [--year 2025]
    python mesh_annotator.py annotate --text "paper text..."
    python mesh_annotator.py validate --pmid 25516281
    python mesh_annotator.py search --query "breast cancer"
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

import networkx as nx
import requests

MESH_DIR = Path.home() / "datasets" / "unsorted" / "mesh"
MESH_DIR.mkdir(parents=True, exist_ok=True)

# Also check legacy path for backwards compatibility
_LEGACY_MESH_DIR = Path.home() / "datasets" / "ontologies" / "mesh"

MESH_XML_URL = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh"
PUBMED_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class MeSHTree:
    """Parse MeSH XML descriptors and build the poly-hierarchy.

    MeSH organizes ~30K descriptors into 16 categories (A-Z).
    Each descriptor has one or more tree numbers (e.g., C10.228.140.300)
    showing its position in the hierarchy.

    Attributes:
        dag: networkx DiGraph with tree-number nodes
        descriptors: dict of descriptor_ui → descriptor info
        name_to_ui: dict of lowercase name → descriptor_ui list
    """

    def __init__(self, xml_path: str | Path | None = None) -> None:
        self.dag = nx.DiGraph()
        self.descriptors: dict[str, dict[str, Any]] = {}
        self.name_to_ui: dict[str, list[str]] = defaultdict(list)
        self.synonym_to_ui: dict[str, list[str]] = defaultdict(list)
        self.tree_to_ui: dict[str, str] = {}
        self.ui_to_trees: dict[str, list[str]] = defaultdict(list)

        if xml_path:
            pickle_path = Path(str(xml_path) + ".pkl")
            if pickle_path.exists():
                import pickle

                print("Loading MeSH from pickle cache...")
                with open(pickle_path, "rb") as pf:
                    cached = pickle.load(pf)
                self.dag = cached["dag"]
                self.descriptors = cached["descriptors"]
                self.name_to_ui = cached["name_to_ui"]
                self.synonym_to_ui = cached["synonym_to_ui"]
                self.tree_to_ui = cached["tree_to_ui"]
                self.ui_to_trees = cached["ui_to_trees"]
                n_desc = len(self.descriptors)
                print(f"  Loaded {n_desc:,} descriptors (cached)")
            else:
                self.load_xml(xml_path)
                # Save pickle cache
                import pickle

                with open(pickle_path, "wb") as pf:
                    pickle.dump(
                        {
                            "dag": self.dag,
                            "descriptors": self.descriptors,
                            "name_to_ui": dict(self.name_to_ui),
                            "synonym_to_ui": dict(self.synonym_to_ui),
                            "tree_to_ui": self.tree_to_ui,
                            "ui_to_trees": dict(self.ui_to_trees),
                        },
                        pf,
                    )
                print(f"  Saved pickle cache to {pickle_path}")

    def load_xml(self, xml_path: str | Path) -> None:
        """Parse MeSH descriptor XML file."""
        xml_path = Path(xml_path)
        if not xml_path.exists():
            raise FileNotFoundError(f"MeSH XML not found: {xml_path}")

        print(f"Parsing MeSH XML from {xml_path}...")
        tree = ET.parse(xml_path)
        root = tree.getroot()

        count = 0
        for record in root.findall("DescriptorRecord"):
            ui_el = record.find("DescriptorUI")
            name_el = record.find("DescriptorName/String")
            if ui_el is None or name_el is None:
                continue

            ui = ui_el.text
            name = name_el.text
            count += 1

            # Scope note
            scope_el = record.find(".//ScopeNote")
            scope_note = scope_el.text.strip() if scope_el is not None and scope_el.text else ""

            # Tree numbers
            tree_numbers = []
            for tn_el in record.findall(".//TreeNumber"):
                if tn_el.text:
                    tree_numbers.append(tn_el.text)
                    self.tree_to_ui[tn_el.text] = ui
                    self.ui_to_trees[ui].append(tn_el.text)

            # Synonyms (entry terms)
            synonyms = []
            for concept in record.findall(".//Concept"):
                for term in concept.findall(".//Term"):
                    term_str = term.find("String")
                    if term_str is not None and term_str.text:
                        syn = term_str.text
                        if syn.lower() != name.lower():
                            synonyms.append(syn)
                        self.synonym_to_ui[syn.lower()].append(ui)

            # Semantic types
            sem_types = []
            for st_el in record.findall(".//SemanticType/SemanticTypeName"):
                if st_el.text:
                    sem_types.append(st_el.text)

            self.descriptors[ui] = {
                "ui": ui,
                "name": name,
                "tree_numbers": tree_numbers,
                "scope_note": scope_note[:200],
                "synonyms": synonyms[:10],
                "semantic_types": sem_types,
            }

            self.name_to_ui[name.lower()].append(ui)

        # Build DAG from tree numbers
        for tree_num, ui in self.tree_to_ui.items():
            self.dag.add_node(
                tree_num,
                ui=ui,
                name=self.descriptors[ui]["name"],
            )
            # Parent = everything up to last dot
            parts = tree_num.rsplit(".", 1)
            if len(parts) == 2:
                parent_tree = parts[0]
                self.dag.add_edge(tree_num, parent_tree)  # child → parent

        n_desc = len(self.descriptors)
        n_nodes = self.dag.number_of_nodes()
        n_edges = self.dag.number_of_edges()
        print(f"  Loaded {n_desc:,} descriptors, {n_nodes:,} tree nodes, {n_edges:,} edges")

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search MeSH descriptors by name or synonym."""
        query_lower = query.lower()
        results = []

        # Exact name match
        for ui in self.name_to_ui.get(query_lower, []):
            results.append({"ui": ui, "match": "exact", **self.descriptors[ui]})

        # Synonym match
        for ui in self.synonym_to_ui.get(query_lower, []):
            if not any(r["ui"] == ui for r in results):
                results.append({"ui": ui, "match": "synonym", **self.descriptors[ui]})

        # Partial name match
        if len(results) < limit:
            for name, uis in self.name_to_ui.items():
                if query_lower in name and name != query_lower:
                    for ui in uis:
                        if not any(r["ui"] == ui for r in results):
                            results.append(
                                {"ui": ui, "match": "partial", **self.descriptors[ui]}
                            )
                            if len(results) >= limit:
                                break

        return results[:limit]

    def match_text(self, text: str) -> dict[str, float]:
        """Match MeSH terms in text using word n-gram scanning."""
        text_lower = text.lower()
        words = re.findall(r"[a-z0-9'-]+", text_lower)
        matches: dict[str, float] = {}

        # Build n-grams from input text
        ngrams: set[str] = set()
        for n in range(1, min(9, len(words) + 1)):
            for i in range(len(words) - n + 1):
                ngrams.add(" ".join(words[i : i + n]))

        # Name matches
        for name, uis in self.name_to_ui.items():
            if len(name) < 4:
                continue
            if name in ngrams:
                for ui in uis:
                    matches[ui] = max(matches.get(ui, 0), 1.0)

        # Synonym matches
        for syn, uis in self.synonym_to_ui.items():
            if len(syn) < 4:
                continue
            if syn in ngrams:
                for ui in uis:
                    matches[ui] = max(matches.get(ui, 0), 0.8)

        return matches

    def propagate_mesh(
        self, direct_matches: dict[str, float], alpha: float = 0.7
    ) -> dict[str, float]:
        """Propagate MeSH annotations upward through the tree hierarchy.

        For each matched descriptor, propagate through ALL its tree positions
        upward to the root, with dampening factor alpha per level.
        """
        weights: dict[str, float] = {}

        for ui, weight in direct_matches.items():
            weights[ui] = max(weights.get(ui, 0), weight)

            # Propagate through each tree number
            for tree_num in self.ui_to_trees.get(ui, []):
                parts = tree_num.split(".")
                for i in range(len(parts) - 1, 0, -1):
                    parent_tree = ".".join(parts[:i])
                    parent_ui = self.tree_to_ui.get(parent_tree)
                    if parent_ui:
                        level_diff = len(parts) - i
                        propagated = weight * (alpha ** level_diff)
                        weights[parent_ui] = max(
                            weights.get(parent_ui, 0), propagated
                        )

        return weights

    def annotate(
        self,
        text: str,
        alpha: float = 0.7,
        threshold: float = 0.1,
        top_k: int | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Full MeSH annotation pipeline."""
        direct = self.match_text(text)
        if not direct:
            return {}

        propagated = self.propagate_mesh(direct, alpha=alpha)

        # Prune
        pruned = {
            ui: w for ui, w in propagated.items() if w >= threshold
        }
        if top_k and len(pruned) > top_k:
            sorted_items = sorted(pruned.items(), key=lambda x: x[1], reverse=True)
            pruned = dict(sorted_items[:top_k])

        # Enrich
        results: dict[str, dict[str, Any]] = {}
        for ui, weight in sorted(
            pruned.items(), key=lambda x: x[1], reverse=True
        ):
            desc = self.descriptors.get(ui, {})
            results[ui] = {
                "name": desc.get("name", ui),
                "weight": round(weight, 4),
                "tree_numbers": desc.get("tree_numbers", []),
                "is_direct": ui in direct,
                "semantic_types": desc.get("semantic_types", []),
            }

        return results


def download_mesh(year: int = 2025) -> Path:
    """Download MeSH descriptor XML from NLM."""
    desc_url = f"{MESH_XML_URL}/desc{year}.xml"
    out_path = MESH_DIR / f"desc{year}.xml"

    if out_path.exists():
        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"MeSH descriptors already downloaded: {out_path} ({size_mb:.0f} MB)")
        return out_path

    print(f"Downloading MeSH {year} descriptors from {desc_url}...")
    resp = requests.get(desc_url, stream=True, timeout=60)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r  {pct:.0f}% ({downloaded / 1024 / 1024:.0f} MB)", end="")

    print(f"\n  Saved to {out_path}")
    return out_path


def get_pubmed_mesh(pmid: str) -> list[str]:
    """Fetch MeSH terms assigned to a paper from PubMed."""
    url = f"{PUBMED_API}/efetch.fcgi"
    resp = requests.get(
        url,
        params={"db": "pubmed", "id": pmid, "rettype": "xml"},
        timeout=15,
    )
    if not resp.ok:
        return []

    root = ET.fromstring(resp.text)
    mesh_terms = []
    for mh in root.findall(".//MeshHeading/DescriptorName"):
        name = mh.text
        ui = mh.get("UI", "")
        if name:
            mesh_terms.append(f"{ui}:{name}")

    return mesh_terms


def validate_annotations(
    predicted: dict[str, dict[str, Any]],
    ground_truth: list[str],
) -> dict[str, float]:
    """Compare predicted MeSH annotations against PubMed ground truth.

    Returns precision, recall, F1 at various thresholds.
    """
    gt_uis = set()
    for term in ground_truth:
        if ":" in term:
            gt_uis.add(term.split(":")[0])

    pred_uis = set(predicted.keys())
    pred_direct = {
        ui for ui, info in predicted.items() if info.get("is_direct")
    }

    tp = len(pred_uis & gt_uis)
    fp = len(pred_uis - gt_uis)
    fn = len(gt_uis - pred_uis)

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-10)

    tp_direct = len(pred_direct & gt_uis)
    precision_direct = tp_direct / max(len(pred_direct), 1)
    recall_direct = tp_direct / max(len(gt_uis), 1)

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "precision_direct_only": round(precision_direct, 3),
        "recall_direct_only": round(recall_direct, 3),
        "predicted": len(pred_uis),
        "ground_truth": len(gt_uis),
        "true_positives": tp,
    }


# ── CLI ──────────────────────────────────────────────────────────────


def cmd_download(args: list[str]) -> int:
    """Download MeSH data."""
    import argparse

    parser = argparse.ArgumentParser(description="Download MeSH")
    parser.add_argument("--year", type=int, default=2025, help="MeSH year")
    parsed = parser.parse_args(args)

    path = download_mesh(parsed.year)
    print(f"\n✅ MeSH {parsed.year} ready at {path}")
    return 0


def cmd_annotate(args: list[str]) -> int:
    """Annotate text with MeSH terms."""
    import argparse

    parser = argparse.ArgumentParser(description="Annotate with MeSH")
    parser.add_argument("--text", "-t", help="Text to annotate")
    parser.add_argument("--file", "-f", help="File containing text")
    parser.add_argument("--year", type=int, default=2025, help="MeSH year")
    parser.add_argument("--alpha", type=float, default=0.7)
    parser.add_argument("--threshold", type=float, default=0.1)
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--output", help="Output JSON path")
    parsed = parser.parse_args(args)

    text = parsed.text
    if parsed.file:
        text = Path(parsed.file).read_text()
    if not text:
        print("Error: provide --text or --file")
        return 1

    xml_path = MESH_DIR / f"desc{parsed.year}.xml"
    if not xml_path.exists():
        download_mesh(parsed.year)

    mesh = MeSHTree(xml_path)
    results = mesh.annotate(
        text, alpha=parsed.alpha, threshold=parsed.threshold, top_k=parsed.top_k
    )

    print(f"\n{'UI':<12} {'Name':<40} {'Weight':>8} {'Direct':>7} {'Trees':>6}")
    print("-" * 78)
    for ui, info in results.items():
        direct = "✓" if info["is_direct"] else ""
        n_trees = len(info.get("tree_numbers", []))
        print(
            f"{ui:<12} {info['name'][:39]:<40} "
            f"{info['weight']:>8.4f} {direct:>7} {n_trees:>6}"
        )
    print(f"\nTotal: {len(results)} MeSH annotations")

    if parsed.output:
        with open(parsed.output, "w") as f:
            json.dump(results, f, indent=2)

    return 0


def cmd_validate(args: list[str]) -> int:
    """Validate MeSH annotation predictions against PubMed ground truth."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate MeSH annotations")
    parser.add_argument("--pmid", required=True, help="PubMed ID")
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--alpha", type=float, default=0.7)
    parser.add_argument("--threshold", type=float, default=0.05)
    parsed = parser.parse_args(args)

    # Get abstract from PubMed
    url = f"{PUBMED_API}/efetch.fcgi"
    resp = requests.get(
        url,
        params={"db": "pubmed", "id": parsed.pmid, "rettype": "xml"},
        timeout=15,
    )
    root = ET.fromstring(resp.text)
    abstract_el = root.find(".//AbstractText")
    title_el = root.find(".//ArticleTitle")
    abstract = abstract_el.text if abstract_el is not None and abstract_el.text else ""
    title = title_el.text if title_el is not None and title_el.text else ""
    text = f"{title} {abstract}"

    # Ground truth MeSH
    gt = get_pubmed_mesh(parsed.pmid)
    print(f"PubMed MeSH for PMID:{parsed.pmid}: {len(gt)} terms")
    for term in gt:
        print(f"  {term}")

    # Predict
    xml_path = MESH_DIR / f"desc{parsed.year}.xml"
    if not xml_path.exists():
        download_mesh(parsed.year)

    mesh = MeSHTree(xml_path)
    predicted = mesh.annotate(text, alpha=parsed.alpha, threshold=parsed.threshold)

    print(f"\nPredicted: {len(predicted)} terms")
    for ui, info in list(predicted.items())[:15]:
        direct = "✓" if info["is_direct"] else ""
        print(f"  {ui:<12} {info['name'][:40]:<40} {info['weight']:>6.3f} {direct}")

    # Validate
    metrics = validate_annotations(predicted, gt)
    print("\nValidation:")
    print(f"  Precision: {metrics['precision']:.1%}")
    print(f"  Recall:    {metrics['recall']:.1%}")
    print(f"  F1:        {metrics['f1']:.1%}")
    print(f"  TP/GT:     {metrics['true_positives']}/{metrics['ground_truth']}")

    return 0


def cmd_search(args: list[str]) -> int:
    """Search MeSH descriptors."""
    import argparse

    parser = argparse.ArgumentParser(description="Search MeSH")
    parser.add_argument("--query", "-q", required=True)
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--limit", type=int, default=10)
    parsed = parser.parse_args(args)

    xml_path = MESH_DIR / f"desc{parsed.year}.xml"
    if not xml_path.exists():
        download_mesh(parsed.year)

    mesh = MeSHTree(xml_path)
    results = mesh.search(parsed.query, limit=parsed.limit)

    for r in results:
        trees = ", ".join(r.get("tree_numbers", [])[:3])
        print(f"  {r['ui']:<12} {r['name']:<40} [{r['match']}] {trees}")

    return 0


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mesh_annotator.py <command> [args]")
        print("Commands: download, annotate, validate, search")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "download": cmd_download,
        "annotate": cmd_annotate,
        "validate": cmd_validate,
        "search": cmd_search,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        return 1

    return commands[command](args)


if __name__ == "__main__":
    sys.exit(main())
