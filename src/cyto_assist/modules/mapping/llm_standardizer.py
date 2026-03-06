"""
LLM Standardizer — Maps unstructured text entities to canonical PKG 2.0/OLS4 nodes.

This module provides tools to take raw entity mentions extracted from papers
(via GROBID, layout parsers, or other LLMs) and map them to standard biological
terminologies (e.g., HGNC, MONDO, ChEBI) or matching OLS4 ontology nodes.
"""

import json
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field


class EntityCategory(str, Enum):
    GENE_PROTEIN = "gene/protein"
    DISEASE = "disease"
    CHEMICAL = "drug/chemical"
    SPECIES = "species"
    CELL_LINE = "cell_line"
    CELL_TYPE = "cell_type"
    PHENOTYPE = "phenotype"


class StandardizedEntity(BaseModel):
    original_mention: str = Field(description="The raw text extracted from the document.")
    category: EntityCategory = Field(description="The classified biological category.")
    suggested_canonical_name: str = Field(description="The standardized name (e.g. HGNC symbol).")
    suggested_ontology_id: Optional[str] = Field(None, description="The canonical ID (e.g., NCBIGene:7157, MONDO:0005090).")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score of the mapping.")


class StandardizationResponse(BaseModel):
    entities: List[StandardizedEntity]


class LLMStandardizer:
    """
    Standardizes biomedical constructs using an LLM.
    Currently stubbed out to be connected to the cytognosis LLM utility/router.
    """

    def __init__(self, model_name: str = "gemini-2.5-pro", temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature

    def _build_prompt(self, raw_mentions: List[str]) -> str:
        return f"""
        You are an expert biomedical ontological mapping assistant.
        Given the following raw entity mentions extracted from a scientific paper,
        standardize them into canonical categories and IDs corresponding to the PKG 2.0 schema:

        - Gene/Protein -> NCBIGene or HGNC
        - Disease -> MONDO
        - Chemical -> ChEBI or MeSH
        - Species -> NCBITaxon
        - Cell Line -> cellosaurus
        - Cell Type -> CL
        - Phenotype -> HPO

        Mentions to map:
        {json.dumps(raw_mentions, indent=2)}

        Please return a strictly formatted JSON array of standardized entities.
        """

    def standardize_batch(self, raw_mentions: List[str]) -> StandardizationResponse:
        """
        Sends raw annotations to the LLM to retrieve standardized nodes.
        Note: Actual LLM provider call is simulated here.
        """
        logger.info(f"Sending {len(raw_mentions)} mentions to {self.model_name} for standardization...")

        # TODO: Replace with actual async LLM call (e.g. google.genai, litellm, etc.)
        # result = llm_client.generate_object(self._build_prompt(raw_mentions), response_model=StandardizationResponse)

        # Simulated response for demonstration
        simulated = []
        for rm in raw_mentions:
            if "p53" in rm.lower() or "tp53" in rm.lower():
                simulated.append(StandardizedEntity(original_mention=rm, category=EntityCategory.GENE_PROTEIN, suggested_canonical_name="TP53", suggested_ontology_id="NCBIGene:7157", confidence=0.99))
            elif "schizophrenia" in rm.lower():
                simulated.append(StandardizedEntity(original_mention=rm, category=EntityCategory.DISEASE, suggested_canonical_name="Schizophrenia", suggested_ontology_id="MONDO:0005090", confidence=0.95))
            else:
                simulated.append(StandardizedEntity(original_mention=rm, category=EntityCategory.PHENOTYPE, suggested_canonical_name=rm.title(), confidence=0.5))

        logger.success(f"Standardized {len(simulated)} entities.")
        return StandardizationResponse(entities=simulated)

if __name__ == "__main__":
    standardizer = LLMStandardizer()
    res = standardizer.standardize_batch(["P53 gene", "Patients with severe schizophrenia", "headache"])
    print(res.model_dump_json(indent=2))
