> **Navigation**: [← Design Index](../README.md) · [Research](../research/README.md) · [Architecture](README.md) · [Products](../products/README.md)

# Orchestration Architecture Design
## Multi-Agent System with LangGraph

---

# Core Orchestration: LangGraph

LangGraph provides graph-based state machines with durable state, human-in-the-loop, and provider-agnostic LLM support. Our agents communicate via structured message passing with typed state.

## Agent Team Structure

```mermaid
graph TB
    subgraph "Orchestrator"
        Router["🎯 Router Agent<br/>Classifies intent, routes to team"]
    end

    subgraph "Document Team"
        Parser["📄 Parser Agent<br/>Extracts content from any format"]
        Analyzer["🔍 Analyzer Agent<br/>Understands structure, entities"]
        Generator["✍️ Generator Agent<br/>Creates templated outputs"]
    end

    subgraph "Knowledge Team"
        KGWriter["📝 KG Writer Agent<br/>Stores entities/relations"]
        KGReader["📖 KG Reader Agent<br/>Queries KG for context"]
        Mapper["🗺️ Entity Mapper<br/>Maps to standard ontologies"]
    end

    subgraph "Communication Team"
        Voice["🎤 Voice Agent<br/>STT/TTS pipeline"]
        GWorkspace["📊 GWorkspace Agent<br/>Google Docs/Slides/Drive"]
        Notifier["🔔 Notifier Agent<br/>Sends alerts, summaries"]
    end

    Router --> Parser
    Router --> KGReader
    Router --> Voice
    Parser --> Analyzer
    Analyzer --> KGWriter
    Analyzer --> Generator
    KGReader --> Router
    Generator --> GWorkspace
    Generator --> Notifier
    KGWriter --> Mapper
```

---

# Use Case 1: Phone → Framework → Google Doc

**Scenario**: Discuss a new project on the phone with Gemini, then generate a structured Google Doc with experiments, timeline, and references from personal KG.

## Data Flow

```mermaid
sequenceDiagram
    participant User as 📱 User (Phone)
    participant Gemini as Gemini Live
    participant Router as Router Agent
    participant Voice as Voice Agent
    participant KGR as KG Reader
    participant Analyzer as Analyzer
    participant Gen as Generator
    participant GW as GWorkspace Agent

    User->>Gemini: Voice discussion about new project
    Gemini->>Router: Transcript + intent (via webhook/API)
    Router->>Voice: Process transcript
    Voice->>Analyzer: Structured transcript (topics, entities, action items)
    
    Analyzer->>KGR: Query: "Find papers on [topics], methods [methods]"
    KGR->>Analyzer: Matching papers, authors, methods from Personal KG
    
    Analyzer->>Gen: Enriched context + template request ("project plan for Nature Methods")
    Gen->>Gen: Apply Jinja2 template (Nature Methods style)
    Gen->>Gen: Generate: Intro, Experiments, Datasets, Timeline, References
    
    Gen->>GW: Create Google Doc with formatted content
    GW->>GW: google-api-python-client → Docs API
    GW->>GW: Insert diagrams, tables, reference list
    GW->>User: Share link via notification
```

## LangGraph State

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph

class ProjectPlanState(TypedDict):
    # Input
    transcript: str
    intent: Literal["project_plan", "summary", "action_items"]
    template_name: str  # e.g., "nature_methods_project"
    
    # Processing
    topics: list[str]
    entities: list[dict]  # {name, type, ontology_id}
    action_items: list[str]
    
    # KG context
    related_papers: list[dict]
    related_methods: list[dict]
    
    # Output
    generated_doc: str  # Markdown
    google_doc_url: str
    messages: list  # Agent communication log
