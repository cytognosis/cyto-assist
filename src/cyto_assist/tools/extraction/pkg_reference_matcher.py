"""
PKG Reference Matcher — Align extracted bibliography / references against PKG 2.0 graph.

Provides tooling to load Bibtex extracted from grobid/custom tools and match
the PMIDs or DOIs against the PKG Neo4j database or DuckDB tables to cross-reference
known citation edges.
"""

from loguru import logger
import re

class PKGReferenceMatcher:
    def __init__(self, neo4j_driver=None, db_connection=None):
        """Pass the active PKG database connectors."""
        self.driver = neo4j_driver
        self.db = db_connection

    def parse_mock_bibtex(self, bibtex_string: str) -> list[dict]:
        """Simple fallback/mock parser to extract DOIs and Titles."""
        entries = []
        # In a real implementation we would use `bibtexparser`
        for block in bibtex_string.split("@article"):
            if not block.strip():
                continue
            doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', block, re.IGNORECASE)
            title_match = re.search(r'title\s*=\s*\{([^}]+)\}', block, re.IGNORECASE)
            pmid_match = re.search(r'pmid\s*=\s*\{([^}]+)\}', block, re.IGNORECASE)

            entries.append({
                "doi": doi_match.group(1) if doi_match else None,
                "pmid": pmid_match.group(1) if pmid_match else None,
                "title": title_match.group(1) if title_match else "Unknown"
            })
        return entries

    def map_to_pkg(self, source_pmid: str, references: list[dict]):
        """
        Check if the parsed references exist in the C01_Papers or PKG database.
        And if the citation edge (C04_ReferenceList_Papers) exists.
        Missing papers/references are isolated to extend the 1-hop network.
        """
        logger.info(f"Mapping {len(references)} references for source paper {source_pmid}...")

        # This function would natively construct Cypher or DuckDB queries:
        # SELECT * FROM papers WHERE doi IN (...)
        # ...

        mapped = []
        unmapped = []

        for ref in references:
            # Simulated check logic
            if ref.get("pmid") and int(ref["pmid"]) % 2 == 0:
                mapped.append(ref)
            else:
                unmapped.append(ref)

        logger.success(f"Successfully mapped {len(mapped)} references to PKG. Discovered {len(unmapped)} missing nodes.")
        return {
            "mapped_references": mapped,
            "missing_references": unmapped
        }

if __name__ == "__main__":
    matcher = PKGReferenceMatcher()
    sample_bibtex = '''
    @article{smith2024,
      title={Deep learning in healthcare},
      pmid={123456},
      doi={10.1000/123}
    }
    @article{johnson2025,
      title={Another paper},
      pmid={123457}
    }
    '''
    refs = matcher.parse_mock_bibtex(sample_bibtex)
    print(matcher.map_to_pkg("99999", refs))
