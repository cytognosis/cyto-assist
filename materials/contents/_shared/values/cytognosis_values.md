# Cytognosis Values: Grant & Application Positioning Guide

How Cytognosis Foundation's core values map to what funders evaluate. Use this document when writing any grant, application, or pitch to identify which values to emphasize and how to frame them.

---

## 1. Open Science, Open Source, Open Models

**Core position**: Everything Cytognosis produces is as open as possible, as restricted as necessary, and always FAIR. Openness is the mission expressed as practice, not an add-on.

**Key evidence**:

- Apache 2.0 for code, CC BY 4.0 for data/publications
- Truly open AI models (weights + data + code + logs + eval, following Ai2 standard)
- FAIR principles: persistent identifiers, machine-readable metadata, open protocols, standard ontologies
- Irrevocable licensing: once open, always open
- Nonprofit-to-PBC pathway preserves openness (commercial value from services, not restrictions)

**Funder-specific framing**:

| Funder | Emphasis | Key Language |
|--------|----------|-------------|
| NSF Tech Labs | Open science as platform infrastructure; FAIR compliance; public good output | "All platform outputs released under Apache 2.0/CC BY 4.0, creating open infrastructure for the biotechnology sector" |
| ARPA-H | Data sharing plan compliance; DMSP alignment; commercialization path | "Open platform enables broad health system adoption while PBC subsidiary manages regulatory pathways" |
| Convergent Research | Open-source as FRO requirement; public goods creation | "Irrevocable open licensing ensures FRO outputs persist as public infrastructure beyond funding period" |
| Astera | Open science track fit; why not industry | "Development happens in public from first commit; not source-available-later" |
| Foresight | Private AI, decentralized approaches | "On-device inference (<5mW) keeps health data local while models remain open" |
| EA LTFF | Open science as longtermist impact multiplier | "Open infrastructure compounds: every researcher who builds on Cytoverse multiplies our impact" |

→ Full commitment statement: `_shared/openness/commitment_to_openness.md`
→ Openness skill: `skills/cytognosis/openness/SKILL.md`

---

## 2. FRO Justification: Why This Work Needs a New Kind of Organization

**Core position**: Cytognosis fills a structural gap between academia (which rewards novelty over infrastructure) and industry (which requires patentable assets and short ROI timelines). It is the "necessary third pillar" for disease biology.

**Key evidence (from Why FRO doc)**:

- **32-year bottleneck**: NIH funded 99.4% of approved drugs, but average discovery-to-approval takes 32 years
- **Sevabertinib case study**: Broad Institute discovered EGFR exon 20 insertions in 2005; drug approved 2025. 8 years dormant because no entity was incentivized to validate the target
- **Commons problem**: US patents protect compounds, not biological mechanisms. Target identification (3-7% of R&D cost) governs >90% of downstream attrition
- **Prevention paradox**: Proving prevention requires larger populations and longer trials than treatment. ICD codes create artificial disease silos

**Coordinated Research Programs (from spec.tech Playbook)**:

