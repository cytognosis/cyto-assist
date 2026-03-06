"""
OLS Harmonizer — Mappings for assigning structured ontology endpoints post-import.

Interacts with the OLS4 public API or local Neo4j database to fetch standard
ontology concepts (like DOID, MONDO, NCBITaxon) for biological terms.
"""

from typing import Any, Dict, List, Optional
import requests
from loguru import logger

class OLSHarmonizer:
    def __init__(self, api_url: str = "https://www.ebi.ac.uk/ols4/api/search"):
        self.api_url = api_url

    def search_term(self, term: str, ontology: Optional[str] = None, exact: bool = False) -> List[Dict[str, Any]]:
        """Search OLS4 for the best matching ontology terms."""
        params = {
            "q": term,
            "rows": 5,
            "exact": "true" if exact else "false"
        }
        if ontology:
            params["ontology"] = ontology.lower()

        try:
            resp = requests.get(self.api_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            docs = data.get("response", {}).get("docs", [])

            return [
                {
                    "label": d.get("label"),
                    "obo_id": d.get("obo_id"),
                    "ontology": d.get("ontology_prefix"),
                    "description": d.get("description", [""])[0] if d.get("description") else None,
                    "score": d.get("score")
                }
                for d in docs
            ]
        except Exception as e:
            logger.error(f"OLS4 Search failed for '{term}': {e}")
            return []

    def harmonize(self, raw_term: str, expected_type: str) -> Optional[Dict[str, Any]]:
        """High-level harmonization helper. Routes expected_type to relevant ontology."""
        ontology_map = {
            "disease": "mondo",
            "phenotype": "hp",
            "cell_type": "cl",
            "anatomy": "uberon",
            "chemical": "chebi",
            "species": "ncbitaxon"
        }

        target_ont = ontology_map.get(expected_type.lower())
        results = self.search_term(raw_term, ontology=target_ont, exact=False)

        if results:
            best_match = results[0]
            logger.info(f"Harmonized '{raw_term}' -> {best_match['label']} ({best_match['obo_id']})")
            return best_match

        logger.warning(f"Could not harmonize '{raw_term}'")
        return None

if __name__ == "__main__":
    harmonizer = OLSHarmonizer()
    print(harmonizer.harmonize("schizophrenia", "disease"))
    print(harmonizer.harmonize("astrocyte", "cell_type"))
