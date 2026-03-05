# Product Design Documents

Specific product designs with user-facing functionality, built on top of the architecture and research foundations.

## Documents

| # | Document | What It Replaces | Core Workflow |
|---|----------|-----------------|---------------|
| 01 | [Paper Analysis Platform](01_paper_analysis_platform.md) | Zotero, Mendeley, Papers | PDF → PyMuPDF/olmOCR → scispaCy NER → AnyType KG + Google Drive |
| 02 | [Personal Assistant](02_personal_assistant.md) | Manual task/calendar/reference management | Voice/text → LangGraph → AnyType MCP → Google Workspace sync |

## Dependencies

Both products are built on:
- **Modular Content Architecture** (`architecture/01`) for content processing
- **Orchestration Design** (`architecture/02`) for agent coordination
- **Edge AI** (`research/02`) for private, on-device processing
