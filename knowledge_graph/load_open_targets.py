import argparse
from pathlib import Path

import duckdb
from loguru import logger

DATA_DIR = Path("/home/mohammadi/datasets")
OT_DIR = DATA_DIR / "network" / "public" / "kg" / "open_targets" / "25.03"
DB_PATH = Path("/home/mohammadi/bioregistry.db")


def verify_bioregistry(conn: duckdb.DuckDBPyConnection):
    """Ensure the Bioregistry is built and contains the ID translation mapping"""
    try:
        count = conn.execute("SELECT COUNT(*) FROM v_translate_id").fetchone()[0]
        logger.info(f"Bioregistry active. v_translate_id contains {count:,} mappings.")
    except Exception as e:
        logger.error(
            "Bioregistry v_translate_id view not found. Please run build_bioregistry.py first."
        )
        raise e


def extract_nodes(conn: duckdb.DuckDBPyConnection, out_dir: Path):
    """
    Extract entity nodes directly from the verified Bioregistry Master Tables.
    These form the backbone of the Graph.
    """
    logger.info("Extracting Master Nodes to TSV...")

    # Gene, Transcript, Protein nodes
    conn.execute(f"""
        COPY (
            SELECT ensembl_id as id, symbol, name, entity_type as label
            FROM master_bioentity WHERE ensembl_id IS NOT NULL
        ) TO '{out_dir}/nodes_bioentity.tsv' (HEADER, DELIMITER '\t');
    """)

    # Disease nodes
    conn.execute(f"""
        COPY (
            SELECT mondo_id as id, name, 'disease' as label
            FROM master_disease WHERE mondo_id IS NOT NULL
        ) TO '{out_dir}/nodes_disease.tsv' (HEADER, DELIMITER '\t');
    """)

    # Chemical nodes
    conn.execute(f"""
        COPY (
            SELECT pubchem_cid as id, name, 'chemical' as label
            FROM master_chemical WHERE pubchem_cid IS NOT NULL
        ) TO '{out_dir}/nodes_chemical.tsv' (HEADER, DELIMITER '\t');
    """)

    # Variant nodes
    conn.execute(f"""
        COPY (
            SELECT rsid as id, chromosome, position, reference, alternate, 'variant' as label
            FROM variant_identifiers WHERE rsid IS NOT NULL
        ) TO '{out_dir}/nodes_variant.tsv' (HEADER, DELIMITER '\t');
    """)
    logger.success("Master node extraction complete.")


