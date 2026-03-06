#!/usr/bin/env python3
"""Ensembl MySQL Dump Downloader

Automatically identifies the latest Ensembl release from FTP and downloads
the essential core database table dumps required for the Bioregistry Graph:
- gene.txt.gz
- transcript.txt.gz
- translation.txt.gz
- xref.txt.gz
- object_xref.txt.gz
- external_db.txt.gz

Usage:
    python download_ensembl.py --out /home/mohammadi/datasets/identifiers/databases/ensembl/mysql
"""

import argparse
import ftplib
import subprocess
from pathlib import Path
from loguru import logger
import sys

FTP_HOST = "ftp.ensembl.org"
FTP_DIR = "/pub/current_mysql/"
TARGET_TABLES = [
    "gene.txt.gz",
    "transcript.txt.gz",
    "translation.txt.gz",
    "xref.txt.gz",
    "object_xref.txt.gz",
    "external_db.txt.gz"
]

def get_latest_human_core() -> str:
    """Connect to Ensembl FTP to find the active human core database directory."""
    logger.info(f"Connecting to {FTP_HOST}{FTP_DIR} to find latest human core database...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login()
        ftp.cwd(FTP_DIR)
        dirs = ftp.nlst()
        human_dirs = [d for d in dirs if d.startswith("homo_sapiens_core_")]
        if not human_dirs:
            raise ValueError("No human core directory found!")

        # Sort to get the latest version (e.g., homo_sapiens_core_115_38)
        human_dirs.sort(key=lambda x: int(x.split("_")[3]))
        latest = human_dirs[-1]
        logger.success(f"Discovered latest release: {latest}")
        return latest
    except Exception as e:
        logger.error(f"Failed to fetch FTP directory listing: {e}")
        sys.exit(1)

def download_tables(db_name: str, out_dir: Path):
    """Utilizes the robust cyto-assist download_manager to pull the targeted tables natively."""
    out_dir.mkdir(parents=True, exist_ok=True)

    import runpy

    # We locate our cyto-assist download_manager script dynamically since it's installed
    try:
        from cyto_assist.data import download_manager
    except ImportError:
        logger.error("Download manager not importable directly. Make sure you run within cyto-assist env.")
        sys.exit(1)

    for table in TARGET_TABLES:
        url = f"ftp://{FTP_HOST}{FTP_DIR}{db_name}/{table}"
        output_path = out_dir / table

        if output_path.exists():
            logger.info(f"Table {table} already exists. Skipping.")
            continue

        logger.info(f"Queueing download for {table}...")

        # Call the CLI main functionality using subprocess to keep it clean via args
        cmd = [
            "uv", "run", "python", "src/cyto_assist/data/download_manager.py",
            "download", url,
            "-o", str(output_path),
            "--connections", "8"
        ]

        result = subprocess.run(cmd)
        if result.returncode != 0:
            logger.error(f"Failed to download {table}.")
            sys.exit(1)

    logger.success(f"All essential Ensembl core tables successfully downloaded to {out_dir}")

def main():
    parser = argparse.ArgumentParser(description="Download Ensembl MySQL Core Data")
    parser.add_argument("--out", type=str, required=True, help="Destination directory for the .txt.gz files")
    args = parser.parse_args()

    out_dir = Path(args.out)
    latest_db = get_latest_human_core()
    download_tables(latest_db, out_dir)

if __name__ == "__main__":
    main()
