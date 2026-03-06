import argparse
from pathlib import Path

import duckdb
import pandas as pd
from loguru import logger

# Paths setup
DATA_DIR = Path("/home/mohammadi/datasets")
ENSEMBL_DIR = DATA_DIR / "identifiers" / "databases" / "ensembl" / "mysql"
PHARMAPROJECTS_DIR = DATA_DIR / "network" / "public" / "clinical" / "Pharmaprojects"
DB_PATH = Path("bioregistry.db")
OT_VARIANT_DIR = DATA_DIR / "network" / "public" / "kg" / "open_targets" / "25.03" / "variant"


def build_master_bioentity(conn: duckdb.DuckDBPyConnection):
    """
    Builds the master_bioentity table merging Gene, Transcript, Protein.
    Prioritizes Ensembl ID as the primary key.
    Reads directly from Ensembl MySQL text dumps using fast DuckDB views.
    """
    logger.info("Building master_bioentity from Ensembl MySQL dumps...")

    # Gene table
    conn.execute(f"""
        CREATE OR REPLACE VIEW ensembl_gene AS
        SELECT
            column00::UBIGINT as gene_id,
            column01::VARCHAR as biotype,
            column07::UBIGINT as display_xref_id,
            column12::VARCHAR as stable_id
        FROM read_csv('{ENSEMBL_DIR}/gene.txt.gz', delim='\\t', header=False, nullstr='\\N', quote='');
    """)

    # Transcript table
    conn.execute(f"""
        CREATE OR REPLACE VIEW ensembl_transcript AS
        SELECT
            column00::UBIGINT as transcript_id,
            column01::UBIGINT as gene_id,
            column09::VARCHAR as biotype,
            column12::UBIGINT as canonical_translation_id,
            column13::VARCHAR as stable_id
        FROM read_csv('{ENSEMBL_DIR}/transcript.txt.gz', delim='\\t', header=False, nullstr='\\N', quote='');
    """)

    # Translation table
    conn.execute(f"""
        CREATE OR REPLACE VIEW ensembl_translation AS
        SELECT
            column0::UBIGINT as translation_id,
            column1::UBIGINT as transcript_id,
            column6::VARCHAR as stable_id
        FROM read_csv('{ENSEMBL_DIR}/translation.txt.gz', delim='\\t', header=False, nullstr='\\N', quote='');
    """)

    # external_db table
    conn.execute(f"""
        CREATE OR REPLACE VIEW ensembl_external_db AS
        SELECT
            column0::UBIGINT as external_db_id,
            column1::VARCHAR as db_name
        FROM read_csv('{ENSEMBL_DIR}/external_db.txt.gz', delim='\\t', header=False, nullstr='\\N', quote='');
    """)

    # xref table
    conn.execute(f"""
        CREATE OR REPLACE VIEW ensembl_xref AS
        SELECT
            column0::UBIGINT as xref_id,
            column1::UBIGINT as external_db_id,
            column2::VARCHAR as dbprimary_acc,
            column3::VARCHAR as display_label
        FROM read_csv('{ENSEMBL_DIR}/xref.txt.gz', delim='\\t', header=False, nullstr='\\N', quote='');
    """)

    # object_xref table
    conn.execute(f"""
        CREATE OR REPLACE VIEW ensembl_object_xref AS
        SELECT
            column0::UBIGINT as object_xref_id,
            column1::UBIGINT as ensembl_id,
            column2::VARCHAR as ensembl_object_type,
            column3::UBIGINT as xref_id
        FROM read_csv('{ENSEMBL_DIR}/object_xref.txt.gz', delim='\\t', header=False, nullstr='\\N', quote='');
    """)

    # Map all XRefs to their object
    conn.execute("""
        CREATE OR REPLACE VIEW mapped_xrefs AS
        SELECT
            ox.ensembl_id as internal_id,
            ox.ensembl_object_type,
            edb.db_name,
            x.dbprimary_acc,
            x.display_label
        FROM ensembl_object_xref ox
        JOIN ensembl_xref x ON ox.xref_id = x.xref_id
        JOIN ensembl_external_db edb ON x.external_db_id = edb.external_db_id;
    """)

    # Master Bioentity Table
    conn.execute("""
        CREATE OR REPLACE TABLE master_bioentity (
            ensembl_id VARCHAR PRIMARY KEY,
            entity_type VARCHAR,
            -- Display Info
            symbol VARCHAR,

            -- Core cross-references
            hgnc_id VARCHAR,
            entrez_id VARCHAR,
            uniprot_ids VARCHAR[],
            refseq_ids VARCHAR[],

            -- Ensembl Internal IDs natively linked
            internal_gene_id UBIGINT,
            internal_transcript_id UBIGINT,
            internal_translation_id UBIGINT
        );
    """)

    # Insert Genes
    logger.info("Ingesting Genes...")
    conn.execute("""
        INSERT INTO master_bioentity (ensembl_id, entity_type, internal_gene_id, symbol, hgnc_id, entrez_id)
        SELECT
            g.stable_id as ensembl_id,
            'Gene' as entity_type,
            MAX(g.gene_id) as internal_gene_id,
            MAX(disp_x.display_label) as symbol,
            MAX(CASE WHEN mx.db_name = 'HGNC' THEN mx.dbprimary_acc END) as hgnc_id,
            MAX(CASE WHEN mx.db_name = 'EntrezGene' THEN mx.dbprimary_acc END) as entrez_id
        FROM ensembl_gene g
        LEFT JOIN ensembl_xref disp_x ON g.display_xref_id = disp_x.xref_id
        LEFT JOIN mapped_xrefs mx ON mx.internal_id = g.gene_id AND mx.ensembl_object_type = 'Gene'
        WHERE g.stable_id IS NOT NULL
        GROUP BY g.stable_id
        ON CONFLICT (ensembl_id) DO NOTHING;
    """)

    # Insert Transcripts
    logger.info("Ingesting Transcripts...")
    conn.execute("""
        INSERT INTO master_bioentity (ensembl_id, entity_type, internal_transcript_id, internal_gene_id, refseq_ids)
        SELECT
            t.stable_id as ensembl_id,
            'Transcript' as entity_type,
            MAX(t.transcript_id) as internal_transcript_id,
            MAX(t.gene_id) as internal_gene_id,
            array_agg(DISTINCT mx.dbprimary_acc) FILTER (WHERE mx.db_name LIKE 'RefSeq_%') as refseq_ids
        FROM ensembl_transcript t
        LEFT JOIN mapped_xrefs mx ON mx.internal_id = t.transcript_id AND mx.ensembl_object_type = 'Transcript'
        WHERE t.stable_id IS NOT NULL
        GROUP BY t.stable_id
        ON CONFLICT (ensembl_id) DO NOTHING;
    """)

    # Insert Proteins
    logger.info("Ingesting Proteins...")
    conn.execute("""
        INSERT INTO master_bioentity (ensembl_id, entity_type, internal_translation_id, internal_transcript_id, uniprot_ids)
        SELECT
            p.stable_id as ensembl_id,
            'Protein' as entity_type,
            MAX(p.translation_id) as internal_translation_id,
            MAX(p.transcript_id) as internal_transcript_id,
            array_agg(DISTINCT mx.dbprimary_acc) FILTER (WHERE mx.db_name  LIKE 'Uniprot/%') as uniprot_ids
        FROM ensembl_translation p
        LEFT JOIN mapped_xrefs mx ON mx.internal_id = p.translation_id AND mx.ensembl_object_type = 'Translation'
        WHERE p.stable_id IS NOT NULL
        GROUP BY p.stable_id
        ON CONFLICT (ensembl_id) DO NOTHING;
    """)

    logger.success("Master bioentity ingestion complete.")