```

## Technical Stack

| Component | Tool | Notes |
|-----------|------|-------|
| Voice input | Gemini Live API → transcript | Or Whisper for local |
| Transcript → Framework | Webhook / Cloud Function | JSON payload with transcript |
| Entity extraction | LLM (Claude/Gemini) | Via LangGraph tool |
| KG query | AnyType MCP / Neo4j Cypher | Papers, methods, datasets |
| Template | Jinja2 (`nature_methods_project.j2`) | Customizable per journal style |
| Doc generation | `google-api-python-client` | Docs API v1 |
| Notification | Email / Push / Slack | Via GWorkspace Agent |

---

# Use Case 2: Laptop → Framework → Personal KG

**Scenario**: Download papers from browser → automatically parse, extract entities, store in AnyType KG with full metadata.

## Data Flow

```mermaid
sequenceDiagram
    participant User as 💻 User (Laptop)
    participant Watch as File Watcher
    participant Router as Router Agent
    participant Parser as Parser Agent
    participant Analyzer as Analyzer
    participant Mapper as Entity Mapper
    participant KGW as KG Writer
    participant AnyType as AnyType (via MCP)
    participant Drive as Google Drive

    User->>Watch: Download paper.pdf to ~/Downloads
    Watch->>Router: New PDF detected
    Router->>Parser: Parse paper.pdf
    
    Parser->>Parser: PyMuPDF: extract text, images, tables
    Parser->>Parser: PyMuPDF4LLM: generate structured Markdown
    Parser->>Parser: Extract BibTeX, DOI, authors, abstract
    Parser->>Parser: Extract figures, save as images
    Parser->>Analyzer: Structured paper content
    
    Analyzer->>Analyzer: LLM: identify key findings, methods, datasets
    Analyzer->>Mapper: Raw entities (genes, diseases, cell types, methods)
    Mapper->>Mapper: Map to ontologies (HGNC, DOID, CL, OBI)
    Mapper->>KGW: Standardized entities + relations
    
    KGW->>AnyType: Create Paper object (DOI as key)
    KGW->>AnyType: Link to Author objects
    KGW->>AnyType: Link to Method, Dataset, Gene objects
    KGW->>AnyType: Store parsed Markdown as content
    KGW->>AnyType: Attach figures as relations
    
    KGW->>Drive: Upload parsed paper + images to Google Drive
    KGW->>User: Notification: "Paper stored: [title]"
```

## AnyType Object Types

| Object Type | Properties | Relations |
|-------------|-----------|-----------|
| **Paper** | DOI, title, abstract, year, journal, bibtex | → Authors, Methods, Datasets, Genes |
| **Author** | name, ORCID, affiliation | → Papers, Institutions |
| **Method** | name, description, OBI ID | → Papers, Datasets |
| **Dataset** | name, source, accession | → Papers, Methods |
| **Gene** | symbol, HGNC ID, full name | → Papers, Diseases, Pathways |
| **Disease** | name, DOID | → Papers, Genes |
| **CellType** | name, CL ID | → Papers, Datasets |
| **ReadingNote** | content, created_date | → Paper, Tags |

## Technical Stack

| Component | Tool |
|-----------|------|
| File watching | `watchdog` (Python) |
| PDF parsing | PyMuPDF + PyMuPDF4LLM |
| Entity extraction | LLM (Claude/Gemini) + custom NER |
| Ontology mapping | bionty (Lamin) / custom lookup |
| KG storage | AnyType MCP Server |
| Large KG | Neo4j (scientific community graph) |
| File storage | Google Drive API |
| Orchestration | LangGraph |

---

# Expansion Path

## Phase 1: Unidirectional (Build → Store)
- Laptop papers → KG (Use Case 2)
- Phone transcript → Google Doc (Use Case 1)

## Phase 2: Bidirectional Context
- KG context → AI assistant (personal knowledge enrichs conversations)
- Google Drive → Framework (load any stored artifact back)

## Phase 3: Continuous Learning
- KG auto-updates when new papers cite stored ones
- Meeting notes auto-enriched with team KG context
- Task/project management via AnyType + voice commands

## Phase 4: Multi-User
- Team KG sharing (AnyType spaces)
- Collaborative paper review workflows
- Shared agent teams with role-based access

---

# Meeting Summarization Extension

Same architecture as Use Case 1, but with:
- **Input**: Gemini note-taker transcript (multiple meetings)
- **Context**: Personal/team KG provides: project context, participant roles, action item history
- **Templates**: Meeting summary, Action items, Decision log, Follow-up tasks
- **Output**: Google Doc (shared) + AnyType tasks (personal) + Calendar events (Google Calendar API)
