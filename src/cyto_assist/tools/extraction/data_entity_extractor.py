#!/usr/bin/env python3
"""Data Entity Extractor — Track datasets and access levels from papers.

Extracts dataset metadata: access level (GA4GH-aligned), data types/modalities,
formats, sizes, and standardized descriptions.

Usage:
    python data_entity_extractor.py extract --url "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE123456"
    python data_entity_extractor.py classify --text "controlled access dbGaP phs000123"
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

# GA4GH-aligned data access levels
ACCESS_LEVELS = {
    "open": {
        "level": 0,
        "label": "Open Access",
        "description": "Freely available, no restrictions on download or use",
        "examples": ["GEO", "ArrayExpress", "SRA (public)", "ENCODE", "GTEx portal"],
    },
    "registered": {
        "level": 1,
        "label": "Registered Access",
        "description": "Requires user registration/account but no formal approval",
        "examples": ["TCGA (open tier)", "UK Biobank (registered)"],
    },
    "controlled": {
        "level": 2,
        "label": "Controlled Access",
        "description": "Requires institutional approval via DAC (Data Access Committee)",
        "examples": ["dbGaP", "EGA", "TCGA (controlled)", "UK Biobank (full)"],
        "requirements": [
            "IRB approval or equivalent",
            "Data Use Agreement (DUA)",
            "Institutional sign-off",
            "Approved research protocol",
        ],
    },
    "restricted": {
        "level": 3,
        "label": "Restricted/Embargoed",
        "description": "Available only to specific collaborators or after embargo period",
        "examples": ["Pre-publication data", "Clinical trial data"],
    },
}

# Data modality patterns
DATA_MODALITIES = {
    "scRNA-seq": ["single-cell rna", "scrna-seq", "10x genomics", "drop-seq", "smart-seq"],
    "bulk RNA-seq": ["rna-seq", "rna sequencing", "transcriptome"],
    "ATAC-seq": ["atac-seq", "chromatin accessibility"],
    "ChIP-seq": ["chip-seq", "chromatin immunoprecipitation"],
    "WGS": ["whole genome sequencing", "wgs"],
    "WES": ["whole exome sequencing", "wes", "exome"],
    "Proteomics": ["proteomics", "mass spectrometry", "LC-MS"],
    "Metabolomics": ["metabolomics", "metabolome"],
    "Imaging": ["imaging", "microscopy", "histology", "pathology"],
    "Clinical": ["clinical data", "electronic health records", "ehr", "patient data"],
    "Spatial": ["spatial transcriptomics", "visium", "merfish", "slide-seq"],
    "Multiome": ["multiome", "multi-modal", "joint profiling"],
}

# Data format patterns
DATA_FORMATS = {
    "FASTQ": ["fastq", ".fastq.gz"],
    "BAM/CRAM": ["bam", "cram", "aligned reads"],
    "VCF": ["vcf", "variant call format"],
    "h5ad": ["h5ad", "anndata"],
    "H5": ["hdf5", ".h5"],
    "CSV/TSV": ["csv", "tsv", "tabular"],
    "DICOM": ["dicom", "medical imaging"],
    "NIfTI": ["nifti", ".nii"],
}

# Repository patterns for access level inference
REPOSITORY_ACCESS = {
    "dbgap": "controlled",
    "ega": "controlled",
    "geo": "open",
    "arrayexpress": "open",
    "sra": "open",
    "encode": "open",
    "gtex": "registered",
    "tcga": "controlled",
    "uk biobank": "controlled",
    "zenodo": "open",
    "figshare": "open",
    "dryad": "open",
}


def classify_access_level(text: str) -> dict[str, Any]:
    """Infer data access level from descriptive text.

    Args:
        text: Text describing data availability (from paper or repository)

    Returns:
        Dict with inferred access level and confidence
    """
    text_lower = text.lower()
    result: dict[str, Any] = {
        "level": "open",
        "confidence": 0.5,
        "signals": [],
    }

    # Check repository patterns
    for repo, level in REPOSITORY_ACCESS.items():
        if repo in text_lower:
            result["level"] = level
            result["confidence"] = 0.9
            result["signals"].append(f"Repository: {repo}")

    # Check access keywords
    controlled_signals = [
        "controlled access", "data access committee", "dac",
        "data use agreement", "dua", "irb", "ethics approval",
        "restricted", "upon request", "reasonable request",
    ]
    open_signals = [
        "freely available", "publicly available", "open access",
        "no restrictions", "creative commons",
    ]

    for signal in controlled_signals:
        if signal in text_lower:
            result["level"] = "controlled"
            result["confidence"] = max(result["confidence"], 0.8)
            result["signals"].append(f"Controlled signal: {signal}")

    for signal in open_signals:
        if signal in text_lower:
            result["level"] = "open"
            result["confidence"] = max(result["confidence"], 0.8)
            result["signals"].append(f"Open signal: {signal}")

    result["access_info"] = ACCESS_LEVELS.get(result["level"], {})
    return result


def detect_modalities(text: str) -> list[str]:
    """Detect data modalities mentioned in text."""
    text_lower = text.lower()
    detected = []

    for modality, patterns in DATA_MODALITIES.items():
        for pattern in patterns:
            if pattern in text_lower:
                if modality not in detected:
                    detected.append(modality)
                break

    return detected


def detect_formats(text: str) -> list[str]:
    """Detect data formats mentioned in text."""
    text_lower = text.lower()
    detected = []

    for fmt, patterns in DATA_FORMATS.items():
        for pattern in patterns:
            if pattern in text_lower:
                if fmt not in detected:
                    detected.append(fmt)
                break

    return detected


def extract_sample_info(text: str) -> dict[str, Any]:
    """Extract sample/cell counts and model system info."""
    text_lower = text.lower()
    info: dict[str, Any] = {
        "n_samples": None,
        "n_cells": None,
        "species": [],
        "model_system": None,
        "tissue_types": [],
    }

    # Sample counts
    for pattern in [
        r"(\d[\d,]*)\s+(?:samples|subjects|individuals|patients|participants)",
        r"n\s*=\s*(\d[\d,]*)",
    ]:
        match = re.search(pattern, text_lower)
        if match:
            info["n_samples"] = int(match.group(1).replace(",", ""))

    # Cell counts
    for pattern in [
        r"(\d[\d,]*)\s+(?:cells|nuclei|single cells)",
    ]:
        match = re.search(pattern, text_lower)
        if match:
            info["n_cells"] = int(match.group(1).replace(",", ""))

    # Species
    for species in ["human", "mouse", "rat", "zebrafish", "drosophila", "c. elegans"]:
        if species in text_lower:
            info["species"].append(species)

    # Model system
    if "in vivo" in text_lower:
        info["model_system"] = "in vivo"
    elif "in vitro" in text_lower or "cell line" in text_lower:
        info["model_system"] = "in vitro"
    elif "organoid" in text_lower:
        info["model_system"] = "organoid"

    return info


def build_data_entity(
    text: str, url: str | None = None
) -> dict[str, Any]:
    """Build a complete data entity description.

    Args:
        text: Text describing the dataset (from paper or repository)
        url: Optional URL to the data repository

    Returns:
        Standardized data entity dict
    """
    return {
        "url": url,
        "access": classify_access_level(text),
        "modalities": detect_modalities(text),
        "formats": detect_formats(text),
        "sample_info": extract_sample_info(text),
    }


# ── CLI ──────────────────────────────────────────────────────────────


def cmd_extract(args: list[str]) -> int:
    """Extract data entity metadata."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract data entity")
    parser.add_argument("--text", "-t", required=True, help="Description text")
    parser.add_argument("--url", help="Data URL")
    parser.add_argument("--output", help="Output JSON")
    parsed = parser.parse_args(args)

    entity = build_data_entity(parsed.text, parsed.url)

    print(f"\n  Access: {entity['access']['level']} "
          f"({entity['access']['confidence']:.0%})")
    print(f"  Modalities: {entity['modalities']}")
    print(f"  Formats: {entity['formats']}")
    sample = entity["sample_info"]
    if sample["n_samples"]:
        print(f"  Samples: {sample['n_samples']:,}")
    if sample["n_cells"]:
        print(f"  Cells: {sample['n_cells']:,}")
    if sample["species"]:
        print(f"  Species: {sample['species']}")

    if parsed.output:
        with open(parsed.output, "w") as f:
            json.dump(entity, f, indent=2)

    return 0


def cmd_classify(args: list[str]) -> int:
    """Classify data access level."""
    import argparse

    parser = argparse.ArgumentParser(description="Classify access level")
    parser.add_argument("--text", "-t", required=True)
    parsed = parser.parse_args(args)

    result = classify_access_level(parsed.text)
    level_info = ACCESS_LEVELS.get(result["level"], {})

    print(f"  Level: {result['level']} ({level_info.get('label', '')})")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  Description: {level_info.get('description', '')}")
    print(f"  Signals: {result['signals']}")

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: data_entity_extractor.py <command> [args]")
        print("Commands: extract, classify")
        return 1

    commands = {"extract": cmd_extract, "classify": cmd_classify}
    command = sys.argv[1]
    if command not in commands:
        return 1
    return commands[command](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