def build_master_disease(conn: duckdb.DuckDBPyConnection):
    """
    Builds master_disease centered on MONDO IDs.
    Loads standard cross-references from Pharmaprojects disease annotations.
    """
    logger.info("Building master_disease...")

    conn.execute("""
        CREATE OR REPLACE TABLE master_disease (
            mondo_id VARCHAR PRIMARY KEY,
            name VARCHAR,
            mesh_ids VARCHAR[],
            icd10_codes VARCHAR[],
            icd9_codes VARCHAR[],
            ncit_codes VARCHAR[],
            omim_ids VARCHAR[],
            efo_ids VARCHAR[],
            doid_ids VARCHAR[],
            orphanet_ids VARCHAR[],
            sctid_codes VARCHAR[],
            umls_cuis VARCHAR[],
            gard_ids VARCHAR[]
        );
    """)

    pharma_disease_path = (
        PHARMAPROJECTS_DIR / "processed" / "identifiers" / "disease_annotations.tsv"
    )

    if pharma_disease_path.exists():
        logger.debug(
            f"Loading Pharmaprojects disease annotations from {pharma_disease_path}..."
        )
        query = f"""
            INSERT INTO master_disease (
                mondo_id, name,
                mesh_ids, icd10_codes, icd9_codes, ncit_codes,
                omim_ids, efo_ids, doid_ids, orphanet_ids,
                sctid_codes, umls_cuis, gard_ids
            )
            SELECT
                MONDO_ID as mondo_id,
                Name as name,
                string_split(MESH, '|') as mesh_ids,
                string_split(ICD10_terms, '|') as icd10_codes,
                string_split(ICD9_terms, '|') as icd9_codes,
                string_split(NCIT, '|') as ncit_codes,
                string_split(OMIM, '|') as omim_ids,
                string_split(EFO, '|') as efo_ids,
                string_split(DOID, '|') as doid_ids,
                string_split(Orphanet, '|') as orphanet_ids,
                string_split(SCTID, '|') as sctid_codes,
                string_split(UMLS, '|') as umls_cuis,
                string_split(GARD, '|') as gard_ids
            FROM read_csv('{pharma_disease_path}', header=True, sep='\\t', quote='', ignore_errors=true, null_padding=true)
            WHERE MONDO_ID IS NOT NULL
            -- In case of multiple rows for same MONDO, take first
            QUALIFY ROW_NUMBER() OVER (PARTITION BY MONDO_ID) = 1;
        """
        try:
            conn.execute(query)
            logger.success("Ingested disease annotations into master_disease.")
        except Exception as e:
            logger.error(f"Failed loading disease annotations: {e}")
    else:
        logger.warning(
            f"Map file {pharma_disease_path} not found. master_disease will be empty."
        )


