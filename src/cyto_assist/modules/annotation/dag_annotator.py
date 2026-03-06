#!/usr/bin/env python3
"""Hierarchical DAG Annotation — Probabilistic ontology annotation using DAG structure.

Uses the directed acyclic graph (DAG) structure of biomedical ontologies to infer
weighted term associations for papers. Direct term matches propagate upward through
ancestor nodes with dampening, weighted by Information Content (IC).

Supports any OBO-format ontology (MONDO, GO, CL, HP, etc.) and MeSH tree structures.

Usage:
    python dag_annotator.py annotate --ontology mondo --text "paper text..."
    python dag_annotator.py ic-stats --ontology go
    python dag_annotator.py compare --ontology mondo --text "..." --ground-truth terms.json
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import networkx as nx
import obonet

CACHE_DIR = Path.home() / ".cache" / "cytognosis" / "dag_annotator"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Default ontology paths (OBO format)
ONTOLOGY_SOURCES: dict[str, str] = {
    "mondo": "http://purl.obolibrary.org/obo/mondo.obo",
    "go": "http://purl.obolibrary.org/obo/go.obo",
    "cl": "http://purl.obolibrary.org/obo/cl.obo",
    "hp": "http://purl.obolibrary.org/obo/hp.obo",
    "doid": "http://purl.obolibrary.org/obo/doid.obo",
    "chebi": "http://purl.obolibrary.org/obo/chebi.obo",
    "uberon": "http://purl.obolibrary.org/obo/uberon.obo",
}


class OntologyDAG:
    """Load an OBO ontology and represent it as a networkx DAG.

    Nodes are ontology term IDs (e.g., 'MONDO:0005090').
    Edges go child → parent (is_a relationships).
    Each node stores: name, synonyms, definition, depth, namespace.
    """

    def __init__(self, ontology_id: str, obo_path: str | None = None) -> None:
        self.ontology_id = ontology_id
        self.dag = nx.DiGraph()
        self.name_to_ids: dict[str, list[str]] = defaultdict(list)
        self.synonym_to_ids: dict[str, list[str]] = defaultdict(list)
        self._ic: dict[str, float] = {}
        self._depths: dict[str, int] = {}

        source = obo_path or ONTOLOGY_SOURCES.get(ontology_id)
        if not source:
            raise ValueError(
                f"Unknown ontology '{ontology_id}'. "
                f"Available: {list(ONTOLOGY_SOURCES.keys())}"
            )

        cache_path = CACHE_DIR / f"{ontology_id}.obo"
        pickle_path = CACHE_DIR / f"{ontology_id}_dag.pkl"

        # Fast path: load pre-built DAG from pickle
        if pickle_path.exists():
            import pickle

            print(f"Loading {ontology_id} from pickle cache...")
            with open(pickle_path, "rb") as pf:
                cached = pickle.load(pf)
            self.dag = cached["dag"]
            self.name_to_ids = cached["name_to_ids"]
            self.synonym_to_ids = cached["synonym_to_ids"]
            self._depths = cached.get("depths", {})
            self._ic = cached.get("ic", {})
            if not self._depths:
                self._compute_depths()
            n_nodes = self.dag.number_of_nodes()
            n_edges = self.dag.number_of_edges()
            print(f"  Loaded {n_nodes:,} terms, {n_edges:,} edges (cached)")
            return

        if cache_path.exists():
            source = str(cache_path)

        print(f"Loading {ontology_id} from {source} (obonet)...")
        obo_graph = obonet.read_obo(source)

        # obonet builds a MultiDiGraph with edges parent→child (is_a)
        # We build our own DiGraph with child→parent edges for propagation
        for node_id, data in obo_graph.nodes(data=True):
            name = data.get("name", "")
            definition = data.get("def", "")
            namespace = data.get("namespace", "")
            is_obsolete = data.get("is_obsolete", "false") == "true"

            synonyms: list[str] = []
            raw_syns = data.get("synonym", [])
            if isinstance(raw_syns, str):
                raw_syns = [raw_syns]
            for syn_str in raw_syns:
                # Parse synonym format: "text" SCOPE [xrefs]
                m = re.match(r'"([^"]+)"', syn_str)
                if m:
                    syn_text = m.group(1)
                    synonyms.append(syn_text)
                    self.synonym_to_ids[syn_text.lower()].append(node_id)

            self.dag.add_node(
                node_id,
                name=name,
                definition=definition,
                namespace=namespace,
                synonyms=synonyms,
                obsolete=is_obsolete,
            )

            if name:
                self.name_to_ids[name.lower()].append(node_id)

        # Add child→parent edges from obonet's parent→child edges
        for child, parent, _key in obo_graph.edges(keys=True):
            if child in self.dag and parent in self.dag:
                self.dag.add_edge(child, parent)

        # Cache OBO locally if fetched from remote
        if not cache_path.exists() and source.startswith("http"):
            try:
                import urllib.request

                urllib.request.urlretrieve(source, cache_path)
            except Exception:
                pass

        # Save pickle cache for fast subsequent loads
        import pickle

        self._compute_depths()
        with open(pickle_path, "wb") as pf:
            pickle.dump(
                {
                    "dag": self.dag,
                    "name_to_ids": dict(self.name_to_ids),
                    "synonym_to_ids": dict(self.synonym_to_ids),
                    "depths": self._depths,
                },
                pf,
            )
        print(f"  Saved pickle cache to {pickle_path}")

        n_nodes = self.dag.number_of_nodes()
        n_edges = self.dag.number_of_edges()
        print(f"  Loaded {n_nodes:,} terms, {n_edges:,} edges")

    def _compute_depths(self) -> None:
        """Compute depth of each node (distance from root)."""
        roots = [n for n in self.dag.nodes() if self.dag.out_degree(n) == 0]
        for root in roots:
            for node, depth in nx.single_source_shortest_path_length(
                self.dag.reverse(), root
            ).items():
                if node not in self._depths or depth < self._depths[node]:
                    self._depths[node] = depth

    def depth(self, term_id: str) -> int:
        """Get depth of a term (0 = root)."""
        return self._depths.get(term_id, 0)

    def max_depth(self) -> int:
        """Maximum depth in the DAG."""
        return max(self._depths.values()) if self._depths else 0

    def ancestors(self, term_id: str) -> set[str]:
        """Get all ancestor term IDs (parents, grandparents, ...)."""
        if term_id not in self.dag:
            return set()
        return set(nx.descendants(self.dag, term_id))  # edges go child→parent

    def children(self, term_id: str) -> set[str]:
        """Get direct children of a term."""
        if term_id not in self.dag:
            return set()
        return set(nx.predecessors(self.dag, term_id))  # edges go child→parent

    def term_name(self, term_id: str) -> str:
        """Get the name of a term."""
        data = self.dag.nodes.get(term_id, {})
        return data.get("name", term_id)

    def match_text(self, text: str) -> dict[str, float]:
        """Find ontology terms mentioned in text (word n-gram scanning).

        Returns dict of term_id → confidence (1.0 for exact name match,
        0.8 for synonym match).
        """
        text_lower = text.lower()
        words = re.findall(r"[a-z0-9'-]+", text_lower)
        matches: dict[str, float] = {}

        # Build all n-grams (1 to 8 words) from the input text
        ngrams: set[str] = set()
        for n in range(1, min(9, len(words) + 1)):
            for i in range(len(words) - n + 1):
                ngrams.add(" ".join(words[i : i + n]))

        # Check names against n-grams (O(vocab) but simple set lookup)
        for name, term_ids in self.name_to_ids.items():
            if len(name) < 4:
                continue
            if name in ngrams:
                for tid in term_ids:
                    if not self.dag.nodes[tid].get("obsolete", False):
                        matches[tid] = max(matches.get(tid, 0), 1.0)

        # Check synonyms
        for syn, term_ids in self.synonym_to_ids.items():
            if len(syn) < 4:
                continue
            if syn in ngrams:
                for tid in term_ids:
                    if not self.dag.nodes[tid].get("obsolete", False):
                        matches[tid] = max(matches.get(tid, 0), 0.8)

        return matches


def propagate_annotations(
    direct_matches: dict[str, float],
    dag: OntologyDAG,
    alpha: float = 0.7,
) -> dict[str, float]:
    """Propagate annotations upward through the DAG with dampening.

    For each directly matched term, all ancestors receive a propagated
    weight that decays by factor `alpha` per edge traversed upward.

    Args:
        direct_matches: term_id → confidence from NER/text matching
        dag: OntologyDAG instance
        alpha: dampening factor per edge (0.7 = 30% decay per level)

    Returns:
        Dict of term_id → propagated weight in [0, 1]
    """
    weights: dict[str, float] = dict(direct_matches)

    for term_id, weight in direct_matches.items():
        if term_id not in dag.dag:
            continue

        # BFS upward through ancestors
        visited = set()
        queue = [(term_id, weight)]

        while queue:
            current, current_weight = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            # Propagate to parents
            for parent in dag.dag.successors(current):  # child→parent edges
                propagated = current_weight * alpha
                if propagated > weights.get(parent, 0):
                    weights[parent] = propagated
                    queue.append((parent, propagated))

    return weights


def compute_information_content(
    dag: OntologyDAG,
    corpus_counts: dict[str, int] | None = None,
) -> dict[str, float]:
    """Compute Information Content for each term.

    IC(t) = -log2(P(t)) where P(t) = freq(t) / max_freq
    If no corpus_counts provided, uses structural IC based on
    number of descendants (more descendants = less specific = lower IC).

    Args:
        dag: OntologyDAG instance
        corpus_counts: Optional term_id → frequency in corpus

    Returns:
        Dict of term_id → IC value (higher = more specific/informative)
    """
    ic: dict[str, float] = {}

    if corpus_counts:
        max_count = max(corpus_counts.values()) if corpus_counts else 1
        for term_id in dag.dag.nodes():
            count = corpus_counts.get(term_id, 0)
            # Add ancestors' counts (true path rule)
            for anc in dag.ancestors(term_id):
                count += corpus_counts.get(anc, 0)
            prob = max((count + 1) / (max_count + 1), 1e-10)
            ic[term_id] = -math.log2(prob)
    else:
        # Depth-based IC: deeper terms are more specific
        # Uses precomputed depths instead of expensive BFS per node
        max_d = dag.max_depth() or 1
        for term_id in dag.dag.nodes():
            d = dag.depth(term_id)
            # Deeper = more specific = higher IC
            prob = max(1.0 - (d / (max_d + 1)), 1e-10)
            ic[term_id] = -math.log2(prob)

    dag._ic = ic
    return ic


def weight_by_ic(
    annotations: dict[str, float],
    ic: dict[str, float],
    max_ic: float | None = None,
) -> dict[str, float]:
    """Re-weight annotations by Information Content.

    Multiplies annotation weight by normalized IC, so more specific
    terms get higher final scores.
    """
    if not ic:
        return annotations

    if max_ic is None:
        max_ic = max(ic.values()) if ic else 1.0

    weighted: dict[str, float] = {}
    for term_id, weight in annotations.items():
        term_ic = ic.get(term_id, max_ic * 0.5)
        ic_factor = term_ic / max_ic  # normalize to [0, 1]
        weighted[term_id] = weight * ic_factor

    return weighted


def prune_annotations(
    annotations: dict[str, float],
    threshold: float = 0.1,
    top_k: int | None = None,
) -> dict[str, float]:
    """Prune low-weight annotations.

    Args:
        annotations: term_id → weight
        threshold: minimum weight to keep
        top_k: if set, keep only top-k annotations

    Returns:
        Pruned annotation dict
    """
    pruned = {
        tid: w for tid, w in annotations.items() if w >= threshold
    }

    if top_k and len(pruned) > top_k:
        sorted_items = sorted(pruned.items(), key=lambda x: x[1], reverse=True)
        pruned = dict(sorted_items[:top_k])

    return pruned


def annotate_text(
    text: str,
    dag: OntologyDAG,
    alpha: float = 0.7,
    threshold: float = 0.1,
    top_k: int | None = None,
    use_ic: bool = True,
) -> dict[str, dict[str, Any]]:
    """Full annotation pipeline: text → match → propagate → IC weight → prune.

    Args:
        text: Input text (abstract + title, or full paper)
        dag: OntologyDAG instance
        alpha: DAG propagation dampening factor
        threshold: Minimum weight after pruning
        top_k: Maximum annotations to return
        use_ic: Whether to weight by Information Content

    Returns:
        Dict of term_id → {name, weight, depth, is_direct, namespace}
    """
    # Step 1: Direct text matching
    direct = dag.match_text(text)

    if not direct:
        return {}

    # Step 2: DAG propagation
    propagated = propagate_annotations(direct, dag, alpha=alpha)

    # Step 3: IC weighting
    if use_ic:
        if not dag._ic:
            compute_information_content(dag)
        propagated = weight_by_ic(propagated, dag._ic)

    # Step 4: Pruning
    pruned = prune_annotations(propagated, threshold=threshold, top_k=top_k)

    # Step 5: Enrich with metadata
    results: dict[str, dict[str, Any]] = {}
    for term_id, weight in sorted(
        pruned.items(), key=lambda x: x[1], reverse=True
    ):
        results[term_id] = {
            "name": dag.term_name(term_id),
            "weight": round(weight, 4),
            "depth": dag.depth(term_id),
            "is_direct": term_id in direct,
            "namespace": dag.dag.nodes[term_id].get("namespace", ""),
        }

    return results


def annotate_paper_from_neo4j(
    pmid: str,
    dag: OntologyDAG,
    driver: Any,
    alpha: float = 0.7,
    threshold: float = 0.1,
) -> dict[str, dict[str, Any]]:
    """Annotate a paper from Neo4j PKG using its title + bio-entities.

    Args:
        pmid: PubMed ID
        dag: OntologyDAG instance
        driver: neo4j.GraphDatabase driver
        alpha: DAG propagation dampening
        threshold: Pruning threshold

    Returns:
        Enriched annotation dict
    """
    # Get paper title
    r, _, _ = driver.execute_query(
        "MATCH (p:Paper {pmid: $pmid}) RETURN p.title AS title",
        pmid=pmid,
    )
    title = r[0]["title"] if r else ""

    # Get mentioned bio-entities
    r, _, _ = driver.execute_query(
        "MATCH (p:Paper {pmid: $pmid})-[:MENTIONS]->(b:BioEntity) "
        "RETURN b.name AS name, b.entityType AS type",
        pmid=pmid,
    )
    entity_text = " ".join(rec["name"] for rec in r)

    combined_text = f"{title} {entity_text}"
    return annotate_text(
        combined_text, dag, alpha=alpha, threshold=threshold
    )


# ── CLI ──────────────────────────────────────────────────────────────


def cmd_annotate(args: list[str]) -> int:
    """Annotate text with ontology terms."""
    import argparse

    parser = argparse.ArgumentParser(description="Annotate text with ontology terms")
    parser.add_argument("--ontology", "-o", required=True, help="Ontology ID")
    parser.add_argument("--text", "-t", help="Text to annotate")
    parser.add_argument("--file", "-f", help="File containing text")
    parser.add_argument("--alpha", type=float, default=0.7, help="Propagation factor")
    parser.add_argument("--threshold", type=float, default=0.1, help="Prune threshold")
    parser.add_argument("--top-k", type=int, default=None, help="Max annotations")
    parser.add_argument("--no-ic", action="store_true", help="Skip IC weighting")
    parser.add_argument("--output", help="Output JSON path")
    parsed = parser.parse_args(args)

    text = parsed.text
    if parsed.file:
        text = Path(parsed.file).read_text()
    if not text:
        print("Error: provide --text or --file")
        return 1

    dag = OntologyDAG(parsed.ontology)
    results = annotate_text(
        text,
        dag,
        alpha=parsed.alpha,
        threshold=parsed.threshold,
        top_k=parsed.top_k,
        use_ic=not parsed.no_ic,
    )

    print(f"\n{'Term ID':<20} {'Name':<40} {'Weight':>8} {'Depth':>6} {'Direct':>7}")
    print("-" * 85)
    for tid, info in results.items():
        direct = "✓" if info["is_direct"] else ""
        print(
            f"{tid:<20} {info['name'][:39]:<40} {info['weight']:>8.4f} "
            f"{info['depth']:>6} {direct:>7}"
        )
    print(f"\nTotal: {len(results)} annotations")

    if parsed.output:
        with open(parsed.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved to {parsed.output}")

    return 0


def cmd_ic_stats(args: list[str]) -> int:
    """Show Information Content statistics for an ontology."""
    import argparse

    parser = argparse.ArgumentParser(description="IC statistics")
    parser.add_argument("--ontology", "-o", required=True, help="Ontology ID")
    parsed = parser.parse_args(args)

    dag = OntologyDAG(parsed.ontology)
    ic = compute_information_content(dag)

    sorted_ic = sorted(ic.items(), key=lambda x: x[1], reverse=True)

    print(f"\nIC Statistics for {parsed.ontology}")
    print(f"  Terms: {len(ic):,}")
    print(f"  Max IC: {max(ic.values()):.2f}")
    print(f"  Min IC: {min(ic.values()):.2f}")
    print(f"  Mean IC: {sum(ic.values()) / len(ic):.2f}")

    print("\nTop 10 most specific (highest IC):")
    for tid, val in sorted_ic[:10]:
        print(f"  {tid:<20} {dag.term_name(tid)[:40]:<40} IC={val:.2f}")

    print("\nTop 10 most general (lowest IC):")
    for tid, val in sorted_ic[-10:]:
        print(f"  {tid:<20} {dag.term_name(tid)[:40]:<40} IC={val:.2f}")

    return 0


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: dag_annotator.py <command> [args]")
        print("Commands: annotate, ic-stats")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "annotate": cmd_annotate,
        "ic-stats": cmd_ic_stats,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands)}")
        return 1

    return commands[command](args)


if __name__ == "__main__":
    sys.exit(main())
