# Cytognosis Foundation: Commitment to Openness

**Open Science. Open Source. Open Models. Open Future.**

---

## Why Openness Is Foundational to Our Mission

Cytognosis Foundation exists because the systems meant to protect health failed one person for 37 years. Siloed specialties, proprietary databases, and closed diagnostic frameworks kept answers hidden in plain sight. The same structural closure that delays diagnosis also delays discovery.

We build in the open because we believe the tools to intercept disease years before symptoms should belong to humanity, not to shareholders. As a 501(c)(3) nonprofit Focused Research Organization, openness is not an add-on to our mission. It is our mission expressed as practice.

Our commitment to openness draws inspiration from organizations that have demonstrated its transformative power. The Allen Institute for AI (Ai2) proves that a nonprofit can produce state-of-the-art AI while releasing everything (data, code, weights, training logs, and evaluation frameworks) under permissive licenses. The Center for Open Science (COS) has built infrastructure that makes transparent, reproducible research the default rather than the exception. The Astera Institute funds neglected scientific ideas that fall between existing institutions. The Apache Software Foundation, Open Source Initiative, and Free Software Foundation have spent decades establishing the legal and philosophical frameworks that make collaborative development possible at global scale. We stand on their shoulders.

---

## Our Three Pillars of Openness

### 1. Open Science

All research produced by Cytognosis Foundation adheres to the principles of open science as articulated by the Budapest Open Access Initiative (2002), the Berlin Declaration on Open Access (2003), and the UNESCO Recommendation on Open Science (2021).

**What this means in practice:**

- **Open access publications.** All Cytognosis-authored research is published in open access venues or deposited as preprints (bioRxiv, medRxiv, arXiv) prior to or simultaneous with journal submission. We do not publish behind paywalls.
- **Preregistration.** Hypothesis-driven studies are preregistered on OSF (Open Science Framework) or ClinicalTrials.gov before data collection begins, reducing publication bias and promoting transparency in our research design.
- **Open protocols.** Laboratory protocols, computational pipelines, and experimental methods are shared via protocols.io or equivalent platforms with sufficient detail for independent replication.
- **Open peer review.** Where available, we opt for open peer review and publish reviewer comments alongside accepted manuscripts.
- **Reproducibility as standard.** Every computational result is accompanied by the code, environment specification (containerized where possible), and data access instructions necessary to reproduce it.

### 2. Open Source

All software tools, libraries, and infrastructure developed by Cytognosis Foundation are released as open source under OSI-approved licenses.

**What this means in practice:**

- **Default license: Apache 2.0.** We select Apache 2.0 as our default license for software because it provides broad permissions for use, modification, and distribution; includes an explicit patent grant that protects both contributors and users; requires clear attribution and documentation of changes; and is compatible with most other open source licenses including GPL v3.
- **Alternative: MIT License.** For lightweight utilities, scripts, and educational materials where simplicity is valued and patent considerations are minimal, we use the MIT License.
- **Full source availability.** Source code is hosted on public GitHub repositories under the Cytognosis organization from the first commit. We do not develop behind closed doors and open-source later. Development happens in public.
- **Community contribution.** All repositories include CONTRIBUTING.md guidelines, a Code of Conduct (Contributor Covenant), and issue templates to lower the barrier for external contributors.
- **Dependency transparency.** We document all dependencies, their licenses, and any compatibility considerations. We avoid incorporating dependencies with licenses that would restrict downstream use.

### 3. Open Models

All AI/ML models, foundation models, and trained weights produced by Cytognosis Foundation are released openly with full transparency into the training process.

**What this means in practice:**

- **Open weights.** Trained model weights are published on Hugging Face and/or Zenodo with persistent identifiers.
- **Open training data.** Training datasets are released under appropriate open data licenses (CC BY 4.0 for non-personal data, or CC BY-NC 4.0 where ethical considerations around health data require it). Where data cannot be shared directly due to privacy regulations (HIPAA, GDPR), we provide synthetic equivalents, detailed data cards, and access instructions for qualified researchers through controlled-access repositories.
- **Open training code.** Training scripts, hyperparameters, configuration files, and training logs are released alongside model weights so that results can be reproduced and methodology can be scrutinized.
- **Open evaluation.** Benchmark results, evaluation scripts, and failure mode analyses are published. We do not report only favorable metrics.
- **Model cards.** Every released model includes a standardized model card documenting intended use, limitations, known biases, training data provenance, and ethical considerations.

---