def build_master_chemical(conn: duckdb.DuckDBPyConnection):
    """
    Builds master_chemical utilizing PubChem CID as the primary key.
    Loads standard cross-references from Pharmaprojects drugs_annotations.tsv.
    """
    logger.info("Building master_chemical...")

    conn.execute("""
        CREATE OR REPLACE TABLE master_chemical (
            pubchem_cid VARCHAR PRIMARY KEY,
            name VARCHAR,
            drugbank_ids VARCHAR[],
            ttd_ids VARCHAR[],
            cas_nums VARCHAR[],
            chembl_ids VARCHAR[],
            zinc_ids VARCHAR[],
            chebi_ids VARCHAR[],
            kegg_cids VARCHAR[],
            kegg_ids VARCHAR[],
            bindingdb_ids VARCHAR[],
            umls_cuis VARCHAR[],
            stitch_ids VARCHAR[]
        );
    """)

    pharma_drugs_path = (
        PHARMAPROJECTS_DIR / "processed" / "identifiers" / "drugs_annotations.tsv"
    )

    if pharma_drugs_path.exists():
        logger.debug(
            f"Loading Pharmaprojects drugs annotations via Pandas from {pharma_drugs_path}..."
        )

        try:
            df = pd.read_csv(
                pharma_drugs_path,
                sep="\\t",
                dtype=str,
                keep_default_na=False,
                on_bad_lines="skip",
                engine="python",
            )

            query = """
                INSERT INTO master_chemical (
                    pubchem_cid, name,
                    drugbank_ids, ttd_ids, cas_nums, chembl_ids, zinc_ids,
                    chebi_ids, kegg_cids, kegg_ids, bindingdb_ids, umls_cuis, stitch_ids
                )
                SELECT
                    pubchem_cid,
                    name,
                    string_split(drugbankId, '|') as drugbank_ids,
                    string_split(ttd_id, '|') as ttd_ids,
                    string_split(cas_num, '|') as cas_nums,
                    string_split(chembl_id, '|') as chembl_ids,
                    string_split(zinc_id, '|') as zinc_ids,
                    string_split(chebi_id, '|') as chebi_ids,
                    string_split(kegg_cid, '|') as kegg_cids,
                    string_split(kegg_id, '|') as kegg_ids,
                    string_split(bindingDB_id, '|') as bindingdb_ids,
                    string_split(UMLS_cuis, '|') as umls_cuis,
                    string_split(stitch_id, '|') as stitch_ids
                FROM df
                WHERE pubchem_cid IS NOT NULL AND pubchem_cid != ''
                QUALIFY ROW_NUMBER() OVER (PARTITION BY pubchem_cid ORDER BY name) = 1;
            """
            conn.execute(query)
            logger.success("Ingested chemical annotations into master_chemical.")
        except Exception as e:
            logger.error(f"Failed loading chemical annotations: {e}")
    else:
        logger.warning(
            f"Map file {pharma_drugs_path} not found. master_chemical will be empty."
        )


