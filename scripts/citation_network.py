#!/usr/bin/env python3
"""Citation Network Builder — Build 1-hop citation networks for papers.

Uses PKG data to build citation subgraphs around papers of interest,
then exports as NetworkX graphs for analysis.

Usage:
    python citation_network.py build PMID [PMID2 ...]  # Build 1-hop network
    python citation_network.py stats PMID               # Citation stats
    python citation_network.py export PMID              # Export as GraphML
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import networkx as nx

PKG_DIR = Path("/home/mohammadi/datasets/network/public/kg/PMK")


def _tsv(name: str) -> str:
    """DuckDB read expression for PKG file."""
    files = {
        "papers": "C01_Papers.tsv",
        "citations": "C04_ReferenceList_Papers.tsv.gz",
        "paper_entities": "C06_Link_Papers_BioEntities.tsv.gz",
    }
    path = PKG_DIR / files[name]
    return (
        f"read_csv_auto('{path}', delim='\\t', header=true,"
        f" quote='', strict_mode=false, nullstr='NULL', all_varchar=true)"
    )


def build_citation_network(
    pmids: list[str],
    max_hops: int = 1,
) -> nx.DiGraph:
    """Build a citation network around seed PMIDs.

    Args:
        pmids: Seed paper PMIDs
        max_hops: Number of citation hops (1 = direct citations)

    Returns:
        NetworkX directed graph with citation edges
    """
    con = duckdb.connect(":memory:")
    con.execute("SET memory_limit = '4GB'")
    con.execute("SET threads = 8")

    G = nx.DiGraph()

    # Get seed paper metadata
    pmid_list = ",".join(f"'{p}'" for p in pmids)
    papers = con.execute(f"""
        SELECT PMID, ArticleTitle, PubYear, CitedCount
        FROM {_tsv('papers')}
        WHERE PMID IN ({pmid_list})
    """).fetchall()

    for p in papers:
        G.add_node(p[0], title=str(p[1])[:100], year=p[2],
                   cited_count=p[3], is_seed=True)

    current_pmids = set(pmids)
    all_pmids = set(pmids)

    for hop in range(max_hops):
        pmid_list = ",".join(f"'{p}'" for p in current_pmids)

        # Outgoing citations (papers cited BY seed papers)
        cited = con.execute(f"""
            SELECT PMID, RefPMID
            FROM {_tsv('citations')}
            WHERE PMID IN ({pmid_list})
        """).fetchall()

        # Incoming citations (papers that CITE seed papers)
        citing = con.execute(f"""
            SELECT PMID, RefPMID
            FROM {_tsv('citations')}
            WHERE RefPMID IN ({pmid_list})
        """).fetchall()

        new_pmids = set()
        for citer, cited_pmid in cited:
            G.add_edge(citer, cited_pmid, type="cites")
            new_pmids.add(cited_pmid)

        for citer, cited_pmid in citing:
            G.add_edge(citer, cited_pmid, type="cites")
            new_pmids.add(citer)

        # Get metadata for new nodes
        new_pmids -= all_pmids
        if new_pmids:
            new_list = ",".join(f"'{p}'" for p in list(new_pmids)[:10000])
            meta = con.execute(f"""
                SELECT PMID, ArticleTitle, PubYear, CitedCount
                FROM {_tsv('papers')}
                WHERE PMID IN ({new_list})
            """).fetchall()
            for p in meta:
                if p[0] not in G:
                    G.add_node(p[0], title=str(p[1])[:100], year=p[2],
                             cited_count=p[3], is_seed=False)

        current_pmids = new_pmids
        all_pmids |= new_pmids
        print(f"  Hop {hop+1}: +{len(new_pmids):,} papers, "
              f"total {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    con.close()
    return G


def cmd_build(pmids: list[str]) -> None:
    """Build and display citation network."""
    print(f"Building 1-hop citation network for {len(pmids)} seed papers...")
    G = build_citation_network(pmids)

    print("\nNetwork Summary:")
    print(f"  Nodes: {G.number_of_nodes():,}")
    print(f"  Edges: {G.number_of_edges():,}")

    # Top cited neighbors
    seed_pmids = {n for n, d in G.nodes(data=True) if d.get("is_seed")}
    neighbors = [(n, d) for n, d in G.nodes(data=True) if not d.get("is_seed")]
    neighbors.sort(key=lambda x: int(x[1].get("cited_count") or 0), reverse=True)

    print("\nTop 10 most-cited neighbors:")
    for n, d in neighbors[:10]:
        print(f"  PMID:{n} cited={d.get('cited_count', '?'):>8} | "
              f"{d.get('title', 'N/A')[:60]}")

    # Save graph
    out = Path(f"/tmp/citation_network_{'_'.join(pmids[:3])}.graphml")
    nx.write_graphml(G, str(out))
    print(f"\n✅ Saved to {out}")


def cmd_stats(pmid: str) -> None:
    """Get citation statistics for a paper."""
    con = duckdb.connect(":memory:")
    con.execute("SET memory_limit = '4GB'")

    # Outgoing
    out_count = con.execute(f"""
        SELECT count(*) FROM {_tsv('citations')}
        WHERE PMID = '{pmid}'
    """).fetchone()[0]

    # Incoming
    in_count = con.execute(f"""
        SELECT count(*) FROM {_tsv('citations')}
        WHERE RefPMID = '{pmid}'
    """).fetchone()[0]

    # Paper metadata
    meta = con.execute(f"""
        SELECT PMID, ArticleTitle, PubYear, CitedCount
        FROM {_tsv('papers')} WHERE PMID = '{pmid}'
    """).fetchone()

    if meta:
        print(f"PMID: {meta[0]}")
        print(f"Title: {meta[1]}")
        print(f"Year: {meta[2]}")
        print(f"PKG CitedCount: {meta[3]}")
    print(f"References (outgoing): {out_count:,}")
    print(f"Cited by (incoming): {in_count:,}")

    con.close()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    cmd = sys.argv[1]
    if cmd == "build":
        if len(sys.argv) < 3:
            print("Usage: citation_network.py build PMID [PMID2 ...]")
            return 1
        cmd_build(sys.argv[2:])
    elif cmd == "stats":
        if len(sys.argv) < 3:
            return 1
        cmd_stats(sys.argv[2])
    elif cmd == "export":
        cmd_build(sys.argv[2:])
    else:
        print(f"Unknown: {cmd}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
