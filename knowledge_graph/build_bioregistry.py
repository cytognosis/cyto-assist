import argparse
from pathlib import Path

import duckdb
import pandas as pd
from loguru import logger

# Paths setup
DATA_DIR = Path("/home/mohammadi/datasets")
IDENTIFIERS_DIR = DATA_DIR / "identifiers" / "databases"
PHARMAPROJECTS_DIR = DATA_DIR / "network" / "public" / "clinical" / "Pharmaprojects"
STITCH_DIR = DATA_DIR / "network" / "public" / "clinical" / "STITCH"
DB_PATH = Path("bioregistry.db")

OT_VARIANT_DIR = DATA_DIR / "network" / "public" / "kg" / "open_targets" / "25.03" / "variant"

HGNC_PATH = IDENTIFIERS_DIR / "HUGO" / "hgnc_complete_set.txt"
ENSEMBL_CANONICAL = (
    IDENTIFIERS_DIR
    / "ensembl"
    / "tsv"
    / "homo_sapiens"
    / "Homo_sapiens.GRCh38.113.canonical.tsv.gz"
)
ENSEMBL_UNIPROT = (
    IDENTIFIERS_DIR
    / "ensembl"
    / "tsv"
    / "homo_sapiens"
    / "Homo_sapiens.GRCh38.113.uniprot.tsv.gz"
)

# HGNC fields (44 columns + our added ones)
HGNC_COLUMNS = [
    "hgnc_id",
    "symbol",
    "name",
    "locus_group",
    "locus_type",
    "status",
    "location",
    "location_sortable",
    "alias_symbol",
    "alias_name",
    "prev_symbol",
    "prev_name",
    "gene_group",
    "gene_group_id",
    "date_approved_reserved",
    "date_symbol_changed",
    "date_name_changed",
    "date_modified",
    "entrez_id",
    "ensembl_gene_id",
    "vega_id",
    "ucsc_id",
    "ena",
    "refseq_accession",
    "ccds_id",
    "uniprot_ids",
    "pubmed_id",
    "mgd_id",
    "rgd_id",
    "lsdb",
    "cosmic",
    "omim_id",
    "mirbase",
    "homeodb",
    "snornabase",
    "bioparadigms_slc",
    "orphanet",
    "pseudogene_org",
    "horde_id",
    "merops",
    "imgt",
    "iuphar",
    "kznf_gene_catalog",
    "mamit-trnadb",
    "cd",
    "lncrnadb",
    "enzyme_id",
    "intermediate_filament_db",
    "rna_central_ids",
    "lncipedia",
    "gtrnadb",
    "agr",
]


