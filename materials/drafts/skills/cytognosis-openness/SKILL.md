---
name: cytognosis-openness
description: >
  Cytognosis Foundation openness policy: open science, open source, open models, FAIR data principles,
  and licensing strategy. Use when choosing licenses for code/data/models, writing grant language about
  open science or FAIR compliance, creating READMEs or CONTRIBUTING.md, discussing nonprofit-to-PBC
  commercial pathway, or referencing FAIR principles. Triggers on: open science, open source, open
  access, FAIR, license, CC BY, Apache 2.0, MIT license, permissive, copyleft, data sharing, OSF,
  preregistration, preprint, reproducibility, DMP, SPDX, REUSE, model card, data card, Hugging Face,
  Zenodo, controlled access, dual licensing, PBC subsidiary, commitment to openness. Cross-references:
  cytognosis-python-standards, cytognosis-brand-identity, cytognosis-grant-writing.
---

# Cytognosis Openness Policy

**Open Science. Open Source. Open Models. Open Future.**

Canonical source for all licensing decisions, FAIR compliance, open science practices, and the
nonprofit-to-commercial pathway for Cytognosis Foundation outputs.

→ For the full commitment statement (board-level document), see `references/commitment-statement.md`
→ For grant-specific open science language, read `cytognosis-grant-writing` after this skill

---

## Core Principle

Everything Cytognosis Foundation produces is **as open as possible and as restricted as necessary,
while always being FAIR.** Openness is not an add-on. It is our mission expressed as practice.

---

## 1. License Quick Reference

| Artifact | Default License | Notes |
|---|---|---|
| Software / Libraries | **Apache 2.0** | Patent grant, attribution, broad compat |
| Scripts / Utilities | **MIT** | Simplicity, max adoption |
| Documentation / Educational | **CC BY 4.0** | Any reuse with attribution |
| Research data (non-personal) | **CC BY 4.0** | Standard open science |
| Research data (health/personal) | **Controlled access** + CC BY-NC 4.0 metadata | DUA required, IRB approval |
| AI/ML model weights | **Apache 2.0** | Consistent with code |
| Training datasets | **CC BY 4.0** or **CC BY-SA 4.0** | Community reciprocity |
| Preprints / Publications | **CC BY 4.0** | Gold open access |
| Brand assets / Logos | **All rights reserved** | Trademark ≠ open source |

### License Selection Rules

1. **Always use OSI-approved licenses for software.** Never use custom, source-available, or proprietary licenses for foundation code.
2. **Always use CC licenses for content/data.** Never use software licenses for non-software.
3. **Every file must have a machine-readable license identifier.** Use SPDX headers and the REUSE specification.
4. **Permissive over copyleft.** We choose Apache 2.0/MIT over GPL to maximize adoption in healthcare, regulatory, and commercial contexts.
5. **No custom license modifications.** We do not create bespoke licenses (like revenue-threshold models). Standard licenses reduce legal friction.

### Why Apache 2.0 (Not MIT) as Default

- Explicit **patent grant** protects contributors and users from patent litigation
- Requires documentation of **changes** (important for auditability in healthcare)
- **Compatible with GPL v3** (if downstream users need copyleft)
- Industry-standard for enterprise and cloud-native projects
- MIT is acceptable for lightweight, utility-level code where patents are not a concern

---

## 2. FAIR Principles Implementation

FAIR (Findable, Accessible, Interoperable, Reusable) guides how we steward digital assets.
Published by Wilkinson et al. in *Scientific Data* (2016), adopted by NIH, EU Horizon, and G20.

**FAIR ≠ Open.** Data can be FAIR without being open (controlled-access health data with rich
metadata). Data can be open without being FAIR (undocumented CSV dump). We require both where possible.

### FAIR Checklist (apply to every release)

**Findable**
- [ ] Persistent identifier assigned (DOI via Zenodo, Hugging Face model ID)
- [ ] Rich machine-readable metadata (schema.org, Dublin Core, domain ontologies)
- [ ] Registered in searchable repository (Zenodo, HF, GEO, CellxGene)

**Accessible**
- [ ] Retrievable via standard open protocols (HTTPS, REST API)
- [ ] Metadata accessible even if data is restricted
- [ ] No proprietary software required for access

**Interoperable**
- [ ] Standard vocabularies/ontologies (GO, HPO, SNOMED CT, LOINC)
- [ ] Open file formats (Parquet, HDF5, AnnData, ONNX)
- [ ] Community API standards (GA4GH, FHIR) where applicable

**Reusable**
- [ ] Clear, machine-readable license attached
- [ ] Detailed provenance documentation
- [ ] Domain-relevant community standards met (MIAME, MINSEQE, etc.)

### FAIR in Grant Language

When writing grants, reference FAIR as follows:
- Cite: Wilkinson, M.D. et al. (2016). *Scientific Data* 3, 160018.
- State: "All outputs will adhere to the FAIR Guiding Principles..."
- Be specific: name the repositories, identifier systems, and metadata schemas you will use.
- Do NOT just say "we follow FAIR principles" without implementation details. Reviewers flag this.
- For NIH: align with NIH Data Management and Sharing Policy (2023).
- For EU/Horizon: align with EOSC (European Open Science Cloud) requirements.

---

## 3. Open Science Practices