def extract_open_target_edges(conn: duckdb.DuckDBPyConnection, out_dir: Path):
    """
    Map OpenTargets datasets into schema-aligned edges by passing
    source/target identifiers through the `v_translate_id` mapping layer securely.
    """
    logger.info("Building Open Targets Edge Extractors...")

    # 1. targets (Chemical -> Protein)
    moa_dir = OT_DIR / "drug_mechanism_of_action"
    if moa_dir.exists():
        logger.info("Extracting `targets` (mechanismOfAction) edges...")
        try:
            import pandas as pd

            # Load with pyarrow to preserve list types, explode them natively in pandas
            df_moa_raw = pd.read_parquet(
                moa_dir,
                engine="pyarrow",
                columns=["chemblIds", "targets", "actionType", "mechanismOfAction"],
            )
            df_moa = df_moa_raw.explode("chemblIds").explode("targets")

            query = f"""
                COPY (
                    SELECT DISTINCT
                        v_chem.canonical_id as source,
                        v_prot.canonical_id as target,
                        'targets' as label,
                        moa.actionType as action_type,
                        moa.mechanismOfAction as mechanism
                    FROM df_moa moa
                    -- Map Drug (ChEMBL) to Master Chemical (PubChem)
                    JOIN v_translate_id v_chem ON moa.chemblIds = v_chem.input_id AND v_chem.canonical_type = 'Chemical'
                    -- Map Target (Ensembl) to Master Protein
                    JOIN v_translate_id v_prot ON moa.targets = v_prot.input_id AND v_prot.canonical_type = 'Protein'
                ) TO '{out_dir}/edges_targets.tsv' (HEADER, DELIMITER '\t');
            """
            conn.execute(query)
            logger.success("Wrote edges_targets.tsv")
        except Exception as e:
            logger.error(f"Error mapping targets: {e}")

    # 2. indication & contraindication (Chemical -> Disease)
    ind_dir = OT_DIR / "drug_indication"
    if ind_dir.exists():
        logger.info("Extracting `indication` edges...")
        try:
            import pandas as pd

            # The 'indications' column is a list of dicts. We explode it, then expand the dicts into columns
            df_ind_raw = pd.read_parquet(
                ind_dir, engine="pyarrow", columns=["id", "indications"]
            )
            df_exploded = df_ind_raw.explode("indications").dropna(
                subset=["indications"]
            )

            # Extract nested fields efficiently
            df_ind = pd.DataFrame(
                {
                    "id": df_exploded["id"],
                    "disease": df_exploded["indications"].apply(
                        lambda x: x.get("disease") if isinstance(x, dict) else None
                    ),
                    "maxPhase": df_exploded["indications"].apply(
                        lambda x: (
                            x.get("maxPhaseForIndication")
                            if isinstance(x, dict)
                            else None
                        )
                    ),
                }
            )

            query = f"""
                COPY (
                    SELECT DISTINCT
                        v_chem.canonical_id as source,
                        v_dis.canonical_id as target,
                        'indication' as label,
                        ind.maxPhase as max_phase
                    FROM df_ind ind
                    JOIN v_translate_id v_chem ON ind.id = v_chem.input_id AND v_chem.canonical_type = 'Chemical'
                    JOIN v_translate_id v_dis ON ind.disease = v_dis.input_id AND v_dis.canonical_type = 'Disease'
                    WHERE ind.disease IS NOT NULL
                ) TO '{out_dir}/edges_indication.tsv' (HEADER, DELIMITER '\t');
            """
            conn.execute(query)
            logger.success("Wrote edges_indication.tsv")
        except Exception as e:
            logger.error(f"Error mapping indications: {e}")

    # 3. associated_with (Gene -> Disease)
    assoc_dir = OT_DIR / "association_overall_direct"
    if assoc_dir.exists():
        logger.info("Extracting `associated_with` (gene-disease) edges...")
        try:
            import pandas as pd

            df_assoc = pd.read_parquet(
                assoc_dir, engine="pyarrow", columns=["targetId", "diseaseId", "score"]
            )

            query = f"""
                COPY (
                    SELECT DISTINCT
                        v_gene.canonical_id as source,
                        v_dis.canonical_id as target,
                        'associated_with' as label,
                        assoc.score
                    FROM df_assoc assoc
                    JOIN v_translate_id v_gene ON assoc.targetId = v_gene.input_id AND v_gene.canonical_type IN ('Gene', 'Protein')
                    JOIN v_translate_id v_dis ON assoc.diseaseId = v_dis.input_id AND v_dis.canonical_type = 'Disease'
                    WHERE assoc.score > 0.1 -- thresholding to avoid explosion
                ) TO '{out_dir}/edges_associated_with.tsv' (HEADER, DELIMITER '\t');
            """
            conn.execute(query)
            logger.success("Wrote edges_associated_with.tsv")
        except Exception as e:
            logger.error(f"Error mapping associated_with: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract Open Targets into BioCypher/Neo4j Graph TSVs"
    )
    parser.add_argument(
        "--out", type=str, default="graph_export", help="Output directory for TSV files"
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not DB_PATH.exists():
        logger.error(f"Database {DB_PATH} not found. Build bioregistry first.")
        return

    logger.info("Connecting to Bioregistry...")
    conn = duckdb.connect(str(DB_PATH))

    verify_bioregistry(conn)
    extract_nodes(conn, out_dir)
    extract_open_target_edges(conn, out_dir)

    conn.close()
    logger.success("Knowledge Graph Edge & Node Extraction Complete.")


if __name__ == "__main__":
    main()
