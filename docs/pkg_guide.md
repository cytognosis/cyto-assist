# PubMed Knowledge Graph 2.0 (PKG) — Comprehensive Reference

> **Paper:** Xu et al. (2025). *PubMed knowledge graph 2.0: Connecting papers, patents, and clinical trials in biomedical science.* Scientific Data, 12, 253.
> **DOI:** [10.1038/s41597-025-05343-8](https://doi.org/10.1038/s41597-025-05343-8)
> **Data:** [Figshare](https://doi.org/10.6084/m9.figshare.c.7007587) | [GitHub](https://PubMedKG.github.io)

---

## 1. Overview

PKG 2.0 connects three pillars of biomedical scholarly communication:

| Source | Description | Count |
|--------|-------------|-------|
| **PubMed** | Academic papers | 36.5M |
| **ClinicalTrials.gov** | Clinical trial records | 480K |
| **USPTO/PatentsView** | Biomedical patents | 1.3M |

Connections established through:

- **Biomedical entities** (NER via BERN2) — 9 types: gene/protein, disease, drug/chemical, species, mutation, cell line, cell type, DNA, RNA
- **Citations** — paper→paper, paper↔patent, paper↔trial, patent↔trial
- **Author disambiguation** — unified author IDs across all sources
- **NIH projects** — grants linking papers to PIs
- **Institutions** — disambiguated affiliations with geo-coordinates

## 2. Schema & Data Files

### Node Tables

| File | Description | Rows | Size | Key Fields |
|------|-------------|------|------|------------|
| `C01_Papers.tsv` | PubMed articles | 36.5M | 5.4G | PMID, PubYear, ArticleTitle, CitedCount, IsClinicalArticle, IsResearchArticle |
| `C07_Authors.tsv` | Disambiguated authors | 26.2M | 570M | AID, BeginYear, RecentYear, PaperNum, h_index |
| `C11_ClinicalTrials.tsv` | Clinical trials | 480K | 1.1G | nct_id, phase, overall_status, conditions, brief_title |
| `C15_Patents.tsv` | USPTO patents | 1.3M | 978M | PatentId, GrantedDate, Title, Abstract, ClaimNum |
| `C23_BioEntities.tsv` | Unique bio-entities | 360K | 15M | EntityId, Type, Mention |

### Relationship Tables

| File | Description | Rows | Size | Key Fields |
|------|-------------|------|------|------------|
| `C02_Link_Papers_Authors.tsv` | Paper↔Author | 160.8M | 5.4G | PMID, AID, AuthorOrder |
| `C03_Affiliations.tsv.gz` | Author affiliations | 96.3M | 4.5G | PMID, AID, Institution, Grid, Country, Lat/Lon |
| `C04_ReferenceList_Papers.tsv.gz` | Paper citations | 774.8M | 3.8G | PMID, RefPMID |
| `C05_PIs.tsv` | Paper↔PI/Project | 53.4M | 3.0G | PMID, PI_ID, Project_Number, AID |
| `C06_Link_Papers_BioEntities.tsv.gz` | Paper↔BioEntity | 464.6M | 12G | PMID, EntityId, Type, Mention |
| `C10_Link_Papers_Journals.tsv` | Paper↔Journal | 29.2M | 5.6G | PMID, Journal_ISSN, SJR, H-index |
| `C12_Link_Papers_Clinicaltrials.tsv` | Paper↔Trial | 968K | 44M | PMID, nct_id |
| `C13_Link_ClinicalTrials_BioEntities.tsv` | Trial↔BioEntity | 11.4M | 1.4G | nct_id, EntityId, Type |
| `C14_Investigators.tsv` | Trial investigators | 586K | 82M | nct_id, AID, Role |
| `C16_Link_Patents_Papers.tsv` | Patent→Paper citations | 18.2M | 791M | PatentId, PMID, ConfScore |
| `C17_Assignees.tsv` | Patent assignees | 1.3M | 121M | patent_id, assignee_id |
| `C18_Link_Patents_BioEntities.tsv` | Patent↔BioEntity | 6.5M | 688M | PatentId, EntityId, Type |
| `C19_Inventors.tsv` | Patent inventors | 4.1M | 379M | patent_id, AID |
| `C21_Bioentity_Relationships.tsv` | Entity-entity relations | 61.8M | 5.0G | entity_id1, entity_id2, relation_type |
| `C22_DatasetMethod.tsv` | Dataset/method mentions | 4.4M | 200M | PMID, Mention, Entity, Type |
| `C24_Link_Clinicaltrials_Patents.tsv` | Trial↔Patent | 27K | 708K | nct_id, PatentId |

**Total: ~1.73 billion rows, ~50 GB**

## 3. Entity Types (BERN2 NER)

| Type | Normalized ID Format | Example |
|------|---------------------|---------|
| Gene/Protein | NCBIGene:ID | NCBIGene:7157 (TP53) |
| Disease | mesh:ID, OMIM:ID | mesh:D012559 (Schizophrenia) |
| Drug/Chemical | mesh:ID, CHEBI:ID | mesh:D000082 (Acetaminophen) |
| Species | NCBITaxon:ID | NCBITaxon:9606 (Homo sapiens) |
| Mutation | tmVar format | p.V600E |
| Cell Line | cellosaurus:ID | cellosaurus:CVCL_0030 (HeLa) |
| Cell Type | CL:ID | CL:0000236 (B cell) |
| DNA | — | — |
| RNA | — | — |

## 4. Graph Model (Neo4j)

```
(:Paper {pmid, title, year, cited_count, ...})
  -[:AUTHORED_BY {order}]-> (:Author {aid, h_index, ...})
  -[:CITES]-> (:Paper)
  -[:MENTIONS {start, end, type}]-> (:BioEntity {id, type, name})
  -[:PUBLISHED_IN]-> (:Journal {issn, sjr, ...})
  -[:LINKED_TO]-> (:ClinicalTrial {nct_id, phase, ...})
  -[:FUNDED_BY]-> (:Project {number, pi_id})

(:Patent {patent_id, title, ...})
  -[:CITES_PAPER]-> (:Paper)
  -[:MENTIONS]-> (:BioEntity)
  -[:INVENTED_BY]-> (:Author)

(:BioEntity)-[:INTERACTS_WITH {relation_type}]->(:BioEntity)
```

## 5. Loading Strategy

Given the 50GB / 1.7B row scale, recommended approach:

1. **DuckDB** for initial exploration and filtering (reads TSV/gzipped natively)
2. **Polars** for streaming transformation (lazy evaluation, out-of-core)
3. **Neo4j `neo4j-admin import`** for bulk loading (much faster than Cypher INSERT)

### Import Order (dependency resolution)

1. Node files first: `C23_BioEntities` → `C07_Authors` → `C01_Papers` → `C11_ClinicalTrials` → `C15_Patents`
2. Then relationship files in any order

### Memory-Efficient DuckDB Queries

```sql
-- Query without loading into memory
SELECT * FROM read_csv_auto('/path/to/C01_Papers.tsv', delim='\t') LIMIT 10;

-- Count entities by type
SELECT Type, count(*) AS cnt
FROM read_csv_auto('/path/to/C23_BioEntities.tsv', delim='\t')
GROUP BY Type ORDER BY cnt DESC;

-- Filter papers by citation count
SELECT PMID, ArticleTitle, CitedCount
FROM read_csv_auto('/path/to/C01_Papers.tsv', delim='\t')
WHERE CitedCount > 1000
ORDER BY CitedCount DESC LIMIT 50;
```

## 6. Key Mappings to Our Ontologies

| PKG Entity Type | Ontology | Our Ontology File |
|----------------|----------|-------------------|
| Disease (mesh) | MeSH → MONDO | `mondo/ontology/mondo.owl` |
| Cell Type (CL) | Cell Ontology | OLS4 / CellxGene |
| Cell Line (cellosaurus) | Cellosaurus | `cellosaurus/` |
| Species (NCBITaxon) | NCBI Taxonomy | OLS4 |
| Gene/Protein | NCBI Gene | External API |
| Drug/Chemical (CHEBI) | ChEBI | OLS4 |