| Practice | Implementation |
|---|---|
| Open access publishing | All papers in OA venues or preprinted (bioRxiv, medRxiv, arXiv) |
| Preregistration | Hypothesis-driven studies registered on OSF or ClinicalTrials.gov |
| Open protocols | Shared via protocols.io |
| Open peer review | Opt in where available |
| Reproducibility | Code + environment + data access for every computational result |
| Open notebooks | Jupyter notebooks in public repos for exploratory analyses |

---

## 4. Open Models Practices

Every AI/ML model release includes:

1. **Model weights** on Hugging Face and/or Zenodo
2. **Training data** (or synthetic equivalent + data card if privacy-restricted)
3. **Training code** + hyperparameters + config files + training logs
4. **Evaluation code** + benchmark results + failure mode analysis
5. **Model card** (intended use, limitations, biases, provenance, ethics)

We follow Ai2's "truly open" standard: not just open-weights, but full transparency into the
entire training pipeline (data → code → weights → eval).

---

## 5. Nonprofit-to-Commercial Pathway

### The Rule: Open Core Stays Open. Forever.

```
┌─────────────────────────────────────────────────┐
│  CYTOGNOSIS FOUNDATION (501(c)(3))              │
│  All outputs: Apache 2.0 / CC BY 4.0           │
│  Irrevocable. Permanent. Public.                │
│                                                  │
│  ┌──────────────────────────────┐               │
│  │  Anyone can use, including:  │               │
│  │  • Researchers               │               │
│  │  • Governments               │               │
│  │  • Companies                 │               │
│  │  • Cytognosis PBC subsidiary │               │
│  └──────────────────────────────┘               │
└─────────────────────────────────────────────────┘
         │ same license as everyone else
         ▼
┌─────────────────────────────────────────────────┐
│  CYTOGNOSIS PBC (future for-profit subsidiary)  │
│  Proprietary value from:                         │
│  • Hosted services (SaaS) with SLAs             │
│  • Regulatory-grade validation / FDA pathway    │
│  • Hardware integration (Cytoscope devices)     │
│  • Enterprise support + professional services    │
│  • Clinical decision support certification       │
│                                                  │
│  NOT from: restricting foundation outputs        │
│  Revenue → flows back to foundation mission      │
└─────────────────────────────────────────────────┘
```

### Key Principles

1. **Licensing flows one direction.** Foundation → world (including subsidiary). Subsidiary gets no exclusive rights.
2. **Irrevocable.** Once released under Apache 2.0 / CC BY 4.0, outputs cannot be relicensed or restricted.
3. **Commercial value = services, not restrictions.** SaaS, validation, hardware, support, certification.
4. **Board safeguard.** Openness mandate requires supermajority + public notice to change.
5. **Revenue recycles.** Subsidiary profits fund more open research.

---

## 6. Repository Setup Checklist

When creating any new Cytognosis repository:

- [ ] `LICENSE` file (Apache 2.0 or MIT)
- [ ] SPDX license headers in every source file
- [ ] `README.md` with Cytognosis attribution, license badge, and citation info
- [ ] `CONTRIBUTING.md` with contribution guidelines
- [ ] `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1)
- [ ] `.reuse/dep5` or equivalent REUSE compliance
- [ ] `CITATION.cff` for academic citation
- [ ] `CHANGELOG.md` (keep-a-changelog format)
- [ ] CI check for license compliance (e.g., `reuse lint`)

→ For full project structure and tooling, see `cytognosis-python-standards`

---

## 7. Open vs. Free: Terminology Guide

| Term | Meaning | Our Position |
|---|---|---|
| **Open source** (OSI) | Source available, modifiable, redistributable under OSI-approved license | Our primary framework |
| **Free software** (FSF) | Upholds four essential freedoms (run, study, modify, redistribute) | Respected; our licenses satisfy these freedoms |
| **FOSS / FLOSS** | Umbrella term for both movements | Acceptable in technical contexts |
| **Source-available** | Code visible but not freely usable/modifiable | We never do this |
| **Open-weights** (AI) | Model weights released but not training data/code | We go beyond this |
| **Truly open** (Ai2) | Weights + data + code + logs + eval | Our standard for models |
| **FAIR** | Findable, Accessible, Interoperable, Reusable | Our data stewardship framework |
| **Open access** (publishing) | Free to read, often CC BY | Our publishing standard |

---

## References

| Resource | URL |
|---|---|
| FAIR Principles (GO FAIR) | https://www.go-fair.org/fair-principles/ |
| Wilkinson et al. 2016 | https://doi.org/10.1038/sdata.2016.18 |
| Apache License 2.0 | https://opensource.org/licenses/Apache-2.0 |
| MIT License | https://opensource.org/licenses/MIT |
| CC BY 4.0 | https://creativecommons.org/licenses/by/4.0/ |
| REUSE Specification | https://reuse.software/ |
| SPDX License List | https://spdx.org/licenses/ |
| Ai2 Research Principles | https://allenai.org/research-principles |
| COS / OSF | https://osf.io |
| NIH DMS Policy | https://sharing.nih.gov/data-management-and-sharing-policy |
| Contributor Covenant | https://www.contributor-covenant.org/ |

→ Full commitment statement: `references/commitment-statement.md`