def build_variant_identifiers(conn: duckdb.DuckDBPyConnection):
    """
    Builds variant_identifiers using Open Targets Variant indices.
    """
    logger.info("Building variant_identifiers...")

    conn.execute("""
        CREATE OR REPLACE TABLE variant_identifiers (
            rsid VARCHAR PRIMARY KEY,
            ot_variant_id VARCHAR,
            chromosome VARCHAR,
            position INTEGER,
            reference VARCHAR,
            alternate VARCHAR
        );
    """)

    if OT_VARIANT_DIR.exists():
        logger.debug(f"Loading Open Targets variants from {OT_VARIANT_DIR}/*.parquet...")

        query = f"""
            INSERT INTO variant_identifiers (
                rsid, ot_variant_id, chromosome, position, reference, alternate
            )
            SELECT
                COALESCE(rsIds[1], variantId) as rsid,
                variantId as ot_variant_id,
                chromosome,
                position,
                referenceAllele as reference,
                alternateAllele as alternate
            FROM read_parquet('{OT_VARIANT_DIR}/*.parquet')
            WHERE variantId IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY COALESCE(rsIds[1], variantId)) = 1;
        """
        try:
            conn.execute(query)
            logger.success("Ingested variant annotations into variant_identifiers.")
        except Exception as e:
            logger.error(f"Failed loading variant annotations: {e}")
    else:
        logger.warning(f"Map directory {OT_VARIANT_DIR} not found. variant_identifiers will be empty.")


