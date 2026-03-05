# Openness Integration for Grant Proposals

Reusable "answer blocks" extracted from Cytognosis's [Commitment to Openness](file:///home/mohammadi/repos/cytognosis/agents/docs/materials/Commitment_to_Openness.md) for use in proposals that evaluate open science, open source, and FAIR data practices.

---

## When to Use

Include openness commitments in proposals for funders that explicitly evaluate or prefer them:

| Funder | What They Want | Which Block to Use |
|--------|----------------|-------------------|
| **NSF Tech Labs** | Open-science mission alignment | Full 3 pillars + FAIR |
| **Convergent Research** | Open Science Commitment section | 3 pillars + Why permissive licenses |
| **Foresight Institute** | Preference for open source | Open Source pillar summary |
| **Astera Institute** | Open science ethos | 3 pillars + FAIR |
| **ARPA-H** | Software component standards, open-source preferred | Open Source pillar + license table |
| **EA (LTFF)** | Not scored, but supports credibility | Brief mention |

---

## Block 1: Three Pillars Summary (150 words)

> Cytognosis Foundation builds in the open because the tools to intercept disease years before symptoms should belong to humanity, not shareholders. Our commitment rests on three pillars:
>
> **Open Science**: All research is published open access (preprints on bioRxiv/arXiv before journal submission), with preregistered studies, open protocols, and full reproducibility.
>
> **Open Source**: All software is released under Apache 2.0 (patent grant, attribution, broad compatibility) on public GitHub from the first commit. Development happens in public.
>
> **Open Models**: All AI/ML weights, training code, hyperparameters, training logs, and evaluation frameworks are published on Hugging Face with model cards documenting intended use, limitations, and biases.

---

## Block 2: FAIR Implementation (100 words)

> We implement the FAIR Guiding Principles (Wilkinson et al., 2016):
>
> - **Findable**: All assets receive DOIs via Zenodo with machine-readable metadata
> - **Accessible**: Retrievable via HTTPS/REST APIs; no proprietary software required
> - **Interoperable**: Using standard ontologies (Gene Ontology, HPO, SNOMED CT) and open formats (Parquet, AnnData, ONNX)
> - **Reusable**: Clear licenses, detailed provenance, domain-relevant community standards
>
> Health data with privacy constraints uses controlled access + synthetic equivalents + full metadata, per our principle: "as open as possible, as restricted as necessary."

---

## Block 3: License Selection Table

| Artifact Type | License | Rationale |
|:---|:---|:---|
| Software / Libraries | Apache 2.0 | Patent grant, attribution, broad compatibility |
| Lightweight scripts | MIT | Simplicity, maximum adoption |
| Documentation | CC BY 4.0 | Any reuse with attribution |
| Research data (non-personal) | CC BY 4.0 | Open scientific data standard |
| Research data (health) | Controlled access + CC BY-NC 4.0 metadata | Ethical constraints, DUA required |
| AI/ML model weights | Apache 2.0 | Consistent with code, patent protections |
| Preprints / Publications | CC BY 4.0 | Gold open access standard |

---

## Block 4: Why Permissive (Not Copyleft) Licenses (75 words)

> We deliberately choose permissive over copyleft licenses. Our mission is to maximize adoption of tools that intercept disease. Copyleft (GPL) creates friction for downstream adoption in healthcare systems, regulatory environments, and commercial partners whose participation is essential for bringing tools to patients. Our open core stays permanently open under irrevocable licenses — any researcher, company, or government has the same access as any Cytognosis subsidiary.

---

## Block 5: Nonprofit-to-Commercial Pathway (100 words)

> As a 501(c)(3) nonprofit FRO, Cytognosis may eventually involve for-profit subsidiaries (PBCs) for scale. Our principles:
>
> 1. **The open core stays open** — permanently, irrevocably
> 2. **Commercial value comes from services, not restrictions** — hosted SaaS, regulatory-grade validation, clinical decision support with SLAs
> 3. **Licensing flows one direction** — the nonprofit licenses openly to the world; subsidiaries get the same access as everyone else
> 4. **Revenue supports the mission** — flowing back to the foundation via licensing fees or charitable contributions