- "Coordinated Research Program" (CRP) = umbrella term covering FROs, ARPA programs, NSF Tech Labs
- CRPs do work that doesn't make sense for a single lab or startup for systemic, institutional reasons
- CRPs very often create public goods (key reason they can't be startups)
- FROs are fully internalized CRPs; ARPA programs are fully externalized
- Good FROs: clear day-one goal, ~$50M deployment plan, single tightly-coupled project, full-time core team

**Funder-specific framing**:

| Funder | Frame As | Key Argument |
|--------|----------|-------------|
| Convergent Research | Textbook FRO | "Clear goal (cellular intelligence platform), $50M deployment plan, single coupled project, full-time team" |
| NSF Tech Labs | Tech Lab team | "Full-time RDI team filling the gap between foundational research and health system adoption" |
| ARPA-H | Program performer | "Institutionalizes the Sevabertinib model: biology exploration + industrial screening under one roof" |
| Astera | Residency project | "Work that doesn't fit in a lab (too much engineering) or a startup (public good, can't capture value)" |
| YC | Nonprofit with edge | "501(c)(3) building health infrastructure that VCs can't fund because value accrues to the public" |

→ Full FRO argument: `_shared/fro-argument/why_fro.md`

---

## 3. Health Equity & Accessibility

**Core position**: Precision health should be a human right, not a privilege. Cytognosis designs for accessibility from day one, targeting the 75% threshold that ARPA-H requires.

**Key evidence**:

- Mission statement: "Make precision health a human right, not a privilege"
- On-device AI (<5mW Cytonome) eliminates cloud dependency for underserved areas
- Open-source removes vendor lock-in for health systems in LMICs
- ARPA-H PROSPR requires accessibility planning for ≥75% of US communities
- Platform design: continuous monitoring replaces expensive episodic testing

**Funder-specific framing**:

| Funder | Emphasis |
|--------|----------|
| ARPA-H | Accessibility plan for ≥75% US communities; cost target <$100/assessment |
| NSF Tech Labs | Broader impacts: reducing health disparities through platform technology |
| Wellcome Leap | Global health equity; LMIC deployment; no cloud dependency |
| EA LTFF | QALYs gained per dollar across populations |
| DRK | Underserved population benefit; measurable outcomes |

---

## 4. Pasteur's Quadrant: Use-Inspired Basic Research

**Core position**: Cytognosis operates in Pasteur's Quadrant, where fundamental biological understanding directly drives practical health applications. We reject the false dichotomy between basic and applied research.

**Key evidence**:

- Cytoverse (The Map): fundamental cell biology mapped as navigable health coordinate system → directly used for individual health monitoring
- Continuous spectrum approach: replaces binary ICD codes with continuous biological trajectories → enables interception years before symptoms
- Platform technology model: like PCR or LEDs, the fundamental advance enables an entire ecosystem of applications

**Where this matters**:

- **NSF Tech Labs**: Explicitly seeks "use-inspired and translational RDI" and "platform technologies that can serve as the foundation for future innovation"
- **ARPA-H**: "Revolutionary solutions" to health challenges, not incremental improvements
- **Convergent Research**: FROs solve problems at the intersection of basic understanding and practical infrastructure
- **Foresight**: "AI for Science" track seeks projects that deepen understanding while enabling practical breakthroughs

---

## 5. Founder Narrative: The Diagnostic Odyssey

**Core position**: Shahin Mohammadi's 37-year diagnostic odyssey, resolved through self-directed genomic analysis identifying an ultra-rare TBX1 mutation, is the single most powerful narrative asset. The founder embodies the dual identity of scientist and patient.

**When to use**:

- **Always lead with it** in personal narrative sections (Emergent Ventures, YC, Astera)
- **Reference for mission credibility** in all proposals: "Cytognosis exists so no one else waits decades for answers"
- **Frame the problem** in technical proposals: real-world proof that siloed specialties, proprietary databases, and closed diagnostic frameworks keep answers hidden in plain sight

**Revelation Arc** (mandatory narrative structure):

1. **The Mystery**: 37 years of misdiagnosis across specialties
2. **The Insight**: Self-directed genomic analysis reveals ultra-rare TBX1 mutation
3. **The Resolution**: Building the infrastructure so this never happens to anyone else

---

## 6. Impact-First Orientation

**Core position**: If it doesn't 10x, it's not worth it. Cytognosis measures success by health outcomes changed, not papers published or patents filed.

**Key metrics**:

- Diseases intercepted years before symptoms (not "early detected")
- Individuals empowered with health autonomy (not "patients treated")
- Open tools adopted by research community (compound impact)
- Cost per QALY gained vs. current standard of care

---

## Funder-Value Mapping Matrix

Quick reference for which values to emphasize in each application:

| Value | ARPA-H | NSF Tech Labs | Convergent | Astera | Foresight | YC | EA LTFF | Emergent V | DRK | Wellcome |
|-------|:------:|:-----:|:-----:|:------:|:-----:|:--:|:------:|:-----:|:---:|:--------:|
| Open science/source | ◐ | ● | ● | ● | ◐ | ○ | ◐ | ○ | ○ | ● |
| FRO/CRP model | ◐ | ● | ● | ● | ◐ | ○ | ◐ | ○ | ○ | ● |
| Health equity | ● | ● | ◐ | ◐ | ○ | ○ | ● | ○ | ● | ● |
| Pasteur's Quadrant | ● | ● | ● | ● | ● | ○ | ◐ | ○ | ○ | ● |
| Founder narrative | ○ | ○ | ◐ | ● | ● | ● | ◐ | ● | ● | ◐ |
| Moonshot ambition | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● |
| Commercialization | ● | ● | ◐ | ◐ | ○ | ● | ○ | ○ | ● | ◐ |
| Impact metrics | ● | ● | ● | ◐ | ◐ | ● | ● | ○ | ● | ● |

`●` = primary criterion, `◐` = evaluated, `○` = not relevant

---

## 7. The Helix Financial Architecture (Purpose + Profit)

**Core position**: Cytognosis resolves the "Dilution vs. Mission Dilemma" by utilizing the Helix Framework. We fund high-risk R&D non-dilutively for 5 years. When scaling via commercial subsidiaries, the operational team receives competitive market-rate equity (~40%), but the 60% "investor premium" stays with the nonprofit parent as **The People's Equity**—used strictly for enforcing global access and funding future research.

**Key evidence**:

- **15-Year, 3-Stage Lifecycle**: Y1-5 (R&D Philanthropy), Y6-10 (Catalytic Capital), Y11-15 (Commercial Scale).
- **The Phase Transition Problem**: Standard 5-year grants abandon technology before clinical utility; Helix provides a 15-year bridge.
- **Structural Mission Lock**: Using Public Benefit Corporation subsidiaries and Future Interest Participation Agreements to bind commercial spinouts to the parent foundation's mission.

**Funder-specific framing**:

| Funder | Emphasis |
|--------|----------|
| ARPA-H | 15-year lifecycle ensures your R&D investment doesn't die in the valley of death |
| Convergent / FRO | The People's Equity resolves the commercialization challenge for FROs without mission drift |
| EA LTFF / DRK | Regenerative financial architecture means initial philanthropy is leveraged indefinitely |
| YC / Astera | Competitive founder/talent equity ensures we can recruit top AI talent despite being a 501(c)(3) |
