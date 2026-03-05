#!/usr/bin/env python3
"""PKG 2.0 Explorer — DuckDB-based analysis of PubMed Knowledge Graph data.

Uses DuckDB for memory-efficient querying of the ~50GB PKG dataset without
loading everything into memory. Also generates statistics and prepares data
for Neo4j import.

Usage:
    python pkg_explorer.py stats      # Print dataset statistics
    python pkg_explorer.py entities   # Analyze bio-entity distribution
    python pkg_explorer.py sample     # Sample papers with rich annotations
    python pkg_explorer.py prepare    # Prepare CSV files for neo4j-admin import
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

# ── Configuration ────────────────────────────────────────────────────────────

PKG_DIR = Path("/home/mohammadi/datasets/network/public/kg/PMK")

# File mappings
FILES = {
    "papers": PKG_DIR / "C01_Papers.tsv",
    "paper_authors": PKG_DIR / "C02_Link_Papers_Authors.tsv",
    "affiliations": PKG_DIR / "C03_Affiliations.tsv.gz",
    "citations": PKG_DIR / "C04_ReferenceList_Papers.tsv.gz",
    "pis": PKG_DIR / "C05_PIs.tsv",
    "paper_entities": PKG_DIR / "C06_Link_Papers_BioEntities.tsv.gz",
    "authors": PKG_DIR / "C07_Authors.tsv",
    "paper_journals": PKG_DIR / "C10_Link_Papers_Journals.tsv",
    "trials": PKG_DIR / "C11_ClinicalTrials.tsv",
    "paper_trials": PKG_DIR / "C12_Link_Papers_Clinicaltrials.tsv",
    "trial_entities": PKG_DIR / "C13_Link_ClinicalTrials_BioEntities.tsv",
    "investigators": PKG_DIR / "C14_Investigators.tsv",
    "patents": PKG_DIR / "C15_Patents.tsv",
    "patent_papers": PKG_DIR / "C16_Link_Patents_Papers.tsv",
    "assignees": PKG_DIR / "C17_Assignees.tsv",
    "patent_entities": PKG_DIR / "C18_Link_Patents_BioEntities.tsv",
    "inventors": PKG_DIR / "C19_Inventors.tsv",
    "entity_relations": PKG_DIR / "C21_Bioentity_Relationships.tsv",
    "datasets_methods": PKG_DIR / "C22_DatasetMethod.tsv",
    "entities": PKG_DIR / "C23_BioEntities.tsv",
    "trial_patents": PKG_DIR / "C24_Link_Clinicaltrials_Patents.tsv",
}


def _read_tsv(con: duckdb.DuckDBPyConnection, name: str) -> str:
    """Return DuckDB SQL to read a TSV file (handles .gz transparently)."""
    path = str(FILES[name])
    return f"read_csv_auto('{path}', delim='\\t', header=true, sample_size=10000, quote='', strict_mode=false, nullstr='NULL', all_varchar=true)"


def cmd_stats(con: duckdb.DuckDBPyConnection) -> None:
    """Print comprehensive statistics for each file."""
    print("=" * 80)
    print("PubMed Knowledge Graph 2.0 — Dataset Statistics")
    print("=" * 80)

    for name, path in FILES.items():
        if not path.exists():
            print(f"\n⚠️  {name}: FILE NOT FOUND ({path})")
            continue
        try:
            result = con.execute(
                f"SELECT count(*) AS cnt FROM {_read_tsv(con, name)}"
            ).fetchone()
            row_count = result[0] if result else 0
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"\n📊 {name} ({path.name})")
            print(f"   Rows: {row_count:>15,}")
            print(f"   Size: {size_mb:>12,.1f} MB")

            # Show columns
            cols = con.execute(
                f"SELECT * FROM {_read_tsv(con, name)} LIMIT 0"
            ).description
            col_names = [c[0] for c in cols]
            print(f"   Columns ({len(col_names)}): {', '.join(col_names[:10])}")
            if len(col_names) > 10:
                print(f"            + {len(col_names) - 10} more")
        except Exception as e:
            print(f"\n❌ {name}: {e}")


def cmd_entities(con: duckdb.DuckDBPyConnection) -> None:
    """Analyze bio-entity distribution."""
    print("=" * 80)
    print("Bio-Entity Distribution")
    print("=" * 80)

    # Entity types
    result = con.execute(f"""
        SELECT Type, count(*) AS cnt
        FROM {_read_tsv(con, 'entities')}
        GROUP BY Type ORDER BY cnt DESC
    """).fetchall()

    print(f"\n{'Type':<20} {'Count':>12}")
    print("-" * 34)
    for row in result:
        print(f"{row[0]:<20} {row[1]:>12,}")

    # Top entities per type
    for entity_type in ("disease", "gene", "drug"):
        print(f"\n--- Top 10 {entity_type} entities ---")
        result = con.execute(f"""
            SELECT EntityId, Mention, count(*) OVER () AS total
            FROM {_read_tsv(con, 'entities')}
            WHERE LOWER(Type) = '{entity_type}'
            LIMIT 10
        """).fetchall()
        for row in result:
            print(f"  {row[0]}: {row[1]}")


def cmd_sample(con: duckdb.DuckDBPyConnection) -> None:
    """Sample highly-cited papers with their entities."""
    print("=" * 80)
    print("Top 20 Most-Cited Papers with Bio-Entities")
    print("=" * 80)

    result = con.execute(f"""
        SELECT p.PMID, p.ArticleTitle, p.PubYear, p.CitedCount
        FROM {_read_tsv(con, 'papers')} p
        WHERE p.CitedCount IS NOT NULL
        ORDER BY CAST(p.CitedCount AS INTEGER) DESC
        LIMIT 20
    """).fetchall()

    for row in result:
        pmid, title, year, cited = row
        print(f"\n  PMID: {pmid} | Year: {year} | Cited: {cited}")
        title_str = str(title)[:100] if title else "N/A"
        print(f"  Title: {title_str}")


def cmd_compare_template(con: duckdb.DuckDBPyConnection) -> None:
    """Compare PKG paper fields with our paper template."""
    print("=" * 80)
    print("PKG Paper Fields vs Our Paper Template")
    print("=" * 80)

    # PKG paper fields
    cols = con.execute(
        f"SELECT * FROM {_read_tsv(con, 'papers')} LIMIT 0"
    ).description
    pkg_fields = {c[0] for c in cols}

    # Our template fields (from _template.yml)
    template_fields = {
        "pmid", "doi", "title", "authors", "journal", "year",
        "abstract", "keywords", "mesh_terms", "cited_by",
        "references", "affiliations", "funding",
        "study_type", "clinical_trial_id",
    }

    print("\n📋 PKG Paper Fields:")
    for f in sorted(pkg_fields):
        mapped = "✅" if f.lower() in {x.lower() for x in template_fields} else "  "
        print(f"  {mapped} {f}")

    print("\n📋 Template Fields NOT in PKG Papers:")
    pkg_lower = {f.lower() for f in pkg_fields}
    for f in sorted(template_fields):
        if f.lower() not in pkg_lower:
            # Check if available in other PKG tables
            tables_with_field = []
            if f in ("authors",):
                tables_with_field.append("C02/C07")
            elif f in ("doi",):
                tables_with_field.append("Not in PKG — use PubMed API")
            elif f in ("abstract",):
                tables_with_field.append("Not in PKG files (in PubMed XML)")
            elif f in ("journal",):
                tables_with_field.append("C10_Journals")
            elif f in ("keywords", "mesh_terms"):
                tables_with_field.append("C06_BioEntities (via NER)")
            elif f in ("references",):
                tables_with_field.append("C04_ReferenceList")
            elif f in ("affiliations",):
                tables_with_field.append("C03_Affiliations")
            elif f in ("funding",):
                tables_with_field.append("C05_PIs")
            elif f in ("clinical_trial_id",):
                tables_with_field.append("C12_Link_Papers_Clinicaltrials")
            source = f" (→ {', '.join(tables_with_field)})" if tables_with_field else ""
            print(f"  ⚠️  {f}{source}")


def cmd_prepare(con: duckdb.DuckDBPyConnection) -> None:
    """Prepare CSV files for neo4j-admin bulk import."""
    output_dir = Path("/tmp/pkg_neo4j_import")
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("Preparing Neo4j Import Files")
    print("=" * 80)

    # 1. BioEntities nodes
    print("\n1/5 Exporting BioEntity nodes...")
    con.execute(f"""
        COPY (
            SELECT EntityId AS 'entityId:ID',
                   Type AS type,
                   Mention AS name,
                   'BioEntity' AS ':LABEL'
            FROM {_read_tsv(con, 'entities')}
        ) TO '{output_dir}/nodes_bioentities.csv'
        WITH (HEADER, DELIMITER ',')
    """)
    print("   ✅ nodes_bioentities.csv")

    # 2. Author nodes
    print("\n2/5 Exporting Author nodes...")
    con.execute(f"""
        COPY (
            SELECT AID AS 'aid:ID',
                   CAST(BeginYear AS VARCHAR) AS begin_year,
                   CAST(RecentYear AS VARCHAR) AS recent_year,
                   CAST(PaperNum AS VARCHAR) AS paper_count,
                   CAST(h_index AS VARCHAR) AS h_index,
                   'Author' AS ':LABEL'
            FROM {_read_tsv(con, 'authors')}
        ) TO '{output_dir}/nodes_authors.csv'
        WITH (HEADER, DELIMITER ',')
    """)
    print("   ✅ nodes_authors.csv")

    # 3. Paper nodes (large — stream)
    print("\n3/5 Exporting Paper nodes (36M rows — this will take a while)...")
    con.execute(f"""
        COPY (
            SELECT CAST(PMID AS VARCHAR) AS 'pmid:ID',
                   CAST(PubYear AS VARCHAR) AS pub_year,
                   ArticleTitle AS title,
                   CAST(CitedCount AS VARCHAR) AS cited_count,
                   CAST(IsClinicalArticle AS VARCHAR) AS is_clinical,
                   CAST(IsResearchArticle AS VARCHAR) AS is_research,
                   'Paper' AS ':LABEL'
            FROM {_read_tsv(con, 'papers')}
        ) TO '{output_dir}/nodes_papers.csv'
        WITH (HEADER, DELIMITER ',')
    """)
    print("   ✅ nodes_papers.csv")

    # 4. Clinical Trial nodes
    print("\n4/5 Exporting ClinicalTrial nodes...")
    con.execute(f"""
        COPY (
            SELECT nct_id AS 'nctId:ID',
                   phase,
                   overall_status AS status,
                   brief_title AS title,
                   conditions,
                   'ClinicalTrial' AS ':LABEL'
            FROM {_read_tsv(con, 'trials')}
        ) TO '{output_dir}/nodes_trials.csv'
        WITH (HEADER, DELIMITER ',')
    """)
    print("   ✅ nodes_trials.csv")

    # 5. Patent nodes
    print("\n5/5 Exporting Patent nodes...")
    con.execute(f"""
        COPY (
            SELECT PatentId AS 'patentId:ID',
                   Type AS patent_type,
                   GrantedDate AS granted_date,
                   Title AS title,
                   CAST(ClaimNum AS VARCHAR) AS claim_count,
                   'Patent' AS ':LABEL'
            FROM {_read_tsv(con, 'patents')}
        ) TO '{output_dir}/nodes_patents.csv'
        WITH (HEADER, DELIMITER ',')
    """)
    print("   ✅ nodes_patents.csv")

    print(f"\n✅ All node files exported to {output_dir}/")
    print("   Next: Export relationship CSVs and run neo4j-admin import")


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python pkg_explorer.py {stats|entities|sample|compare|prepare}")
        return 1

    cmd = sys.argv[1]
    con = duckdb.connect(":memory:")
    # Set memory limit to avoid OOM on large files
    con.execute("SET memory_limit = '4GB'")
    con.execute("SET threads = 8")

    commands = {
        "stats": cmd_stats,
        "entities": cmd_entities,
        "sample": cmd_sample,
        "compare": cmd_compare_template,
        "prepare": cmd_prepare,
    }

    if cmd not in commands:
        print(f"Unknown command: {cmd}. Use one of: {', '.join(commands)}")
        return 1

    commands[cmd](con)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
