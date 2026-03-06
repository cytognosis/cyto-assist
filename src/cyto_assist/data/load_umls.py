#!/usr/bin/env python3
"""UMLS Metathesaurus Ingestion Script

Loads the NLM Unified Medical Language System (UMLS) Rich Release Format (RRF)
files directly into a pre-computed DuckDB database inside the Cyto-assist bioregistry.
This allows massive concept mappings (CUI), languages, and sources (MSH, SNOMED)
to be evaluated blazingly fast locally in cyto-assist NLP workloads.

Source: `MRCONSO.RRF` -> Target: `bioregistry.db`
"""

import sys
import duckdb
from pathlib import Path
import argparse


def load_mrconso(db_path: Path, mrconso_path: Path) -> None:
    """Load the MRCONSO.RRF file into the DuckDB bioregistry."""
    if not mrconso_path.exists():
        print(f"Error: {mrconso_path} does not exist.")
        sys.exit(1)

    print(f"Connecting to {db_path}...")
    con = duckdb.connect(str(db_path))

    # Drop old if exists
    con.execute("DROP TABLE IF EXISTS umls_mrconso")

    print("Creating umls_mrconso table...")
    con.execute("""
        CREATE TABLE umls_mrconso (
            CUI VARCHAR, LAT VARCHAR, TS VARCHAR, LUI VARCHAR,
            STT VARCHAR, SUI VARCHAR, ISPREF VARCHAR, AUI VARCHAR,
            SAUI VARCHAR, SCUI VARCHAR, SDUI VARCHAR, SAB VARCHAR,
            TTY VARCHAR, CODE VARCHAR, STR VARCHAR, SRL VARCHAR,
            SUPPRESS VARCHAR, CVF VARCHAR
        )
    """)

    print(f"Ingesting into DuckDB from {mrconso_path} (delimited by '|')...")
    # Use standard CSV reader with quoting disabled (UMLS uses literal pipe only)
    con.execute(f"COPY umls_mrconso FROM '{mrconso_path}' (DELIMITER '|', HEADER FALSE, QUOTE '')")

    count = con.execute("SELECT COUNT(*) FROM umls_mrconso").fetchone()[0]
    print(f"Successfully loaded {count:,} records into umls_mrconso.")

    # Create indices for fast lookup
    print("Building indices on CUI, STR, SAB, and CODE...")
    con.execute("CREATE INDEX idx_umls_cui ON umls_mrconso(CUI)")
    con.execute("CREATE INDEX idx_umls_str ON umls_mrconso(STR)")
    con.execute("CREATE INDEX idx_umls_sab ON umls_mrconso(SAB)")
    con.execute("CREATE INDEX idx_umls_code ON umls_mrconso(CODE)")
    print("Indices created.")
    con.close()


def load_mrrel(db_path: Path, mrrel_path: Path) -> None:
    """Load the MRREL.RRF file into the DuckDB bioregistry."""
    if not mrrel_path.exists():
        print(f"Error: {mrrel_path} does not exist.")
        sys.exit(1)

    print(f"Connecting to {db_path}...")
    con = duckdb.connect(str(db_path))

    # Drop old if exists
    con.execute("DROP TABLE IF EXISTS umls_mrrel")

    print("Creating umls_mrrel table...")
    con.execute("""
        CREATE TABLE umls_mrrel (
            CUI1 VARCHAR, AUI1 VARCHAR, STYPE1 VARCHAR, REL VARCHAR,
            CUI2 VARCHAR, AUI2 VARCHAR, STYPE2 VARCHAR, RELA VARCHAR,
            RUI VARCHAR, SRUI VARCHAR, SAB VARCHAR, SL VARCHAR,
            RG VARCHAR, DIR VARCHAR, SUPPRESS VARCHAR, CVF VARCHAR
        )
    """)

    print(f"Ingesting into DuckDB from {mrrel_path} (delimited by '|')...")
    con.execute(f"COPY umls_mrrel FROM '{mrrel_path}' (DELIMITER '|', HEADER FALSE)")

    count = con.execute("SELECT COUNT(*) FROM umls_mrrel").fetchone()[0]
    print(f"Successfully loaded {count:,} records into umls_mrrel.")

    con.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="UMLS Data Loader")
    parser.add_argument("--db", type=Path, default=Path.home() / "bioregistry.db",
                        help="Target DuckDB file")
    parser.add_argument("--rrf-dir", type=Path, default=Path("/home/mohammadi/datasets/identifiers/databases/UMLS/umls-2025AB-metathesaurus-full/2025AB/META"),
                        help="Directory containing MRCONSO.RRF and MRREL.RRF")
    parser.add_argument("--include-rel", action="store_true", help="Also load MRREL (edges/relations)")
    args = parser.parse_args()

    mrconso_file = args.rrf_dir / "MRCONSO.RRF"
    mrrel_file = args.rrf_dir / "MRREL.RRF"

    load_mrconso(args.db, mrconso_file)

    if args.include_rel:
        load_mrrel(args.db, mrrel_file)

    return 0

if __name__ == "__main__":
    sys.exit(main())
