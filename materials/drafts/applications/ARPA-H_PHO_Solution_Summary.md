# ARPA-H Proactive Health Office (PHO) - Solution Summary

**Solicitation:** ARPA-H-SOL-24-106 (Amendment 03)
**Performer:** Cytognosis Foundation (501c3)
**Project Title:** The Cytognosis Platform: A Universal Cellular Intelligence Coordinate System for Pre-Disease Sensing
**Principal Investigator:** Shahin Mohammadi, PhD

---

## 1. Overall Scientific and Technical Merit

**The Problem: The Mechanistic, Temporal, and Complexity Blindspots**
Healthcare operates with three structural blindspots. The *mechanistic blindspot*: current diagnostics measure symptoms, not causes, creating artificial disease silos that blind researchers to shared biological mechanisms. The *temporal blindspot*: by the time clinical symptoms trigger diagnosis, significant organ damage is irreversible, yet no continuous monitoring platform tracks pre-symptomatic disease trajectories. The *complexity blindspot*: binary ICD codes collapse individual heterogeneity into population averages. Consequently, healthcare is reactive, waiting for disease onset rather than deploying continuous and widespread sensing of health-state.

**The Solution: Cytoverse, Cytoscope, and Cytonome**
Cytognosis introduces a radically new, disease-agnostic approach that transforms precision biomedicine into a continuous sensing paradigm. Our cellular intelligence platform ("GPS for Health") consists of three integrated components:

1. **Cytoverse (The Map):** A predictive surrogate model that constructs an AI health coordinate system. We map disease biology along continuous axes trained on single-cell multi-omic data across 50+ disease subtypes. Instead of binary "healthy/sick" classifications, Cytoverse learns continuous disease axes, modeling the variation between case-control pairs to reveal specific trajectory deviations years before clinical presentation.
2. **Cytoscope (The Sensor):** Programmable, continuous biosensing hardware for population-scale deployment. Cytoscope relies on low-cost sensing modalities (e.g., multiplexed aptamer panels, MEMS-based electrochemical sensors) to measure 10-100+ biomarkers simultaneously, tracking the molecular orchestra rather than a single molecule.
3. **Cytonome (The Navigator):** On-device causal AI (<5 mW) that computes personalized health trajectory predictions locally. By disentangling root drivers from symptoms using structural causal models without cloud dependency, Cytonome empowers individuals with actionable interceptive guidance.

**Feasibility and Risk Mitigation**
The Cytoverse coordinate system rests on peer-reviewed, single-cell analysis frameworks (ACTIONet) already adopted by major consortia (PsychENCODE, ROSMAP) and validated in our mapping of Alzheimer's and Schizophrenia *[Science 2024, Nature 2019]*.
*Risk 1: Biosensor Multiplexing Signal-to-Noise.* Mitigation: We utilize dynamic, active-reset sensing architectures (95 Hz oscillation) to track both biomarker increases and decreases with high fidelity.
*Risk 2: Edge Compute Limitations.* Mitigation: Our foundation models are aggressively quantized and distilled (3B parameters or smaller) and employ federated learning with differential privacy, ensuring clinical-grade accuracy on standard mobile devices without cloud dependency.

## 2. Potential Contribution and Relevance to ARPA-H Mission

**Population-Scale Health Span Extension**
The Cytognosis platform directly addresses the PHO mandate for "prophylactic approaches to prevention" and "early indicators of both disease- and pre-disease states." By establishing a baseline of continuous molecular tracking, we can detect the gradual drift from healthy coordinates toward disease attractors. This provides individuals and health systems with actionable, proactive health outcomes that are inexpensive, effective, and capable of increasing individual health spans even in the absence of clinical disease.

**Differentiation from Existing Portfolio**
While PROSPR scales therapeutic clinical trials for aging and EVIDENT validates endpoints for behavioral therapies, Cytognosis builds the upstream, *disease-agnostic diagnostic infrastructure layer*. We answer the question of *who* needs intervention and *when*, identifying pre-disease states that existing programs can then treat.

**Open-Source Standards and Interoperability**
Cytognosis aligns completely with ARPA-H’s interoperability and open-source mandates. All software (source code, federated learning pipelines, edge models) will be released under the **Apache 2.0 license**, and all data under **CC BY 4.0**. Our data models are designed for FHIR and TEFCA compliance, facilitating seamless integration with EHRs and establishing a general-purpose, open data API for the broader health ecosystem.

**Transition Strategy: The Helix Financial Architecture**
To ensure our 15-year innovation lifecycle doesn't die in the traditional "Valley of Death" that plagues 5-year grants, Cytognosis utilizes the **Helix Framework**. ARPA-H OT funding (Years 1-5) serves as non-dilutive R&D philanthropy to resolve the hardest technical bottlenecks. Because this risk is de-risked without VC dilution, the 60% equity "investor premium" typical of startups is permanently held by our 501(c)(3) parent as *The People's Equity*. When the platform transitions to commercial scale (Years 11-15) via Public Benefit Corporation (PBC) subsidiaries, this structural mission lock guarantees tiered global pricing and broad population accessibility for at least 75% of communities, while still providing competitive equity to attract top-tier engineering talent.

## 3. Proposer's Capabilities and/or Related Experience

**Shahin Mohammadi, PhD (PI & CEO)**
Dr. Mohammadi brings 20 years of computational biology expertise from MIT, the Broad Institute, insitro, and GenBio AI. He co-led the first single-cell multi-cohort atlas of schizophrenia (*Science* 2024) and the first single-cell atlas of Alzheimer's disease (*Nature* 2019), demonstrating a track record of discovering pre-symptomatic cell-type vulnerabilities. Beyond academic rigor, his 37-year diagnostic odyssey—resolved by his own self-directed genomic analysis identifying an ultra-rare TBX1 mutation—provides unmatched founder conviction to dismantle the mechanistic and temporal blindspots of modern healthcare.

The Cytognosis team merges deep biological exploration with high-throughput engineering under one roof, functioning as a Focused Research Organization (FRO) uniquely positioned to execute milestone-driven ARPA-H projects.

## 4. Cost/Price/Budget Assessment

We seek an Other Transaction (OT) agreement valued at **$15.0M over 24 months** for Phase 1 (Foundation).

- **$8.5M (AI & Compute):** Training of the disease-agnostic Cytoverse foundation model on >50 subtypes, including federated learning infrastructure and edge-distillation for Cytonome.
- **$4.5M (Hardware engineering):** Prototype development and validation of Cytoscope programmable active-reset sensors for a core 25-plex biomarker panel.
- **$2.0M (Regulatory/Admin):** IRB-approved phase 0 testing, open-source software release, and GA4GH/FHIR standards compliance.
This effort reflects the aggressive risk profile expected by ARPA-H, explicitly rejecting incremental advances to prototype a universal biological coordinate system.
