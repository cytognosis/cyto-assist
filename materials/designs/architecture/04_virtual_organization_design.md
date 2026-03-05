# Virtual Organization Architecture

The Virtual Organization (VO) represents Cytognosis's novel approach to compounding, structuring, and routing AI capabilities through hierarchical personas. Instead of treating Large Language Models as flat homogeneous agents loaded with disjointed tooling, the VO architecture structures them as distinct employees operating within semantic bounds defined by organizational charts.

## 1. The Core Principles

### Graph-Based Persona Construction

Rather than writing exhaustive monolithic prompts for different capabilities (e.g. Bioinformatician vs Grant Writer), personas are defined as nodes in a directed cyclical graph of dependencies mapping out to specific discrete capabilities known as `Skills`.

- **Inheritance**: Personas specify an `inherits` list which acts identically to object-oriented programming. A `Grant Writer` inherits the `Communication Specialist` persona, which inherits the `Cytognosis Brand` skill and the `Markdown Writing` skill.
- **Overrides**: An inheriting persona can override or augment the quantitative weights associated with specific skills.

### The Virtual Hiring Process

Instantiating an agent for a specific workspace is referred to as "Virtual Hiring." Through the `agent-skills-cli` framework orchestrated inside the `nox` configuration interface, a Virtual Hiring resolves the full inheritance tree for a specific persona yaml definition, gathers all explicit constraints and instructions attached to the linked `.md` descriptions, and compresses the final unified representation into the agent's core initial prompt framework.

## 2. Structure mapping

The configurations operate under `configs/virtual_organization/`:

```text
virtual_organization/
├── organization.yaml        # Top-level organizational graph properties
└── personas/
    ├── engineering/         # Engineering teams (Agent Engineer, ML Architect)
    ├── science/             # Scientific teams (Bioinformatician, Research Scientist)
    └── business/            # Business logic (Grant Writer, Regulatory Specialist)
```

## 3. Skill Bundling and Installation

A critical extension to basic Virtual Hiring is the implementation of Skill Bundles. The `noxfile.py` orchestrator provides functionality for injecting comprehensive bundles without manual parsing.

### Available Default Bundles

- **Deep Learning**: Bundles [torch-geometric, ml-foundations, scientific-visualization]
- **Web Development**: Bundles [react-expert, nextjs-developer, typescript-pro, cytognosis-design-system]
- **Bioinformatics**: Bundles [genomics-toolkit, single-cell-analysis, biomedical-databases]

By utilizing `nox -s bundle_skills -- <bundle_name>`, the Cytognosis agent-skills toolkit executes rapid installations caching the distinct primitives into the agent's `/home/mohammadi/.agents/skills/` paths.

## 4. Analytical Feedback Loops

Through standardized CLI linting integration, Virtual Personas are systematically quantified using `agent-skills-cli analyze`. This enforces Cytognosis's progressive disclosure strict formatting (header metadata, `NEVER` boundaries, explicit triggers, file length caps). The analytical metrics ensure organization-wide constraints hold true regardless of external model changes.