def create_v_translate_id(conn: duckdb.DuckDBPyConnection):
    """
    Creates a unified SQL View `v_translate_id` that maps input IDs of ANY TYPE
    to their canonical identifier (Ensembl for Biomolecules, MONDO for Disease, PubChem for Chemicals).
    """
    logger.info("Creating v_translate_id resolution view...")

    query = """
        CREATE OR REPLACE VIEW v_translate_id AS

        -- BE: Ensembl (Self map)
        SELECT ensembl_id as input_id, ensembl_id as canonical_id, 'Ensembl' as id_type, entity_type as canonical_type FROM master_bioentity
        UNION ALL
        -- BE: HGNC
        SELECT hgnc_id as input_id, ensembl_id as canonical_id, 'HGNC' as id_type, entity_type as canonical_type FROM master_bioentity WHERE hgnc_id IS NOT NULL
        UNION ALL
        -- BE: Symbol
        SELECT symbol as input_id, ensembl_id as canonical_id, 'Symbol' as id_type, entity_type as canonical_type FROM master_bioentity WHERE symbol IS NOT NULL
        UNION ALL
        -- BE: Entrez
        SELECT entrez_id as input_id, ensembl_id as canonical_id, 'Entrez' as id_type, entity_type as canonical_type FROM master_bioentity WHERE entrez_id IS NOT NULL
        UNION ALL
        -- BE: UniProt (Array)
        SELECT UNNEST(uniprot_ids) as input_id, ensembl_id as canonical_id, 'UniProt' as id_type, entity_type as canonical_type FROM master_bioentity WHERE uniprot_ids IS NOT NULL
        UNION ALL
        -- BE: RefSeq (Array)
        SELECT UNNEST(refseq_ids) as input_id, ensembl_id as canonical_id, 'RefSeq' as id_type, entity_type as canonical_type FROM master_bioentity WHERE refseq_ids IS NOT NULL

        UNION ALL

        -- DIS: MONDO self-map
        SELECT mondo_id as input_id, mondo_id as canonical_id, 'MONDO' as id_type, 'Disease' as canonical_type FROM master_disease
        UNION ALL
        -- DIS: DOID (Array)
        SELECT UNNEST(doid_ids) as input_id, mondo_id as canonical_id, 'DOID' as id_type, 'Disease' as canonical_type FROM master_disease WHERE doid_ids IS NOT NULL
        UNION ALL
        -- DIS: EFO (Array)
        SELECT UNNEST(efo_ids) as input_id, mondo_id as canonical_id, 'EFO' as id_type, 'Disease' as canonical_type FROM master_disease WHERE efo_ids IS NOT NULL
        UNION ALL
        -- DIS: MESH (Array)
        SELECT UNNEST(mesh_ids) as input_id, mondo_id as canonical_id, 'MESH' as id_type, 'Disease' as canonical_type FROM master_disease WHERE mesh_ids IS NOT NULL

        UNION ALL

        -- CHEM: PubChem self-map
        SELECT pubchem_cid as input_id, pubchem_cid as canonical_id, 'PubChem' as id_type, 'Chemical' as canonical_type FROM master_chemical
        UNION ALL
        -- CHEM: ChEMBL (Array)
        SELECT UNNEST(chembl_ids) as input_id, pubchem_cid as canonical_id, 'ChEMBL' as id_type, 'Chemical' as canonical_type FROM master_chemical WHERE chembl_ids IS NOT NULL
        UNION ALL
        -- CHEM: DrugBank (Array)
        SELECT UNNEST(drugbank_ids) as input_id, pubchem_cid as canonical_id, 'DrugBank' as id_type, 'Chemical' as canonical_type FROM master_chemical WHERE drugbank_ids IS NOT NULL

        UNION ALL

        -- VAR: rsID self-map
        SELECT rsid as input_id, rsid as canonical_id, 'rsID' as id_type, 'Variant' as canonical_type FROM variant_identifiers
        UNION ALL
        -- VAR: OT Variant ID
        SELECT ot_variant_id as input_id, rsid as canonical_id, 'OT_Variant' as id_type, 'Variant' as canonical_type FROM variant_identifiers WHERE ot_variant_id IS NOT NULL
        ;
    """
    try:
        conn.execute(query)
        logger.success("Created v_translate_id view.")
    except Exception as e:
        logger.error(f"Failed to create v_translate_id: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Compile unified Bioregistry using DuckDB and Native Ensembl MySQL dumps"
    )
    parser.add_argument(
        "--db", type=str, default=str(DB_PATH), help="Path to bioregistry.db"
    )
    args = parser.parse_args()

    conn = duckdb.connect(args.db)
    logger.info(f"Connected to DuckDB: {args.db}")

    build_master_bioentity(conn)
    build_master_disease(conn)
    build_master_chemical(conn)
    build_variant_identifiers(conn)

    create_v_translate_id(conn)

    # Validation count
    res_bio = conn.execute("SELECT COUNT(*) FROM master_bioentity").fetchone()
    logger.info(f"Rows in master_bioentity: {res_bio[0]}")
    res_dis = conn.execute("SELECT COUNT(*) FROM master_disease").fetchone()
    logger.info(f"Rows in master_disease: {res_dis[0]}")
    res_chem = conn.execute("SELECT COUNT(*) FROM master_chemical").fetchone()
    logger.info(f"Rows in master_chemical: {res_chem[0]}")
    res_var = conn.execute("SELECT COUNT(*) FROM variant_identifiers").fetchone()
    logger.info(f"Rows in variant_identifiers: {res_var[0]}")

    res_v = conn.execute("SELECT COUNT(*) FROM v_translate_id").fetchone()
    logger.info(f"Total mappings in v_translate_id: {res_v[0]}")
    conn.close()

if __name__ == "__main__":
    main()