## The FAIR Principles: Our Data Stewardship Framework

We commit to the FAIR Guiding Principles for scientific data management and stewardship (Wilkinson et al., *Scientific Data*, 2016). FAIR is not a synonym for "open." It is a complementary framework that ensures our digital research outputs are useful, not merely available.

### How We Implement FAIR

**Findable**
- All datasets, models, and code artifacts receive globally unique, persistent identifiers (DOIs via Zenodo, Hugging Face model IDs, or equivalent).
- Rich, machine-readable metadata (using domain-appropriate schemas such as schema.org, Dublin Core, and biomedical ontologies) accompanies every digital asset.
- Assets are registered in searchable community repositories (e.g., Zenodo, Hugging Face, GEO for genomics data, CellxGene for single-cell data).

**Accessible**
- Metadata and data are retrievable via standardized, open protocols (HTTPS, REST APIs).
- Metadata remains accessible even if underlying data is restricted (e.g., for privacy-protected health data, metadata describes the dataset fully while data access requires IRB-approved application).
- We never require proprietary software to access our outputs.

**Interoperable**
- Data uses formal, widely adopted vocabularies and ontologies (Gene Ontology, Human Phenotype Ontology, SNOMED CT, LOINC) for knowledge representation.
- File formats are open and non-proprietary (Parquet, HDF5, AnnData for single-cell, ONNX for models) rather than locked to specific tools.
- APIs follow community standards (GA4GH for genomic data, FHIR for clinical data) to enable integration with other systems.

**Reusable**
- Every dataset and model is released with a clear, machine-readable license.
- Detailed provenance information documents how data was collected, processed, and quality-controlled.
- Data meets domain-relevant community standards (MIAME for microarray, MINSEQE for sequencing, minimum information standards for single-cell).

### FAIR ≠ Open: An Important Distinction

We embrace the nuance that FAIR and open are related but distinct concepts. Data can be FAIR without being fully open (e.g., controlled-access health data with rich metadata, clear access procedures, and standardized formats). Data can be open without being FAIR (e.g., a CSV dump on a website with no metadata, no persistent identifier, and no documentation).

Our commitment is to make everything as open as possible and as restricted as necessary, while always being FAIR. For health-related data involving human subjects, ethical, legal, and privacy constraints take precedence. In these cases, we maximize openness through synthetic data generation, differential privacy, federated access, and detailed metadata that enables discovery even when raw data access requires authorization.

---

## Understanding Open vs. Free: Our Philosophical Position

The open source and free software movements share common ground but differ in emphasis. The Free Software Foundation (FSF) frames software freedom as a moral imperative rooted in four essential freedoms: to run, study, modify, and redistribute software. The Open Source Initiative (OSI) emphasizes the practical benefits of collaborative, transparent development. Both perspectives have merit.

Cytognosis Foundation takes a pragmatic, mission-aligned position:

- We use **OSI-approved licenses** (Apache 2.0, MIT) as our defaults because they are well-understood, widely adopted, legally tested, and compatible with both nonprofit and commercial use cases.
- We respect the **philosophical commitments of the free software movement** and ensure our license choices uphold the four freedoms in practice, even though we do not mandate copyleft.
- We choose **permissive over copyleft licenses** deliberately. Our mission is to maximize the adoption and impact of tools that intercept disease. Copyleft licenses (GPL) can create friction for downstream adoption in healthcare systems, regulatory environments, and commercial partners whose participation is essential for bringing our tools to the people who need them.
- We use the term **"open source"** (consistent with OSI usage) rather than "free software" in our communications, while acknowledging the broader FLOSS tradition. When we say "open," we mean it in the fullest sense: not just source-available, but truly open for use, modification, and redistribution.

---

## License Selection Guide

Different artifact types call for different license considerations:

| Artifact Type | Default License | Rationale |
|---|---|---|
| **Software / Libraries** | Apache 2.0 | Patent grant, attribution, broad compatibility |
| **Lightweight scripts / utilities** | MIT | Simplicity, maximum adoption |
| **Documentation / Educational content** | CC BY 4.0 | Allows any reuse with attribution |
| **Research data (non-personal)** | CC BY 4.0 | Standard for open scientific data |
| **Research data (health/personal)** | Controlled access + CC BY-NC 4.0 metadata | Ethical constraints, DUA required |
| **AI/ML model weights** | Apache 2.0 | Consistent with code, patent protections |
| **Training datasets** | CC BY 4.0 or CC BY-SA 4.0 | Community reciprocity for data |
| **Preprints / Publications** | CC BY 4.0 | Gold open access standard |
| **Brand assets / Logos** | All rights reserved | Trademark protection is distinct from open source |

