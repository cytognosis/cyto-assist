# **Foresight AI for Safety & Science Nodes 2026**

## 

## About You

### Full name

Shahin Mohammadi

### Email address

[mohammadi@cytognosis.org](mailto:mohammadi@cytognosis.org)

### Affiliated organization(s) or project(s)

Cytognosis Foundation

### Website, CV, or LinkedIn profile link

[https://www.linkedin.com/in/shmohammadi/](https://www.linkedin.com/in/shmohammadi/)

### Applying as an

Organization

### Primary region

America

### Primary country

USA

### What type of org?

Non-profit \- US

---

## Track Record

### What is your/your team's track record?

Our team brings together computational neuroscience, AI systems architecture, and cross-scale brain mapping. Over the past decade, we have been active contributors to major international consortia, including PsychENCODE, PsychAD, and ROSMAP, helping build the first detailed molecular atlases of neuropsychiatric and neurodegenerative disease. This work spans 10+ publications in Science and Nature journals, with complementary expertise ranging from single-cell genomics and disease axis discovery (Mohammadi), to brain connectomics and multi-scale integration (Davila-Velderrain), to scalable AI and distributed systems (Grama).

* **Shahin Mohammadi**, PhD (PI/CEO, Cytognosis Foundation): 20 years building AI for biological and medical applications across academia (MIT, Broad Institute, Purdue University) and industry (insitro, GenBio AI). Creator of the ACTION/ACTIONet framework for single-cell analysis (github.com/shmohammadi/ACTIONet, 500+ stars), adopted by PsychENCODE, PsychAD, ROSMAP, and other major consortia. Co-led the first single-cell multi-cohort atlas of schizophrenia (Ruzicka, Mohammadi et al., Science 2024), which identified continuous disease axes and biologically distinct subtypes within one DSM diagnosis, the direct scientific foundation for this project. Co-led the multi-cohort atlas of bipolar disorder (Han, Mohammadi et al., Cell, under revision). Co-first author on the first single-cell atlas of Alzheimer's disease (Mathys, Davila-Velderrain, Mohammadi et al., Nature 2019), revealing cell-type-specific vulnerability years before clinical onset. Contributing author on the PsychENCODE capstone (Emani et al., Science 2024), integrating single-cell genomics across 388 human brains.  
* **Jose Davila-Velderrain, PhD** (Neuroverse Co-Lead, Human Technopole Milan): Group Leader in Computational Neuroscience at Human Technopole. Co-developed the PsychAD single-cell atlas (Science 2024), led the Alzheimer's hippocampal atlas (Nature Medicine 2021), and contributed to APOE4 mechanisms in oligodendrocytes (Nature 2022). Provides cross-scale integration expertise bridging molecular and circuit-level neuroscience.  
* **Ananth Grama, PhD** (Scientific Advisor, Purdue University): Samuel Conte Distinguished Professor and Director of the Institute for Physical AI (IPAI) at Purdue. Expert in AI models, methods, and interpretability, scalable computing, and distributed systems. Provides guidance on foundation model architecture and compute optimization.

### Project participant(s) (including roles and links)

- PI / CEO: Shahin Mohammadi, PhD ([https://www.linkedin.com/in/shmohammadi/](https://www.linkedin.com/in/shmohammadi/))  
- Neuroverse Co-Lead: Jose Davila-Velderrain, PhD, Group Leader, Human Technopole Milan  
- Scientific Advisor: Ananth Grama, PhD, Distinguished Professor, Purdue IPAI Director

### Full name and email of a primary reference

Brad Ruzicka, PhD, Assistant Professor, McLean Hospital / Harvard Medical School. Co-first author on our Science 2024 schizophrenia atlas. Can speak to the quality and scientific impact of our molecular neuroscience work and the potential of the Neuroverse framework. Contact to be provided upon request.

---

## About Your Project

### What are you applying for?

Funding (Grant), Physical node access (Bay Area), Local compute

### Foresight focus area

AI for Neuro, Brain-Computer Interfaces & Whole Brain Emulation

### Project title

**Neuroverse**: An Open-Source, Private Mental Health Compass for Everyone

### What are you trying to do? (max 350 characters)

We treat mental health the way we treated diabetes before glucose monitors: blind between visits, one-size-fits-all, decades behind the science. We are building open-source, on-device AI that continuously maps mental health through conversation and wearable sensors. A personal mental health compass for everyone: always on, fully private, and free.

### How is today's approach limited? What is new in your approach, and what does success look like?

#### Today's Limits

Mental health assessment is stuck in the 1950s. A patient visits a clinician once every few weeks, completes a questionnaire (PHQ-9, GAD-7), receives a categorical label (e.g., "moderate depression"), and receives treatment that fails in 47-58% of cases (STAR\*D; Rush et al. 2006). Between visits, clinicians have zero visibility into the patient's actual trajectory. Two patients with identical PHQ-9 scores of 15 may have entirely different underlying biology, yet they receive the same first-line treatment.

Three specific failures define the current landscape:

1. **Static generic snapshots instead of personalized trajectories**. Continuous glucose monitoring revealed that dietary responses are profoundly personal: the same food can cause glucose spikes in some people but not in others. Mental health has no equivalent continuous monitor. We miss the patterns of deterioration and recovery that would enable timely intervention, and we have no way to measure treatment response between clinical visits.  
2. **Privacy barriers prevent honest engagement.** People already struggle to share mental health concerns even with therapists. Current AI mental health tools are cloud-based and require deeply personal psychological data to be sent to corporate servers. This creates a fundamental trust barrier. A 2024 JAMA study found that general-purpose LLMs can reinforce harmful patterns and, in extreme cases, may contribute to suicidal ideation. Purpose-built, on-device models have the potential to eliminate this risk entirely.  
3. **Behavioral tracking is disconnected from neurobiology.** NIMH introduced Research Domain Criteria (RDoC) over a decade ago as a dimensional alternative to DSM categories, and Grotzinger et al. (Nature 2026\) demonstrated that the genetic architecture across 14 psychiatric disorders maps onto a five-factor model consistent with HiTOP. However, no computational system connects behavioral-level tracking to these molecular dimensions. The behavioral layer that could make molecular psychiatry accessible to millions simply does not exist.

#### What's New

We aim to replace reactive, generic, and categorical mental health care with a system that is proactive, personalized, and multidimensional, starting with the behavioral study layer that makes this accessible to everyone.

The Neuroverse is a multi-scale framework we are developing at Cytognosis Foundation that maps brain disease along three complementary scales: **Micro** (genotype plus single-cell transcriptomics), **Meso** (brain connectomics via fMRI/fNIRS/EEG), and **Macro** (behavioral plus wearable physiology). Our scientific credibility at the molecular scale is established: our Science 2024 work identified continuous disease axes within schizophrenia, our Nature 2019 work revealed pre-symptomatic cell-type vulnerability in Alzheimer's, and Grotzinger et al. (Nature 2026\) confirmed shared genetic dimensions organize psychiatric variation across 14 disorders into a five-factor structure.

The critical missing piece, and the focus of this Foresight project, is the broadly-accessible Macro study layer: one that runs on consumer devices and can eventually connect these molecular axes to individual monitoring at scale.

This Foresight project builds that Macro study layer through three innovations:

1. Privacy-first edge AI for mental health. We deploy purpose-built compact language models (3B parameters or smaller) entirely on-device using emerging Edge AI architectures. All personal data stays on the user's device with no cloud dependency. Only anonymized, aggregated population features are shared for model improvement via federated learning with differential privacy guarantees. These are not general-purpose chatbots; they are specialized for mental health state quantification, where focused models can match larger centralized models on specific clinical tasks (Weber et al. 2025; Kambeitz et al. 2025).

2. Continuous dimensional mental health coordinates. Rather than categorical labels, our system generates continuous scores along data-driven axes of mental health variation. We fine-tune against validated clinical instruments (PHQ-9, GAD-7, PSS-10, PCL-5) and combine with wearable sensor streams: heart rate variability, sleep architecture, temperature, and activity from the Oura Ring 4 (validated: r=0.99 RHR, r=0.88 HRV vs. ECG gold standard; Kinnunen et al. 2020), plus prefrontal cortex hemodynamics from the Muse S Athena (the only consumer device combining EEG and fNIRS). This creates a multimodal representation that captures what questionnaires miss: a subject's personal trajectory between visits.

3. Personalized baselines with deviation detection. Each individual's model learns their typical patterns across conversational, physiological, and neural data streams. This enables detection of clinically meaningful deviations from personal baselines, which is critical because absolute scores vary enormously between individuals, and a "normal" score for one person may represent a significant decline for another.

All models, training code, evaluation benchmarks, and deployment toolkits are released as open-source public goods under the Apache 2.0 license for code and model weights, and CC BY 4.0 for documentation and non-personal data. We follow a "truly open" standard: not just open-weights, but full transparency into the entire training pipeline (data, code, weights, evaluation). The edge AI architecture directly aligns with Foresight's mission of building capacity for private local compute. Our open-source implementation provides a reusable blueprint for any health AI application that requires privacy-preserving on-device processing.

#### Success Looks Like

Our strategic plan has two proposed variations:

1. **Option A (sequential build with primary focus on building the behavioral model first)**: An on-device mental health assessment engine validated against clinical standards (r \> 0.7 with PHQ-9/GAD-7), running entirely on consumer smartphones. Continuous dimensional mental health coordinates for each user, derived from conversational AI, replacing episodic snapshots with trajectories. An edge AI deployment toolkit (model weights, training code, federated learning infrastructure) released under Apache 2.0, serving as a reusable blueprint for privacy-preserving health AI.  
2. **Option B (concurrent build of behavioral and connectomic models)**: At 18 months with Option B, we deliver everything in A, plus: Multimodal fusion integrating conversation, wearable physiology (Oura Ring 4), and neural signals (Muse S Athena EEG/fNIRS) into unified mental health coordinates. Our first-ever proprietary multimodal dataset from the Phase 0 internal pilot (core team, 3 months). A 20 to 30-person external pilot demonstrating that continuous multimodal tracking detects clinically meaningful changes that periodic assessment misses. Publication-ready results and preliminary data that make an ARPA-H follow-on proposal competitive.

### If there are risks, is it possible to differentially advance safety-enhancing aspects of the technology first?

Safety in AI-powered mental health monitoring operates across three distinct domains, each requiring purpose-built safeguards. We address all three, and we build the safety infrastructure first.

#### 1\. Patient Safety in Mental Health Monitoring

Mental health conditions carry inherent risks, including episodes of crisis, self-harm, and suicidal ideation. Any monitoring system must reliably detect these events. We build hard-coded crisis detection into every on-device model: when risk indicators are detected, the system immediately surfaces professional resources (988 Suicide and Crisis Lifeline, Crisis Text Line) and, where the user has opted in, alerts a designated clinician or emergency contact. This mirrors the duty-to-warn framework that governs therapist-patient relationships, under which confidentiality is maintained except when there is an imminent risk of harm to self or others. The system explicitly does not attempt therapy or crisis intervention; it augments professional care by providing clinicians with continuous data between visits and by serving as an always-available safety net for early warning.

#### 2\. Safety of the Patient in LLM Interactions

Recent reports have documented serious harms from individuals using general-purpose LLMs for emotional support, including reinforcement of harmful thought patterns, inappropriate therapeutic advice, and, in extreme cases, contributions to suicidal ideation (JAMA 2024). These risks arise because general-purpose models are not designed for mental health contexts and lack appropriate guardrails. Our approach addresses this directly: the on-device models are purpose-built for quantifying mental health states and structured assessment, not for open-ended therapeutic conversation. They are trained against validated clinical instruments with explicit failure-mode analysis across demographics, severity levels, and linguistic backgrounds. Development proceeds only along dimensions where correlation with validated instruments exceeds r \> 0.6, with transparent reporting of where models fail. A bias audit protocol is published before any model release.

#### 3\. Protection of Sensitive Mental Health Data

Mental health data is among the most sensitive categories of personal information, arguably more vulnerable to abuse and discrimination than even genetic data. Employment decisions, insurance coverage, custody proceedings, immigration status, and security clearances can all be affected by mental health records. The risk of data breaches or misuse is not hypothetical; it is a documented barrier that prevents people from seeking care in the first place. As Abdmeziem and Ahmed Nacer (2025) detail in their analysis of IoT-LLM integration for mental health, continuous monitoring compounds these risks by generating longitudinal behavioral profiles far more revealing than any single clinical encounter.

Our core mitigation is architectural: all personal data stays on the device at all times. Beyond this baseline, we are designing an open protocol with a layered privacy architecture:

**Perception Layer (Edge AI):** All sensor processing, voice interaction, and personalized health modeling runs locally on the user's device. Raw data (conversation transcripts, physiological signals, neural recordings) never leaves the device, regardless of the architecture.

**Decentralized Infrastructure Layer:** For collective model improvement, we adopt a privacy-first shared compute-and-storage model inspired by blockchain consensus mechanisms and peer-to-peer distribution (similar to BitTorrent). This allows users to benefit from population-scale learning without any single organization owning the data, introducing a single point of failure, or creating a centralized honeypot for breaches. Federated learning with formal differential privacy guarantees (explicit epsilon budgets) ensures that individual contributions cannot be reverse-engineered from aggregate updates.

**External Interaction Layer:** When interaction with more capable external models is necessary (e.g., for complex clinical reasoning that exceeds on-device capacity), the system sends only encrypted, model-derived embeddings rather than raw data. These embeddings are designed to preserve the clinical information needed for inference while stripping personally identifiable patterns. Additional strategies include secure multi-party computation and homomorphic encryption for specific query types.

This three-layer architecture is itself an open-source contribution: all protocol specifications, reference implementations, and security audit frameworks are released under the Apache-2.0 license. The code is not "trust us" security; it is "verify it yourself" security. Any researcher or organization can audit every privacy claim, and the community can improve the safeguards over time.

#### Safety-First Development Order

Safety infrastructure is built and validated before any participant-facing system exists:

Months 1 to 6: Privacy architecture, crisis detection module, bias audit framework, and the open protocol specification. All safety systems are deployed, tested, and open-sourced before any participant interaction.

Months 7 to 12: Clinical validation against gold-standard assessments. Models are evaluated for safety and accuracy before they are used for tracking.

Months 13 to 18: Pilot deployment only after all safety benchmarks pass.

### Please outline the start and end times, as well as your key project milestones.

#### Phase 1: Foundation (Months 1 to 6, Apr to Sep 2026\) \[Options A and B\]

Months 1 to 2: Data pipeline and safety infrastructure. Deliverables: Crisis detection module; bias audit protocol; open protocol specification (layered privacy architecture); IRB submission; training data curation from public clinical dialogue datasets paired with PHQ-9/GAD-7 scores.

Months 3 to 4: Base model fine-tuning. Deliverables: 3B parameter or smaller model fine-tuned for mental health state quantification using Low-Rank Adaptation (LoRA) plus Direct Preference Optimization (DPO) on Foresight local compute; clinical correlation benchmarks.

Months 5 to 6: Edge optimization. Deliverables: Model distilled and quantized for on-device deployment; retrospective validation against clinical datasets.

Go/No-Go at Month 6: Does the fine-tuned model achieve r \> 0.6 correlation with PHQ-9 and GAD-7 on held-out clinical data? If not, iterate on training data and model architecture before proceeding.

#### Phase 2a: Phase 0 Internal Pilot (Months 7 to 9, Oct to Dec 2026\) \[Option B only\]

Month 7: Wearable integration and self-instrumentation. Core team (3 to 5 people) begins daily use of all sensors plus daily conversational assessment. Oura Ring 4 API and Muse S Athena SDK integration.

Month 8: Multimodal data collection. Continuous data streams: AI-derived mental health scores, HRV/sleep/activity, EEG/fNIRS prefrontal hemodynamics, all from the same individuals. Biweekly self-administered clinical assessments for ground truth.

Month 9: Multimodal fusion model v0. First multimodal model trained on Phase 0 data. Internal benchmarking of conversation-only vs. conversation plus physiology vs. full multimodal. Pipeline debugging and refinement.

Why Phase 0 matters: This is the single most important de-risking step in the project. We answer "Does our multimodal pipeline actually produce meaningful signals from real humans?" on ourselves before recruiting external participants. No recruitment delays, no participant safety concerns, no regulatory complexity, just rapid iteration on the methodology.

#### Phase 2b: Validation (Months 10 to 12, Jan to Mar 2027\) \[Options A and B\]

Month 10: Federated learning infrastructure. Differential privacy framework; on-device personalization pipeline; aggregation protocol.

Month 11: Clinical validation. Option A: Retrospective validation against clinical datasets. Option B: Prospective validation using Phase 0 multimodal data plus retrospective benchmarks.

Month 12: Publication and interim release. Validation results published as open-access preprint; open-source release of all models, training code, evaluation benchmarks, and deployment configurations under Apache 2.0.

Go/No-Go at Month 12: Option A: Does edge deployment maintain clinical correlation within 5% of cloud-based inference? Option B: Does the multimodal system outperform single-modality (conversation-only) assessment?

#### Phase 3: External Pilot (Months 13 to 18, Apr to Sep 2027\) \[Option B only\]

Months 13 to 14: Pilot enrollment and baseline. 20 to 30 participants (MDD, GAD, PTSD, neurotypical). Baseline clinical assessments; device distribution.

Months 15 to 16: Continuous monitoring. 3 months of daily tracking; biweekly clinical assessments for ground truth; personalized baseline learning.

Months 17 to 18: Analysis and final release. Pilot results: models, code, and anonymized data released as open-source public goods; publication; ARPA-H proposal submission.

Option A at Months 13 to 18: Focuses on extended retrospective validation, model refinement, open-source documentation, and community building at the Foresight node.

#### Key Deliverables Summary

- Month 2: Crisis detection module, bias audit framework, and open protocol specification (Options A and B)  
- Month 4: Fine-tuned mental health LLM, 3B parameters or smaller (Options A and B)  
- Month 6: Edge-optimized model plus deployment toolkit, open-sourced under Apache 2.0 (Options A and B)  
- Month 9: Phase 0 internal multimodal dataset (Option B only)  
- Month 9: Multimodal fusion model combining conversation, wearable, and EEG/fNIRS (Option B only)  
- Month 10: Federated learning infrastructure with differential privacy (Options A and B)  
- Month 12: Clinical validation report and open-access preprint; retrospective for A, prospective for B (Options A and B)  
- Month 18: 20 to 30 person external pilot results (Option B only)  
- Month 18: Full Neuroverse Macro platform; software only for A, software plus hardware plus data for B  
- Ongoing: All deliverables open-source (Apache 2.0 for code/models, CC BY 4.0 for documentation/data)

### If this project goes well, how do you plan to scale it to have the impact needed for safe AI in 3 years?

#### Year 2 (2027 to 2028): Clinical-Scale Validation via ARPA-H Proposal

The Neuroverse Macro is the broadly accessible entry point to a multi-scale precision psychiatry platform. Successful completion of this 18-month project provides the preliminary data and validated technology to unlock three scaling vectors.

With Option B, the Phase 0 and Phase 1 pilot data from this project directly feed into an ARPA-H proposal for the Precision Health Outcomes (PHO) program. We arrive at the proposal with our own multimodal dataset and validated methodology. With Option A, we would first need to secure a small intermediate grant ($30 to 50K) to run the pilot before submitting to ARPA-H. Either path leads to the same destination, but Option B gets us there 6 to 12 months faster.

Target: 500 to 1,000 participants in a study across 6 psychiatric conditions (MDD, GAD, PTSD, BD, SZ, SUD) with validated continuous monitoring. The Foresight-funded edge AI architecture and open-source toolkit become the backbone of this larger deployment. By Year 2, increasingly powerful on-device AI (models that are 7B+ today will run on phones by 2028\) will enable richer conversational assessment without any cloud dependency.

#### Year 2 to 3 (2027 to 2029): Cross-Scale Integration, Connecting Macro to Micro

This is where the Neuroverse becomes uniquely powerful. Using the validated Macro behavioral coordinates from this project, we connect them to our established Micro-scale molecular data (NeuroBioBank 10K+ genomes, PsychENCODE 388 paired WGS plus single-cell transcriptomes). The question becomes: can we predict which molecular subtype a patient belongs to from their behavioral plus wearable trajectory alone? If yes, this transforms precision psychiatry from something requiring a brain biopsy to something running on your phone. Emerging multimodal AI capabilities (foundation models that integrate text, time-series, and omics data) will make this cross-scale bridge feasible at a scale impossible today.

#### Year 3 (2028 to 2029): Population Deployment as Open-Source Public Good

Target: 5,000+ users continuously monitored. All models, datasets, federated learning infrastructure, and clinical validation results are released as open-source public goods under Apache 2.0 (code/models) and CC BY 4.0 (documentation/non-personal data). The Neuroverse Macro becomes a platform that any researcher, clinician, or public health system can deploy, with no proprietary lock-in, no corporate data collection, and no subscription fees. Edge AI capabilities maturing over 3 years (on-device models approaching 10B+ parameters) mean the system gets more powerful while remaining entirely private.

#### Impact on Safe AI

Open-source privacy blueprint. Our edge AI plus federated learning architecture, including the three-layer open protocol for privacy-preserving IoT-LLM integration, is a reusable template for any health AI application requiring privacy preservation. Every component is auditable. This directly advances Foresight's goal of building capacity for private local compute.

Interpretable disease dimensions. Mental health coordinates grounded in validated clinical constructs, not opaque embeddings, ensure clinicians and patients can understand model outputs. As we connect to the molecular Neuroverse, axes gain biological interpretability (cell types, pathways, genetics) rather than remaining black-box predictions.

Equity by design. Open-source architecture ensures precision mental health is accessible globally. No subscription wall. No corporate data harvesting. The system runs on any modern smartphone, the most ubiquitous computing platform on earth.

### Share any additional information and links you may find useful for us to know.

#### Key Publications

1. Ruzicka WB, Mohammadi S, et al. (2024). Single-cell multi-cohort dissection of schizophrenia. Science 384(6698). Identified continuous disease axes within one DSM diagnosis.  
2. Mathys H, Davila-Velderrain J, Mohammadi S, et al. (2019). Single-cell transcriptomic analysis of Alzheimer's disease. Nature 570, 332 to 337\. First single-cell Alzheimer's atlas.  
3. Emani PS, et al. (incl. Mohammadi S, Davila-Velderrain J) (2024). PsychENCODE: Single-cell genomics across 388 human brains. Science 384(6698).  
4. Han S, Mohammadi S, et al. (2024/2026). Single-cell multi-cohort transcriptomic dissection of bipolar disorder. Cell (under revision after the first round of reviews).  
5. Grotzinger AD, et al. (2026). Mapping the genetic landscape across 14 psychiatric disorders. Nature 649(8096), 406 to 415\.

#### Existing Open-Source Contributions

- ACTIONet: github.com/shmohammadi/ACTIONet (500+ stars). Single-cell analysis framework adopted by PsychENCODE, ROSMAP, and other major consortia. Licensed under Apache 2.0.  
- ACTION: github.com/shmohammadi/ACTION. Core algorithms for archetypal analysis of multi-omic data.

#### Supporting Literature

- Kambeitz J et al. (2025). Structure of psychopathology is represented in LLM embedding spaces.  
- Weber S et al. (2025). Fine-tuned LLMs achieve clinically relevant accuracy for depression evaluation.  
- Onysk J, Huys QJM (2025). Quantifying depressive states with LLMs.  
- Hua Y et al. (2025). LLMs for mental health care: scoping review.  
- Kinnunen H et al. (2020). Oura Ring validation: feasible for nocturnal HR and HRV monitoring. Physiological Reports.  
- Torous J et al. (2017). Digital phenotyping via smartphones within RDoC. Translational Psychiatry.  
- Tozzi L et al. (2024). Brain circuit biotypes in depression/anxiety. Nature Medicine.  
- Abdmeziem MR, Ahmed Nacer A (2025). Leveraging IoT and LLM for depression and anxiety disorders: a privacy-preserving perspective. Preprint, HAL-05038835.

#### Strategic Alignment with Foresight

Private local compute: Our project demonstrates that clinically meaningful AI health monitoring can operate entirely on consumer hardware, advancing Foresight's core interest in alternatives to centralized cloud AI.

AI for Neuro: We are building computational infrastructure to map the human neuropsychiatric landscape, directly aligned with Foresight's Neuro/BCI priority.

Open-source commitment: Every deliverable is released under permissive open-source licenses (Apache 2.0 for code/models, CC BY 4.0 for documentation/data). We follow a "truly open" standard: not just open-weights, but full transparency into the entire training pipeline. All models, code, data pipelines, evaluation benchmarks, and validation results are public goods.

Safety-first: Privacy architecture, crisis detection, and bias audits precede model deployment. The three-layer open protocol for privacy-preserving IoT-LLM integration is itself an open-source safety contribution applicable beyond mental health. Interpretable disease dimensions prevent black-box clinical decisions.

#### Context: Cytognosis Foundation

Cytognosis Foundation is a 501(c)(3) nonprofit incorporated in Delaware, founded in 2024 to build open-source computational infrastructure for precision medicine. The Neuroverse is our first major program. We are applying for our first external grant. This proposal represents the transition from self-funded development to externally supported research. The Foresight grant would be transformative for our ability to execute.

---

## About Your Request

### Physical Node

#### Which node are you interested in?

Bay Area

#### For how long do you want to use the space?

18 months: April 1, 2026–September 30, 2027

#### Who in your team wants to use the space?

Full-time (4 to 5 days/week): Shahin Mohammadi (PI/CEO), throughout the 18-month period.

Part-time (as needed): 1 ML Engineer (to be hired with grant funding), 3 to 4 days/week during Phases 2 and 3\. Visiting collaborators (Jose Davila-Velderrain, clinical partners) on a periodic basis.

Total: 1 to 2 people regularly, occasionally 3\.

#### How do you want to use the space?

Physical office, Co-working

#### How are you planning to use the node / contribute to the community?

Direct contributions:

1. Quarterly open sessions on privacy-preserving health AI. Practical workshops covering: edge model deployment, federated learning implementation, differential privacy for health data, and on-device inference optimization. These are transferable skills relevant to any Foresight project working with sensitive data, not just neuro.

2. Open office hours. Weekly 2-hour blocks where other Foresight teams can get hands-on help with foundation model fine-tuning, single-cell analysis, multimodal data fusion, or edge AI deployment.

3. Shared infrastructure and tooling. All our ML pipeline templates, sensor integration code, federated learning frameworks, and deployment configurations will be documented and shared as open-source toolkits that other node projects can adopt.

4. Cross-project collaboration. We actively seek integration with BCI projects (our neural data processing could provide features for BCI decoding), longevity bio projects (the Neuroverse framework extends to neurodegeneration, since our Nature 2019 Alzheimer's atlas is foundational), and AI safety projects (our interpretable disease axes are a case study in transparent AI for healthcare).

5. Neurotechnology Seminar Group participation. Active engagement in Foresight's Neuro seminar group, presenting results and learning from other groups.

Community building: Participate in all Foresight events and workshops. Host visiting researchers from Human Technopole (Milan) and Purdue. Mentor early-career researchers interested in neuroAI.

#### Workshop participation?

Yes

### Funding

#### Are you requesting funding?

Yes

#### Will there be overhead?

No. Cytognosis Foundation will apply 100% of funding directly to project costs. As a lean nonprofit, we have no indirect cost rate.

#### How much funding do you request (USD)?

$45,000 to $75,000 (see Options A and B below)

We present two funding levels that deliver different scopes.

#### Please break down your funding request precisely.

##### Option A: $45,000 total (On-Device Mental Health AI, Macro Software Only)

At this level, we build and validate the core AI system: an open-source, on-device language model fine-tuned for continuous quantification of mental health states, validated retrospectively against existing clinical datasets.

- Personnel: $18,000 (40%). Part-time ML engineer specializing in edge AI (6 months, approximately $3K/mo). Handles model distillation, quantization, and on-device optimization.  
- Edge AI hardware: $4,000 (9%). 1x NVIDIA DGX Spark (GB10), 128GB unified memory, 1 PFLOP FP4. Edge inference development platform.  
- Data infrastructure: $3,000 (7%). Secure storage, encrypted backup, API costs, and licensing for clinical datasets.  
- IRB and regulatory: $2,000 (4%). IRB submission and review fees; informed consent preparation.  
- Travel and collaboration: $3,500 (8%). Collaborator visits; 1 to 2 conference presentations.  
- Open-source infrastructure: $2,000 (4%). Documentation, CI/CD, model hosting (Hugging Face), community tooling.  
- Contingency: $2,500 (6%). Unforeseen costs.  
- Subtotal: $35,000  
- Plus Foresight compute: approximately $10,000 value (approximately 2,500 GPU-hours for model training)  
- Effective total: approximately $45,000

Option A delivers: A validated, open-source, on-device mental health LLM with an edge deployment toolkit released under Apache 2.0, validated against existing clinical datasets only (retrospective). No wearable integration. No prospective human data collection.

What Option A leaves out: Wearable sensor integration, EEG/fNIRS neural data, and any prospective human data collection. The models would be validated on existing clinical datasets, but we would not yet have our own multimodal dataset linking AI-derived mental health scores to real physiological signals from real people. This means the critical question ("Does continuous multimodal monitoring detect what periodic assessment misses?") remains unanswered.

##### Option B: $75,000 total (On-Device AI \+ Wearable Sensors \+ Phase 0 Internal Pilot, Recommended)

At this level, we build everything in Option A, purchase wearable hardware (Oura Ring 4 for physiological signals, Muse S Athena for EEG/fNIRS neural data), and run a Phase 0 internal pilot within our core team before recruiting any external participants. This creates our first-ever multimodal dataset linking AI-derived mental health coordinates to physiological and neural signals, and de-risks the methodology before running a formal pilot.

- Everything in Option A: $35,000 (47%).  
- Wearable sensors: $12,000 (16%). 10x Oura Ring 4 ($5,000) for HRV/sleep/activity, 5x Muse S Athena ($2,500) for EEG/fNIRS, 5x Emotiv Insight ($2,500) for 5-ch EEG validation, plus accessories.  
- Phase 0 internal pilot: $5,000 (7%). 3-month self-experimentation within core team (3 to 5 people): daily device wear, biweekly clinical self-assessment, multimodal data collection. Covers consumables, data management, and clinical assessment tools.  
- Extended personnel: $9,000 (12%). ML engineer extension (3 additional months) for multimodal fusion model development plus wearable SDK integration.  
- Participant compensation: $4,500 (6%). 20 to 30 external pilot participants at $150 to $225 each for a 3-month study (Phase 1, after Phase 0 validation).  
- Additional contingency: $2,000 (3%). Device replacements, additional recruitment.  
- Subtotal (new items): $32,500  
- Total: $67,500  
- Plus Foresight compute: approximately $10,000 value (approximately 3,200 GPU-hours, additional training for multimodal fusion)  
- Effective total: approximately $77,500

Option B delivers everything in Option A, plus:

1. Phase 0 internal pilot (Months 7 to 9): The core team (3 to 5 people) wears all sensors daily for 3 months, generating the first-ever Neuroverse multimodal dataset: conversation-derived mental health scores, Oura Ring physiology, Muse S Athena EEG/fNIRS, and Emotiv EEG, all from the same individuals. This is low-risk (no external participants), fast (no recruitment delays), and gives us ground truth for the multimodal fusion model before involving external participants.

2. Multimodal fusion model: Trained on Phase 0 data. The system that integrates conversational AI, physiological wearables, and neural signals into a unified mental health framework. This is the piece that transforms the project from "another mental health chatbot" into a genuinely novel multi-signal platform.

3. Phase 1 external pilot (Months 13 to 18): 20 to 30 participants across clinical populations (MDD, GAD, PTSD, neurotypical), using a methodology already validated on ourselves in Phase 0\. Generates publication-ready results and preliminary data for ARPA-H follow-on.

Why Option B is worth the additional $30K: The Phase 0 self-experimentation is the single most de-risking step we can take. It answers "does our multimodal pipeline actually work on real humans?" before we spend resources on external recruitment. It also produces our first proprietary dataset, without which we are building AI on other people's data only, and our follow-on proposals (ARPA-H, NSF) lack the preliminary results that make them competitive.

##### Cost-effectiveness rationale (both options)

- Primary compute is from Foresight's local allocation, not from the monetary grant. This saves an estimated $5,000 to $15,000 in cloud GPU costs.  
- Zero overhead. Every dollar goes to direct project costs.  
- Open-source output maximizes impact per dollar. All deliverables are released under permissive licenses (Apache-2.0 / CC BY 4.0), ensuring that every funded artifact benefits the broader community.  
- Leverages $0 existing external funding. This is our first grant. Approval signals viability for larger follow-on proposals (ARPA-H, NSF) that will scale the work by 10 to 100x.  
- AI reduces personnel costs. We use AI-assisted code generation, literature review, and experiment design throughout.

#### Do you have an ambitious or moderate version?

Yes. Option A ($45,000) is the moderate version: it delivers a validated, open-source, on-device mental health LLM with an edge deployment toolkit, validated retrospectively against existing clinical datasets. No wearable sensors and no prospective human data collection.

Option B ($75,000) is the ambitious version: it adds wearable sensors (Oura Ring 4, Muse S Athena, Emotiv Insight), a 3-month Phase 0 internal pilot with our core team generating our first multimodal dataset, and a Phase 1 external pilot with 20 to 30 participants. This produces preliminary data for ARPA-H follow-on proposals and answers the critical question of whether continuous multimodal monitoring detects what periodic assessment misses.

### Compute

#### Are you requesting compute?

Yes

#### How many GPU hours do you expect to need?

Total estimate: approximately 2,500 GPU-hours (Option A) to 3,200 GPU-hours (Option B), A100-equivalent, over 18 months.

- Phase 1 (Months 1 to 6): 1,200 GPU-hours, 90% training / 10% inference. Base model fine-tuning (LoRA plus DPO on 3B or smaller model); sparse autoencoder training for interpretable feature extraction; edge model distillation and quantization.  
- Phase 2a (Months 7 to 9, Option B only): 700 GPU-hours, 70% training / 30% inference. Multimodal fusion model training (conversation plus physiological plus neural streams from Phase 0 data); wearable signal encoding models.  
- Phase 2b (Months 10 to 12): 800 GPU-hours, 60% training / 40% inference. Federated learning simulation; clinical validation experiments; ablation studies.  
- Phase 3 (Months 13 to 18): 500 GPU-hours, 30% training / 70% inference. Pilot data analysis (Option B) or extended validation (Option A); personalized model fine-tuning; population-level aggregation.

Overall split: approximately 70% training / 30% inference.

GPU type needed: A100 80GB (sufficient for 3B or smaller model fine-tuning and multimodal fusion). H100 preferred if available (faster iteration).

Open-source commitment: All models trained on Foresight compute will be released open-source under Apache 2.0, with full training code, configurations, reproducibility scripts, model cards, and evaluation benchmarks.

#### Would your project benefit from access to local, private compute?

Yes, this is central to our project's design and value proposition.

Our project specifically demonstrates that clinically meaningful health AI can operate on private, local infrastructure. Using Foresight's local compute for training directly embodies this principle:

1. Training data sensitivity. Fine-tuning on de-identified mental health assessment data is sensitive. Local compute ensures that no clinical dialogue data is transmitted to third-party cloud providers.

2. Reproducible open-source training. By training on Foresight's documented local infrastructure, we can provide exact reproducibility instructions that do not depend on proprietary cloud configurations.

3. Blueprint for private health AI. The training pipeline we develop on Foresight's local compute becomes part of the open-source release, demonstrating to the community that private compute is viable for health AI model development, not just inference.

Requirements: 4x A100 80GB or equivalent; standard NVMe storage (2TB or less) for dataset processing; Python/PyTorch/HuggingFace stack.

---

## Miscellaneous

### Consent to share with advisors?

Yes

### Expedited processing needed?

No

### Confidential information

None

### How did you discover this opportunity?

Foresight website and community network

### Seminar groups

- Neurotechnology Seminar Group  
- Longevity Biotech Seminar Group

