# **Y Combinator Application: Cytognosis**

---

## FOUNDERS

**Founder:** Shahin Mohammadi

---

## FOUNDER QUESTIONS

### Who writes code, or does other technical work on your product? Was any of it done by a non-founder? Please explain.

All technical work to date has been done by me. Core platform architecture, AI model development, and data pipeline design are built on 20 years of computational biology expertise across MIT, Broad Institute, insitro, and GenBio AI. Collaborating scientists (José Davila-Velderrain at Human Technopole, Madhvi Menon at University of Manchester) contribute domain expertise, not code.

### Are you looking for a cofounder?

Yes. Actively seeking:

1. **Erin Rist** (preferred): Co-developed this vision through NUCLEATE in 2019\. She now brings operational excellence from early-stage biotech; I've deepened the technical foundation. We've maintained alignment and are in discussions to reunite.

2. **Technical cofounder**: Someone with biosensor/hardware experience (ideally from Dexcom, Abbott, or 10x Genomics background) who shares our commitment to democratizing precision health.

---

## COMPANY

### Company name

Cytognosis

### Describe what your company does in 50 characters or less.

AI-powered continuous health monitoring for everyone

*(49 characters)*

### Company URL

[https://www.cytognosis.org/](https://www.cytognosis.org/)

### What is your company going to make? Please describe your product and what it does or will do.

**The Problem: Healthcare's $850B Blindspot**

Modern medicine suffers from three fundamental blindspots that cost $850B annually in non-optimized therapy alone:

- **Mechanistic Blindness**: We treat symptoms, not causes. Depression has 4+ biological subtypes, yet we cycle through the same medications hoping something works. Autoimmune patients typically take 4.5-7 years to be diagnosed by 4+ physicians.

- **Complexity Blindness**: We measure single markers when a disease involves networked systems. GWAS accounts for only 5-20% of the heritability of complex diseases. Blood panels miss which specific immune cells are driving dysfunction.

- **Temporal Blindness**: We take quarterly snapshots of systems that change on timescales of minutes. Alzheimer's signatures appear 15-30 years before symptoms. Cancer DNA circulates 3+ years before diagnosis. By the time we detect disease, the intervention window has closed.

**Our Solution: The Cytognosis Platform**

We're building a "GPS for Health" with three integrated technologies:

1. **Cytoverse (The Map)**: AI that maps all human cellular states into continuous health coordinates. Instead of binary disease labels, you get a position on quantitative biological axes. Built on single-cell atlases we created (Nature 2019, Science 2024\) covering 10M+ cells across 50+ conditions.

2. **Cytoscope (The Sensor)**: Programmable biosensors for continuous molecular monitoring. Like CGM, but for 50-100+ biomarkers optimized for YOUR genetics. Key innovation: active-reset architecture achieves sub-minute temporal resolution (vs. one-way kinetics of current sensors), tracking both increases AND decreases in real-time.

3. **Cytonome (The Navigator)**: On-device AI (\<5mW) that converts molecular coordinates into personalized interventions. Privacy-first architecture with federated learning. Your data never leaves your device.

**User Experience**: A wearable patch continuously tracks your molecular state, positioning you on personalized health axes. When your coordinates shift toward a disease trajectory, you get actionable recommendations: "Your inflammatory markers are trending up. Based on your genetics, try: adjust sleep timing, reduce alcohol this week." Catch the spark before it becomes a fire.

**Think**: Continuous glucose monitoring × Function Health's comprehensive panels × Zoe's personalized insights, but tracking the actual cellular conversations that drive disease, not just downstream markers.

### Where do you live now, and where would the company be based after YC?

Daly City, CA / South San Francisco, CA

### Explain your decision regarding location.

South San Francisco is the global epicenter of biotech for good reason:

- **Talent density**: 1,000+ biotech companies within 20 miles; deep bench of biosensor, AI, and clinical talent  
- **Lab access**: JLABS offers immediate, no-equity wet lab space; 25% vacancy rates mean once-in-a-decade deals on dedicated facilities  
- **Clinical partnerships**: Stanford, UCSF, and Kaiser within 30 minutes for validation studies  
- **Hardware ecosystem**: Proximity to biosensor supply chain (Dexcom, Abbott Diabetes nearby)

Geography matters when building hardware requiring wet labs, clinical collaborations, and biosensor manufacturing partnerships.

---

## PROGRESS

### How far along are you?

- **October 2024**: Left industry role to work full-time as CEO  
- **January 2025**: 501(c)(3) approved; nonprofit foundation established  
- **Current**:  
  - Curating PsychENCODE \+ NeuroBioBank datasets for the first Cytoverse models  
  - Evaluating biosensor architectures for Cytoscope v1  
  - Negotiating partnerships with the Gates Foundation and clinical sites  
- **Pipeline**: $52.5M ARPA-H proposal submitted; FRO application in progress

### How long have each of you been working on this? How much of that has been full-time?

- **Vision**: 6 years (NUCLEATE 2019 with Erin Rist)  
- **Technical foundation**: 20 years building the underlying AI/biology tools  
- **Full-time on Cytognosis**: Since October 2024 (4 months)

### What tech stack are you using, or planning to use?

**AI/ML Infrastructure:**

- PyTorch \+ PyTorch Geometric for heterogeneous graph neural networks  
- Custom sparse kernels for signed network processing (millions of cellular interactions)  
- BioCypher knowledge graphs grounding models in biological reality  
- BioChatter RAG framework bridging knowledge graphs to foundation models

**Data Harmonization:**

- Biomni agents for automated dataset curation  
- OLS4 standardized ontologies (Cell Ontology, UBERON, MONDO) for FAIR compliance

**Biosensor Development:**

- Evaluating CMOS-based FET arrays, aptamer-based electrochemical sensors, and nanopore platforms  
- Targeting integration with established CGM form factors

**Development Tools:**

- Cursor/Windsurf AI coding assistants  
- Rigorous CI/CD for medical-grade reliability

### Are people using your product?

No. Pre-product stage.

### When will you have a version people can use?

| Milestone | Timeline | Description |
| :---- | :---- | :---- |
| Cytoverse v0.5 | Month 6 | Research API for cellular disease axes (5 disorders) |
| Cytoverse v1.0 | Month 12 | Production cellular coordinate system |
| Cytoscope prototype | Month 18 | Benchtop multi-analyte sensor validation |
| Integrated platform beta | Month 36 | 1,000-person longitudinal study |
| Consumer device | Month 60 | Derisked for manufacturing |

### Do you have revenue?

No.

### If you are applying with the same idea as a previous batch, did anything change?

N/A (first application)

### If you have already participated in an incubator/accelerator?

**NUCLEATE (2019)**: Completed with Erin Rist. Developed initial Cytognosis concept. Poised to launch when COVID hit. Our "brief pause" stretched into years; we both took industry roles. Those early concepts became this platform.

---

## IDEA

### Why did you pick this idea to work on? Do you have domain expertise in this area? How do you know people need what you're making?

**Personal urgency meets technical capability.**

I spent 37 years with misdiagnoses across 10 medical specialties and experimental treatments that sometimes made things worse. Then I used the very AI tools I'd been building at MIT and the Broad Institute to analyze my own genome. The answer: an ultra-rare TBX1 mutation orchestrating all my "unrelated" conditions. One root cause. Ten specialists. None saw it.

This journey revealed medicine's fatal flaw: **we diagnose symptom clusters, not causes.** Like treating "fever" without knowing if it's flu, COVID, or strep. We label "depression" and cycle through medications, essentially reverse-engineering causes through human experimentation.

The tragedy deepens with timing:

- Alzheimer's signatures appear **15-30 years** before memory fails  
- Cancer DNA circulates **3+ years** before tumors form  
- Autoimmune dysfunction begins **years** before tissue damage

By the time symptoms emerge, the intervention window has often closed.

**Domain expertise:**

- 20 years computational biology (Purdue → MIT → Broad Institute → insitro → GenBio AI)  
- Led first single-cell brain atlases for Alzheimer's (Nature 2019\) and schizophrenia (Science 2024\)  
- 4,000+ citations across 40+ publications in Nature, Science, Cell  
- Built AIDO, the first multiscale foundation model in biology

**Market validation:**

- Function Health: 100K+ customers paying $500/year for quarterly blood panels  
- Zoe: 500K+ users for CGM-based dietary optimization  
- CGM market: $15B and growing 10%+ annually  
- 60% of US adults have chronic conditions; 90% of the $5.3T healthcare spending

People are desperate for health visibility. Current options give them either comprehensive-but-static (Function) or continuous-but-limited (Zoe/CGM). We give them comprehensive AND continuous.

### Who are your competitors? What do you understand about your business that they don't?

| Competitor | What They Do | Their Limitation | Our Advantage |
| :---- | :---- | :---- | :---- |
| Function Health | 100+ blood biomarkers quarterly | Static snapshots of dynamic systems; miss trajectories | Continuous monitoring catches changes as they emerge |
| Zoe | CGM \+ microbiome for diet | Only metabolic signals; can't see immune/neuro | Multi-system: metabolic \+ immune \+ neuro \+ more |
| Levels/Nutrisense | CGM interpretation | Single analyte (glucose) | 50-100+ programmable biomarkers |
| Grail/Exact Sciences | Cancer screening | Binary detection; limited to cancer | Continuous health coordinates across all conditions |
| 23andMe | Genetic risk scores | Static genetics; no dynamic monitoring | Genetics \+ real-time cellular state |

**What we understand that they don't:**

Disease isn't static; it's not a set of markers in the blood. It's **dynamic cellular conversations**.

Current approaches fail because:

1. **Wrong temporal resolution**: Immune responses and hormonal shifts happen in minutes/hours. Quarterly panels miss the entire trajectory.  
2. **Wrong measurement level**: Blood biomarkers are downstream effects. We monitor the upstream cellular states actually driving disease.  
3. **No personalization at the cellular level**: They compare you to population averages. We learn YOUR baseline and detect YOUR deviations.

The distinction: Monthly security photos vs. real-time monitoring. We detect the earliest cellular perturbations as they emerge, not after they've cascaded into systemic disease.

### How do or will you make money? How much could you make?

**Revenue Model (OpenBCI-style hardware \+ SaaS):**

| Stream | Price Point | Description |
| :---- | :---- | :---- |
| Cytoscope device | $299-499 | Programmable biosensor patch (replaceable monthly) |
| Cytognosis subscription | $29-49/month | AI insights, personalized recommendations, Cytoverse access |
| Sensor refills | $99/month | Replacement biosensor cartridges |
| Enterprise/Research | Custom | API access, cohort analytics, clinical trial tools |

**Unit Economics:**

- Device COGS: \~$100 at scale  
- Gross margin: 65-70% on hardware, 85%+ on subscription  
- LTV: $1,500+ (24-month average retention, based on CGM benchmarks)  
- Target CAC: \<$200 (health-conscious early adopters, word-of-mouth)

**Market Size:**

| Segment | Size | Our Target |
| :---- | :---- | :---- |
| Global chronic disease population | 500M people | 1% \= 5M users |
| US adults with chronic conditions | 133M (60%) | 2% \= 2.6M users |
| "Worried well" health optimizers | 50M globally | 5% \= 2.5M users |
| CGM market (analog) | $15B, 10%+ CAGR | Expand from glucose to full molecular |

**Revenue Projections:**

| Year | Users | Revenue | Notes |
| :---- | :---- | :---- | :---- |
| 3 | 10K | $6M | Early adopters, research partnerships |
| 5 | 100K | $60M | Consumer launch |
| 7 | 1M | $600M | Scale \+ enterprise |
| 10 | 5M | $3B | Global deployment |

**Path to $1B+:**

- 2M users in developed markets × $600/year \= $1.2B  
- Enterprise/research contracts: $200M  
- Simultaneously serve 10M+ in emerging markets through philanthropic subsidies (Gates Foundation partnership)

**Our Edge**: Hybrid nonprofit/PBC structure enables $100M+ in government/philanthropic R\&D funding while generating sustainable commercial revenue. Developed markets subsidize emerging markets, creating both impact and a defensible moat.

### Which category best applies to your company?

Biotech

### If you had any other ideas you considered applying with, please list them.

The core vision (Cytognosis platform) is constant. Strategic variations I'm evaluating:

1. **Neuro-first vs. Immune-first**: Start with neuropsychiatric conditions (schizophrenia, bipolar, Alzheimer's) where I have the deepest data, or autoimmune conditions (RA, lupus, MS) where continuous monitoring has more immediate clinical utility?

2. **Research tool vs. Consumer device**: Launch first as a research platform for pharma/academic customers (faster regulatory path, immediate revenue), then expand to consumers?

3. **Software-only MVP**: Release Cytoverse as a standalone AI platform first (no hardware dependency), then integrate Cytoscope once sensors are validated?

Currently leaning toward: **Neuro-first research tool → Consumer neuropsychiatric monitoring → Expand to autoimmune and metabolic.**

### Please describe the scientific basis for your product. How does it work?

**Scientific Foundation (two pillars):**

**Pillar 1: Cellular Disease Axes Exist and Are Measurable**

Our Science 2024 publication demonstrated continuous "disease axes" in schizophrenia affecting specific neuronal subtypes. One DSM diagnosis contains multiple distinct biological diseases. This confirms:

- Traditional diagnostic categories don't match biological reality  
- Molecular patterns can stratify patients better than symptoms  
- Cross-disorder shared genetics (Grotzinger et al., Nature Genetics 2022; Science 2025\) reflect shared cellular mechanisms

We've built the first single-cell atlases for psychiatric disorders (PsychENCODE, ROSMAP). We have the molecular maps to operationalize what others only theorize.

**Pillar 2: Continuous Molecular Monitoring Is Now Feasible**

Recent advances enable expanded continuous monitoring:

- **Cross-modal imputation**: Clinically relevant readouts (like tau-PET for Alzheimer's) can be predicted from simpler, non-invasive measurements when training data links both modalities (Nature Communications 2025\)

- **Programmable affinity sensors**: Active-reset aptamer-based biosensors achieve continuous monitoring across diverse analyte classes, not just enzymatic targets like glucose (Nature Communications 2024\)

- **CMOS integration**: Field-effect transistor arrays enable massively parallel sensing at consumer-grade costs

**How It Works:**

1. **Cytoverse** learns a continuous coordinate system from 10M+ single cells across 50+ conditions, creating "health latitude/longitude"

2. **Cytoscope** sensors sample interstitial fluid via reverse iontophoresis, measuring 50-100+ biomarkers and projecting you onto Cytoverse coordinates

3. **Cytonome** runs on-device causal models to identify which axes are shifting and recommends personalized interventions

**Key Innovation**: The "sparsity of shift" principle. Disease doesn't change everything; it perturbs specific cellular circuits. By mapping the full healthy state space, we detect the earliest deviations with high specificity.

### Describe the next few stages in developing your product. For each stage, how much time and money will it take?

**PHASE 1: FOUNDATION (Years 1-2) | $15M**

*Goal: Validate core AI and identify optimal biosensor architecture*

| Milestone | Timeline | Cost | Deliverable |
| :---- | :---- | :---- | :---- |
| Cytoverse v0.5 | Month 6 | $2M | Cellular disease axes across 5 disorders |
| Cytoverse v1.0 | Month 12 | $3M | Production API, 10+ disorders |
| Cytoverse v2.0 (WGS) | Month 18 | $3M | Genetic risk integration |
| Cytoscope architecture | Month 18 | $5M | Validated sensor modality selection |
| Cytonome prototype | Month 24 | $2M | On-device inference proof-of-concept |

**PHASE 2: INTEGRATION (Years 3-4) | $25M**

*Goal: Integrated platform validated in longitudinal human studies*

| Milestone | Timeline | Cost | Deliverable |
| :---- | :---- | :---- | :---- |
| Cytoscope benchtop | Month 30 | $8M | 50+ analyte parallel sensing |
| 1,000-person study | Month 36 | $7M | Longitudinal validation |
| Wearable prototype | Month 42 | $6M | Consumer form factor |
| FDA pathway | Month 48 | $4M | Regulatory strategy established |

**PHASE 3: COMMERCIALIZATION (Year 5\) | $35M**

*Goal: Consumer launch and scale*

| Milestone | Timeline | Cost | Deliverable |
| :---- | :---- | :---- | :---- |
| Manufacturing | Month 54 | $15M | Production-ready device |
| 5,000-person beta | Month 57 | $10M | Pre-launch validation |
| Consumer launch | Month 60 | $10M | Go-to-market |

**Total 5-Year Budget: $75M**

- Government/philanthropic (70%): $52.5M (ARPA-H, Gates, Wellcome)  
- Equity/revenue (30%): $22.5M

### If you were accepted into YC, what could you accomplish by Demo Day?

**Deliverables by Demo Day (3 months):**

1. **Cytoverse v0.3 (Alpha)**

   - Curated multimodal atlas: 500K+ cells across 5 neuropsychiatric disorders  
   - First trained pairwise embedding model  
   - Research API with basic axis projection  
2. **Cytoscope Architecture Decision**

   - Completed evaluation of 3 biosensor modalities  
   - Selected primary technology partner  
   - Defined Year 1 hardware development roadmap  
3. **Key Partnerships Secured**

   - Clinical site LOIs (targeting UCSF, Stanford)  
   - Biosensor technology partner signed  
   - Gates Foundation or Wellcome Trust discussion initiated  
4. **Team Expansion**

   - 1-2 key hires (ML engineer, biosensor engineer)  
   - Cofounder decision finalized (ideally Erin Rist)  
5. **Seed Round**

   - $3-5M seed round closed or committed  
   - 18-month runway secured

**Why This Is Achievable**: The data infrastructure exists (PsychENCODE, NeuroBioBank). The AI architecture is designed. I've been building toward this for 20 years. YC provides the forcing function, network, and capital to compress what would otherwise take 12 months into 3\.

### Does your product need regulatory approval (FDA)? If so, what is the approval process?

**Regulatory Strategy: Phased Approach**

**Phase 1 (Years 1-3): Research Use Only**

- No FDA approval required for research tools  
- Partner with academic institutions and pharma for validation studies  
- Generate clinical evidence base

**Phase 2 (Years 3-4): Wellness Device (510(k) Exempt)**

- Position initial consumer device as "general wellness" (like Fitbit, Oura)  
- Focus on lifestyle optimization, not disease diagnosis  
- Clear labeling: "Not intended to diagnose, treat, or cure any disease."

**Phase 3 (Years 4-5): Clinical Decision Support**

- 510(k) pathway for specific indications with established predicates  
- FDA Breakthrough Device Designation for novel capabilities  
- Target Class II device classification

**Key Regulatory Considerations:**

- De Novo pathway if no suitable predicate exists  
- Engage the FDA Biomarker Qualification Program early  
- Build clinical evidence through academic partnerships before regulatory submission

**Cost/Timeline for FDA Clearance:**

- Wellness device path: Minimal regulatory cost  
- 510(k) clinical device: $2-5M, 12-18 months  
- De Novo: $5-10M, 24-36 months

**Our Edge**: Consumer wellness positioning (Fitbit model) allows market entry while building clinical evidence. Philanthropic subsidies (Gates Foundation) reduce dependence on insurance reimbursement that typically requires FDA clearance.

### What experimental data (if any) do you have showing that this would work?

**Published Validation:**

1. **Science 2024**: Identified continuous disease axes in schizophrenia affecting specific neuronal subtypes. Proved that one DSM diagnosis is actually multiple biological diseases with distinct molecular signatures.

2. **Nature 2019**: First single-cell atlas of Alzheimer's disease brain, revealing cell-type-specific pathology invisible to bulk analysis.

3. **Cross-disorder genetics** (Grotzinger et al.): Confirmed shared genetic architecture across 14 psychiatric disorders, validating our approach of learning shared axes rather than studying diseases in silos.

**Field Consensus:**

- NIMH introduced RDoC a decade ago to replace symptom-based diagnosis  
- Former NIMH Director Steven Hyman (Precision Psychiatry 2025): "Time to Retire the DSM and Begin Again"  
- Everyone agrees we need data-driven disease axes; we have the actual molecular maps to build them

**Technology Validation:**

- Cross-modal imputation proven (Nature Communications 2025): Can predict tau-PET from simpler modalities  
- Continuous aptamer sensing demonstrated (Nature Communications 2024): Active-reset biosensors achieve real-time multi-analyte tracking

**Our Unique Position:**

- Led creation of first single-cell atlases across psychiatric disorders (PsychENCODE, ROSMAP)  
- Not proposing theoretical frameworks; implementing them using real molecular data that didn't exist until our recent publications  
- The biological ground truth now exists; we're building the bridge to clinical application

**Next Validation Steps:**

1. Extend schizophrenia axes to cross-disorder analysis  
2. Validate cross-modal imputation on held-out cohorts  
3. Demonstrate biosensor detection of axis-relevant biomarkers

---

## EQUITY

### Have you formed ANY legal entity yet?

Yes

### Please list all legal entities you have and in what state or country each was formed.

**Cytognosis Foundation**

- Delaware nonprofit corporation  
- Incorporated: September 8, 2024  
- IRS 501(c)(3) approved  
- EIN: 39-4383634

### Please describe the breakdown of the equity ownership in percentages among the founders, employees and any other stockholders.

As a 501(c)(3) nonprofit, there is no traditional equity ownership.

**Planned structure (in progress with general counsel):**

**Hybrid Nonprofit/PBC Model:**

- **Cytognosis Foundation (501(c)(3))**: Maintains mission control, holds IP, receives philanthropic funding  
- **Cytognosis Inc. (Delaware PBC)**: For-profit subsidiary for commercial operations, investor returns (capped), employee equity

**Proposed PBC equity allocation:**

- Founders: 60%  
- Employee pool: 20%  
- Investors: 20% (initially)

This structure enables:

- Mission alignment (nonprofit controls direction)  
- Investor returns (PBC enables equity upside)  
- Philanthropic leverage ($100M+ government/foundation funding)  
- Employee incentives (PBC equity)

### Have you taken any investment yet?

No

### Are you currently fundraising?

Yes

### Please provide any relevant details about your current fundraise.

**Active Applications (Non-dilutive):**

- ARPA-H Proactive Health Office: $52.5M over 5 years (submitted)  
- ARPA-H Health Science Futures: $25M (in preparation)  
- Convergent Research FRO program: $75-100M (in preparation)  
- Foresight Institute AI Node: $70-100K \+ compute (submitted)

**Planned Equity Round:**

- Seed: $3-5M (targeting Q2 2026\)  
- Use: Team expansion, Cytoverse development, biosensor architecture validation  
- Runway: 18 months

**Philanthropic Pipeline:**

- Gates Foundation: Initial discussions for global health deployment  
- Wellcome Trust: Health equity and open science alignment

---

## CURIOUS

### What convinced you to apply to Y Combinator? Did someone encourage you to apply? Have you been to any YC events?

1. **Will MacAskill's post** "Why nonprofits should apply to Y Combinator" on Effective Altruism opened my eyes to YC's acceptance of mission-driven organizations.

2. **YC's biotech track record**: Ginkgo Bioworks, 23andMe, Benchling prove YC understands long-horizon, capital-intensive biotech.

3. **Network effects**: YC's investor network and alumni community would accelerate partnerships (clinical sites, biosensor manufacturers, enterprise customers).

4. **Forcing function**: The 3-month sprint would compress 12 months of progress into Demo Day, exactly what we need to prove out Cytoverse and lock in biosensor strategy.

---

## BATCH PREFERENCE

### What batch do you want to apply for?

Summer 2026

---

## SUMMARY

**Cytognosis** is building the "GPS for Health": AI-native infrastructure for continuous molecular monitoring that detects disease years before symptoms emerge.

**The problem**: Healthcare spends $5.3T/year, 90% on chronic conditions, yet waits for symptoms before acting. By then, intervention windows have closed.

**Our solution**: Three integrated technologies:

- **Cytoverse**: AI mapping all human cellular states into continuous health coordinates  
- **Cytoscope**: Programmable biosensors for continuous 50-100+ biomarker tracking  
- **Cytonome**: On-device AI converting molecular data into personalized interventions

**Why us**:

- 20 years building the underlying science (Nature 2019, Science 2024\)  
- 37 years of personal urgency from misdiagnosis  
- First-mover on cellular atlases that make this possible

**Why now**:

- Foundation models \+ single-cell atlases \+ programmable biosensors converged in 2024  
- Market validated: Function Health (100K users), Zoe (500K users), CGM ($15B market)  
- Regulatory path clear: Wellness device → Clinical decision support

**The ask**: YC funding, network, and a forcing function to ship Cytoverse v0.3 and lock in the biosensor strategy by Demo Day.

**The vision**: A world where cellular intelligence is a human right. Where disease is prevented rather than treated. Where no one waits 37 years for answers that AI could provide today.