def build_master_bioentity(conn: duckdb.DuckDBPyConnection):
    """
    Builds the master_bioentity table merging Gene, Transcript, Protein, RNA.
    Prioritizes Ensembl ID as the primary key.
    Reads HGNC mappings directly into the table.
    """
    logger.info("Building master_bioentity...")

    # For fast ingestion, DuckDB can read TSV directly
    # HGNC complete set has 50+ columns. We read it as a view first.
    logger.debug(f"Reading HGNC TSV from {HGNC_PATH}...")

    # 1. Create table schema mapped accurately to HGNC and Ensembl headers
    conn.execute("""
        CREATE OR REPLACE TABLE master_bioentity (
            ensembl_id VARCHAR PRIMARY KEY,  -- ENSG... or ENST... or ENSP...
            entity_type VARCHAR,             -- Gene, Transcript, Protein, ncRNA

            -- Core IDs
            hgnc_id VARCHAR,
            symbol VARCHAR,
            name VARCHAR,
            status VARCHAR,
            entrez_id VARCHAR,
            uniprot_ids VARCHAR,
            refseq_ids VARCHAR,

            -- Aliases & History
            alias_symbols VARCHAR,
            alias_names VARCHAR,
            prev_symbols VARCHAR,
            prev_names VARCHAR,

            -- Chromosomal Map
            chromosome VARCHAR,

            -- External Database Links (Raw ingestion from HGNC)
            locus_type VARCHAR,
            locus_group VARCHAR,
            date_approved VARCHAR,
            date_modified VARCHAR,
            date_symbol_changed VARCHAR,
            date_name_changed VARCHAR,
            enzyme_ids VARCHAR,
            mouse_genome_database_id VARCHAR,
            pubmed_ids VARCHAR,
            gene_group_id VARCHAR,
            gene_group_name VARCHAR,
            ccds_ids VARCHAR,
            vega_ids VARCHAR,
            omim_id VARCHAR,
            ucsc_id VARCHAR,
            rat_genome_database_id VARCHAR,
            lncipedia_id VARCHAR,
            gtrnadb_id VARCHAR,
            agr_hgnc_id VARCHAR,
            mane_select_ensembl VARCHAR,
            mane_select_refseq VARCHAR
        );
    """)

    # We use DuckDB's read_csv natively parsing HGNC taking explicit column names
    # HGNC file might have slightly different names, but read_csv with auto_detect=true works
    # with a select wrapper.
    query = f"""
        INSERT INTO master_bioentity (
            ensembl_id, entity_type, hgnc_id, symbol, name, status,
            entrez_id, uniprot_ids, refseq_ids,
            alias_symbols, alias_names, prev_symbols, prev_names,
            chromosome,
            locus_type, locus_group, date_approved, date_modified,
            date_symbol_changed, date_name_changed, enzyme_ids,
            mouse_genome_database_id, pubmed_ids, gene_group_id, gene_group_name,
            ccds_ids, vega_ids, omim_id, ucsc_id, rat_genome_database_id,
            lncipedia_id, gtrnadb_id, agr_hgnc_id, mane_select_ensembl, mane_select_refseq
        )
        SELECT
            ensembl_gene_id as ensembl_id,
            'Gene' as entity_type,
            hgnc_id,
            symbol,
            name,
            status,
            entrez_id,
            uniprot_ids,
            refseq_accession as refseq_ids,
            alias_symbol as alias_symbols,
            alias_name as alias_names,
            prev_symbol as prev_symbols,
            prev_name as prev_names,
            location as chromosome,
            locus_type,
            locus_group,
            date_approved_reserved as date_approved,
            date_modified,
            date_symbol_changed,
            date_name_changed,
            enzyme_id as enzyme_ids,
            mgd_id as mouse_genome_database_id,
            pubmed_id as pubmed_ids,
            gene_group_id,
            gene_group as gene_group_name,
            ccds_id as ccds_ids,
            vega_id as vega_ids,
            omim_id,
            ucsc_id,
            rgd_id as rat_genome_database_id,
            lncipedia as lncipedia_id,
            gtrnadb as gtrnadb_id,
            agr as agr_hgnc_id,
            mane_select as mane_select_ensembl, -- Note: HGNC mane_select includes both, will just capture it
            NULL as mane_select_refseq
        FROM read_csv('{HGNC_PATH}', header=True, sep='\t', quote='', ignore_errors=true, null_padding=true)
        WHERE ensembl_gene_id IS NOT NULL
        -- Deduplicate if multiple HGNC records point to the same Ensembl ID
        -- By taking the one that is 'Approved' first or lowest HGNC ID
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY ensembl_gene_id
            ORDER BY case when status='Approved' then 0 else 1 end, hgnc_id
        ) = 1;
    """

    try:
        conn.execute(query)
        logger.success("Inserted HGNC entries into master_bioentity.")
    except Exception as e:
        logger.error(f"Failed loading HGNC data: {e}")

    # 2. Ingest Ensembl Canonical Transcripts
    logger.info("Ingesting Canonical Transcripts...")
    query_transcripts = f"""
        INSERT INTO master_bioentity (ensembl_id, entity_type)
        SELECT DISTINCT "Ensembl Canonical" as ensembl_id, 'Transcript' as entity_type
        FROM read_csv('{ENSEMBL_CANONICAL}', header=True, sep='\t', quote='', ignore_errors=true, null_padding=true)
        WHERE "Ensembl Canonical" IS NOT NULL
        ON CONFLICT (ensembl_id) DO NOTHING;
    """
    try:
        conn.execute(query_transcripts)
        logger.success("Ingested Ensembl Transcripts.")
    except Exception as e:
        logger.error(f"Failed loading Transcripts: {e}")

    # 3. Ingest Ensembl Proteins
    logger.info("Ingesting Proteins via Uniprot map...")
    query_proteins = f"""
        INSERT INTO master_bioentity (ensembl_id, entity_type, uniprot_ids)
        SELECT
            protein_stable_id as ensembl_id,
            'Protein' as entity_type,
            string_agg(xref, '|') as uniprot_ids
        FROM read_csv('{ENSEMBL_UNIPROT}', header=True, sep='\t', quote='', ignore_errors=true, null_padding=true)
        WHERE protein_stable_id IS NOT NULL and protein_stable_id != '-'
        GROUP BY protein_stable_id
        ON CONFLICT (ensembl_id) DO NOTHING;
    """
    try:
        conn.execute(query_proteins)
        logger.success("Ingested Ensembl Proteins.")
    except Exception as e:
        logger.error(f"Failed loading Proteins: {e}")


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

    # Pharmaprojects disease_annotations.tsv contains standard xrefs mapped to MONDO
    # Load them natively via DuckDB
    pharma_disease_path = (
        PHARMAPROJECTS_DIR / "processed" / "identifiers" / "disease_annotations.tsv"
    )

    if pharma_disease_path.exists():
        logger.debug(
            f"Loading Pharmaprojects disease annotations from {pharma_disease_path}..."
        )

        # We need to map the flat Pharmaprojects columns to ARRAYs
        # The file columns typically are: MONDO, DOID, EFO, ICD9, ICD10, MESH, NCIT, Orphanet, SCTID, UMLS, GARD, OMIM
        # They might be pipe-separated if multiple. DuckDB's string_split helps.
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
            FROM read_csv('{pharma_disease_path}', header=True, sep='\t', quote='', ignore_errors=true, null_padding=true)
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
    Fields include: drugbankId, ttd_id, cas_num, chembl_id, zinc_id, chebi_id, kegg_cid, kegg_id, bindingDB_id, UMLS_cuis, stitch_id
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
            # Use pandas for robust quoting and escape parsing on messy TSV
            df = pd.read_csv(
                pharma_drugs_path,
                sep="\t",
                dtype=str,
                keep_default_na=False,
                on_bad_lines="skip",
                engine="python",
            )

            # Use DuckDB to load the dataframe nicely
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
    Extracts the master rsID from the rsIds array, falling back to variantId.
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

        # We unpack the first rsID if available, else fallback to variantId
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

    # We build a UNION ALL query taking arrays and flattening them using DuckDB's UNNEST mapping
    query = """
        CREATE OR REPLACE VIEW v_translate_id AS

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
        SELECT UNNEST(string_split(uniprot_ids, '|')) as input_id, ensembl_id as canonical_id, 'UniProt' as id_type, entity_type as canonical_type FROM master_bioentity WHERE uniprot_ids IS NOT NULL

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
        description="Compile unified Bioregistry using DuckDB"
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
