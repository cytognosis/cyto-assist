#!/usr/bin/env python3
"""PKG → Neo4j Import Pipeline — Prepares CSVs and runs neo4j-admin import.

This script:
1. Uses DuckDB to read PKG TSV files (handles .gz, quoting issues)
2. Exports node and relationship CSVs in neo4j-admin import format
3. Runs neo4j-admin database import for bulk loading

The neo4j-admin import format requires:
- Node CSVs: header with :ID, properties, :LABEL
- Relationship CSVs: header with :START_ID, :END_ID, :TYPE, properties

Usage:
    python pkg_neo4j_import.py prepare   # Generate CSV files
    python pkg_neo4j_import.py import    # Run neo4j-admin import
    python pkg_neo4j_import.py verify    # Verify imported data
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import duckdb

# ── Configuration ────────────────────────────────────────────────────────────

PKG_DIR = Path("/home/mohammadi/datasets/network/public/kg/PMK")
IMPORT_DIR = Path("/tmp/pkg_neo4j_import")
NEO4J_HOME = Path("/home/mohammadi/software/neo4j")
DB_NAME = "pkg"


def _tsv(name: str) -> str:
    """Return DuckDB read expression for a PKG file."""
    files = {
        "papers": "C01_Papers.tsv",
        "paper_authors": "C02_Link_Papers_Authors.tsv",
        "affiliations": "C03_Affiliations.tsv.gz",
        "citations": "C04_ReferenceList_Papers.tsv.gz",
        "pis": "C05_PIs.tsv",
        "paper_entities": "C06_Link_Papers_BioEntities.tsv.gz",
        "authors": "C07_Authors.tsv",
        "paper_journals": "C10_Link_Papers_Journals.tsv",
        "trials": "C11_ClinicalTrials.tsv",
        "paper_trials": "C12_Link_Papers_Clinicaltrials.tsv",
        "trial_entities": "C13_Link_ClinicalTrials_BioEntities.tsv",
        "patents": "C15_Patents.tsv",
        "patent_papers": "C16_Link_Patents_Papers.tsv",
        "patent_entities": "C18_Link_Patents_BioEntities.tsv",
        "entity_relations": "C21_Bioentity_Relationships.tsv",
        "entities": "C23_BioEntities.tsv",
        "trial_patents": "C24_Link_Clinicaltrials_Patents.tsv",
    }
    path = PKG_DIR / files[name]
    return (
        f"read_csv_auto('{path}', delim='\\t', header=true,"
        f" sample_size=10000, quote='', strict_mode=false,"
        f" nullstr='NULL', all_varchar=true)"
    )


def _export(con: duckdb.DuckDBPyConnection, sql: str, outfile: Path) -> int:
    """Export a DuckDB query to CSV and return row count."""
    con.execute(f"COPY ({sql}) TO '{outfile}' WITH (HEADER, DELIMITER ',')")
    # Count lines (minus header)
    result = con.execute(
        f"SELECT count(*) FROM read_csv_auto('{outfile}')"
    ).fetchone()
    return result[0] if result else 0


def cmd_prepare() -> None:
    """Generate neo4j-admin import CSV files."""
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(":memory:")
    con.execute("SET memory_limit = '8GB'")
    con.execute("SET threads = 16")

    print("=" * 70)
    print("PKG → Neo4j Import: Preparing CSV Files")
    print("=" * 70)

    # ── Node files ──────────────────────────────────────────────────────

    # 1. BioEntity nodes (360K) — small, fast
    print("\n[1/9] BioEntity nodes...")
    n = _export(con, f"""
        SELECT EntityId AS "entityId:ID(BioEntity)",
               Type AS "entityType:string",
               Mention AS "name:string"
        FROM {_tsv('entities')}
    """, IMPORT_DIR / "nodes_bioentities.csv")
    print(f"   ✅ {n:,} rows")

    # 2. Author nodes (26M)
    print("\n[2/9] Author nodes...")
    n = _export(con, f"""
        SELECT AID AS "aid:ID(Author)",
               CAST(BeginYear AS VARCHAR) AS "beginYear:int",
               CAST(RecentYear AS VARCHAR) AS "recentYear:int",
               CAST(PaperNum AS VARCHAR) AS "paperCount:int",
               CAST(h_index AS VARCHAR) AS "hIndex:int"
        FROM {_tsv('authors')}
    """, IMPORT_DIR / "nodes_authors.csv")
    print(f"   ✅ {n:,} rows")

    # 3. Paper nodes (36M) — large
    print("\n[3/9] Paper nodes (36M — may take 2-3 min)...")
    n = _export(con, f"""
        SELECT CAST(PMID AS VARCHAR) AS "pmid:ID(Paper)",
               CAST(PubYear AS VARCHAR) AS "pubYear:int",
               REPLACE(REPLACE(ArticleTitle, '"', '""'), ',', ' ') AS "title:string",
               CAST(CitedCount AS VARCHAR) AS "citedCount:int",
               CAST(IsClinicalArticle AS VARCHAR) AS "isClinical:boolean",
               CAST(IsResearchArticle AS VARCHAR) AS "isResearch:boolean",
               CAST(AuthorNum AS VARCHAR) AS "authorCount:int"
        FROM {_tsv('papers')}
    """, IMPORT_DIR / "nodes_papers.csv")
    print(f"   ✅ {n:,} rows")

    # 4. ClinicalTrial nodes (480K)
    print("\n[4/9] ClinicalTrial nodes...")
    n = _export(con, f"""
        SELECT nct_id AS "nctId:ID(Trial)",
               phase AS "phase:string",
               overall_status AS "status:string",
               REPLACE(REPLACE(brief_title, '"', '""'), ',', ' ') AS "title:string",
               study_type AS "studyType:string"
        FROM {_tsv('trials')}
    """, IMPORT_DIR / "nodes_trials.csv")
    print(f"   ✅ {n:,} rows")

    # 5. Patent nodes (1.3M)
    print("\n[5/9] Patent nodes...")
    n = _export(con, f"""
        SELECT PatentId AS "patentId:ID(Patent)",
               Type AS "patentType:string",
               GrantedDate AS "grantedDate:string",
               REPLACE(REPLACE(Title, '"', '""'), ',', ' ') AS "title:string",
               CAST(ClaimNum AS VARCHAR) AS "claimCount:int"
        FROM {_tsv('patents')}
    """, IMPORT_DIR / "nodes_patents.csv")
    print(f"   ✅ {n:,} rows")

    # ── Relationship files ──────────────────────────────────────────────

    # 6. Paper AUTHORED_BY Author (160M)
    print("\n[6/9] AUTHORED_BY relationships (160M — may take 5 min)...")
    n = _export(con, f"""
        SELECT CAST(PMID AS VARCHAR) AS ":START_ID(Paper)",
               AID AS ":END_ID(Author)",
               CAST(AuthorOrder AS VARCHAR) AS "order:int"
        FROM {_tsv('paper_authors')}
        WHERE AID IS NOT NULL AND AID != ''
    """, IMPORT_DIR / "rels_authored_by.csv")
    print(f"   ✅ {n:,} rows")

    # 7. Paper CITES Paper (774M) — largest
    print("\n[7/9] CITES relationships (774M — may take 10+ min)...")
    n = _export(con, f"""
        SELECT CAST(PMID AS VARCHAR) AS ":START_ID(Paper)",
               CAST(RefPMID AS VARCHAR) AS ":END_ID(Paper)"
        FROM {_tsv('citations')}
        WHERE PMID IS NOT NULL AND RefPMID IS NOT NULL
    """, IMPORT_DIR / "rels_cites.csv")
    print(f"   ✅ {n:,} rows")

    # 8. Paper MENTIONS BioEntity (464M)
    print("\n[8/9] MENTIONS relationships (464M — may take 8 min)...")
    n = _export(con, f"""
        SELECT CAST(PMID AS VARCHAR) AS ":START_ID(Paper)",
               EntityId AS ":END_ID(BioEntity)",
               Type AS "entityType:string"
        FROM {_tsv('paper_entities')}
        WHERE EntityId IS NOT NULL AND EntityId != ''
    """, IMPORT_DIR / "rels_mentions.csv")
    print(f"   ✅ {n:,} rows")

    # 9. BioEntity INTERACTS_WITH BioEntity (61M)
    print("\n[9/9] INTERACTS_WITH relationships (61M)...")
    n = _export(con, f"""
        SELECT entity_id1 AS ":START_ID(BioEntity)",
               entity_id2 AS ":END_ID(BioEntity)",
               relation_type AS "relationType:string",
               CAST(PMID AS VARCHAR) AS "pmid:string"
        FROM {_tsv('entity_relations')}
        WHERE entity_id1 IS NOT NULL AND entity_id2 IS NOT NULL
    """, IMPORT_DIR / "rels_interacts.csv")
    print(f"   ✅ {n:,} rows")

    # Summary
    print(f"\n{'=' * 70}")
    total_size = sum(f.stat().st_size for f in IMPORT_DIR.glob("*.csv"))
    print(f"Total CSV size: {total_size / (1024**3):.1f} GB")
    print(f"Output directory: {IMPORT_DIR}")
    print(f"\nRun: python {__file__} import")

    con.close()


def cmd_import() -> None:
    """Run neo4j-admin database import."""
    neo4j_admin = NEO4J_HOME / "bin" / "neo4j-admin"

    # Stop Neo4j first
    print("Stopping Neo4j...")
    subprocess.run([str(NEO4J_HOME / "bin" / "neo4j"), "stop"], check=False)

    cmd = [
        str(neo4j_admin), "database", "import", "full", DB_NAME,
        "--overwrite-destination",
        # Node files
        f"--nodes=Paper={IMPORT_DIR}/nodes_papers.csv",
        f"--nodes=Author={IMPORT_DIR}/nodes_authors.csv",
        f"--nodes=BioEntity={IMPORT_DIR}/nodes_bioentities.csv",
        f"--nodes=ClinicalTrial={IMPORT_DIR}/nodes_trials.csv",
        f"--nodes=Patent={IMPORT_DIR}/nodes_patents.csv",
        # Relationship files
        f"--relationships=AUTHORED_BY={IMPORT_DIR}/rels_authored_by.csv",
        f"--relationships=CITES={IMPORT_DIR}/rels_cites.csv",
        f"--relationships=MENTIONS={IMPORT_DIR}/rels_mentions.csv",
        f"--relationships=INTERACTS_WITH={IMPORT_DIR}/rels_interacts.csv",
        # Performance settings
        "--skip-bad-relationships",
        "--skip-duplicate-nodes",
        "--processors=16",
        "--max-off-heap-memory=8G",
    ]

    print("Running neo4j-admin import...")
    print(f"Command: {' '.join(cmd[:5])} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        sys.exit(1)

    print(f"\n✅ Import complete. Start Neo4j and create database '{DB_NAME}':")
    print(f"   {NEO4J_HOME}/bin/neo4j start")
    print(f"   Then in cypher-shell: CREATE DATABASE {DB_NAME}")


def cmd_verify() -> None:
    """Verify imported data via Python driver."""
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver("bolt://localhost:7687",
                                  auth=("neo4j", "cytognosis2025"))
    driver.verify_connectivity()

    queries = [
        ("Total Papers", "MATCH (p:Paper) RETURN count(p) AS cnt"),
        ("Total Authors", "MATCH (a:Author) RETURN count(a) AS cnt"),
        ("Total BioEntities", "MATCH (b:BioEntity) RETURN count(b) AS cnt"),
        ("Total Citations", "MATCH ()-[r:CITES]->() RETURN count(r) AS cnt"),
        ("Total Mentions", "MATCH ()-[r:MENTIONS]->() RETURN count(r) AS cnt"),
        ("Total Interactions", "MATCH ()-[r:INTERACTS_WITH]->() RETURN count(r) AS cnt"),
    ]

    print("=" * 60)
    print("PKG Neo4j Import Verification")
    print("=" * 60)
    for label, query in queries:
        records, _, _ = driver.execute_query(query)
        print(f"  {label}: {records[0]['cnt']:,}")

    driver.close()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python pkg_neo4j_import.py {prepare|import|verify}")
        return 1

    commands = {"prepare": cmd_prepare, "import": cmd_import, "verify": cmd_verify}
    cmd = sys.argv[1]
    if cmd not in commands:
        print(f"Unknown: {cmd}. Use: {', '.join(commands)}")
        return 1
    commands[cmd]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