### On Custom and Restrictive Licenses

We have studied licenses like Liquid AI's LFM Open License, which modifies Apache 2.0 to add revenue-based commercial restrictions. While we appreciate the intent of protecting small-scale and nonprofit use, we do not adopt this approach for our foundation outputs. Custom licenses create legal uncertainty, fragment the ecosystem, and are not OSI-approved. Our commitment is to standard, well-understood licenses that the community already trusts.

If future Cytognosis for-profit subsidiaries (PBCs) develop proprietary products or services on top of the foundation's open outputs, they do so as downstream users of permissively licensed code, not by restricting the open outputs themselves. The open foundation remains open.

---

## Nonprofit-to-Commercial Pathway: Protecting Openness While Enabling Impact

Cytognosis Foundation is structured as a 501(c)(3) nonprofit. We also anticipate that bringing our tools to scale may eventually involve for-profit subsidiaries operating as Public Benefit Corporations (PBCs). This dual structure must protect openness while enabling the commercial partnerships, regulatory pathways, and sustained investment that healthcare delivery requires.

**Our principles for this pathway:**

1. **The open core stays open.** All research, foundation models, training data, evaluation frameworks, and core software libraries developed by Cytognosis Foundation are released under permissive open licenses (Apache 2.0 / CC BY 4.0) and remain permanently open. These licenses are irrevocable. Once released, they cannot be retracted.

2. **Commercial value comes from services, not restrictions.** For-profit subsidiaries may build proprietary value through hosted services (SaaS), regulatory-grade validation and certification, hardware integration, clinical decision support systems with guaranteed uptime/SLAs, and professional support and enterprise features. They do not build proprietary value by closing previously open outputs.

3. **Licensing flows one direction.** The nonprofit licenses openly to the world (including any subsidiary). The subsidiary does not gain exclusive rights to foundation outputs. Any researcher, company, or government has the same access as a Cytognosis subsidiary.

4. **Revenue supports the mission.** Revenue generated by for-profit subsidiaries flows back to the foundation through licensing fees, revenue sharing, or charitable contributions, funding further open research.

5. **Governance safeguards.** The foundation's board maintains an openness mandate that cannot be overridden by commercial interests. Any changes to licensing policy require board approval with a supermajority and a public notice period.

---

## Accountability and Transparency

Commitments without accountability are marketing. We hold ourselves to measurable standards:

- **Annual openness audit.** We publish an annual report documenting what percentage of our outputs (code, data, models, publications) were released openly, any exceptions and their justifications, and FAIR compliance metrics.
- **Public roadmap.** Our research roadmap, including planned data releases and model publications, is maintained publicly on GitHub.
- **License compliance monitoring.** We use automated tools (e.g., REUSE, SPDX) to ensure every file in every repository has a clear, machine-readable license identifier.
- **Community feedback.** We maintain open channels (GitHub Discussions, community calls) for external stakeholders to raise concerns about our openness practices.

---

## Signatories and Adoption

This commitment is adopted by the Cytognosis Foundation Board of Directors and applies to all Foundation activities, employees, contractors, and funded projects.

**Adopted:** [Date]
**Review cycle:** Annual, with public comment period

*Cytognosis Foundation, Inc. | 501(c)(3) | EIN 39-4383634*

---

## References and Inspirations

- Wilkinson, M.D. et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data* 3, 160018.
- Budapest Open Access Initiative (2002). https://www.budapestopenaccessinitiative.org/
- Berlin Declaration on Open Access to Knowledge in the Sciences and Humanities (2003).
- UNESCO Recommendation on Open Science (2021).
- Allen Institute for AI — Research Principles. https://allenai.org/research-principles
- Center for Open Science — OSF. https://osf.io
- Astera Institute. https://astera.org
- Open Source Initiative — Open Source Definition. https://opensource.org/osd
- Free Software Foundation — Four Essential Freedoms. https://www.gnu.org/philosophy/free-sw.html
- Apache Software Foundation. https://www.apache.org
- PLOS — Commitment to Open Science. https://plos.org/commit-to-openness/
- GO FAIR Foundation — FAIR Principles. https://www.go-fair.org/fair-principles/
- NIH Data Management and Sharing Policy (2023).
- CARE Principles for Indigenous Data Governance (2019).
