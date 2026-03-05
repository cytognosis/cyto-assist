# Architecture Documents

System-level designs, abstractions, and engineering blueprints.

## Documents

| # | Document | Key Abstractions | Depends On |
|---|----------|------------------|------------|
| 01 | [Modular Content Architecture](01_modular_content_architecture.md) | `ContentUnit`, `ContentAdapter`, `TemplateRegistry`, `WebFormAdapter`, Quarto integration | Research: Framework Assessment, Edge AI |
| 02 | [Orchestration Design](02_orchestration_design.md) | LangGraph agent teams, state machines, 2 use cases (phone→GDoc, laptop→KG) | Research: Framework Assessment |
| 03 | [Whiteboard Design](03_whiteboard_design.md) | Feature matrix from 7 platforms, Mermaid+Excalidraw hybrid, implementation priority | Research: Framework Assessment |

## Architectural Layers

```
┌─────────────────────────────────────────┐
│ Interface Layer (Voice, Files, Web)      │ ← 02_orchestration
├─────────────────────────────────────────┤
│ Orchestration (LangGraph Agents)         │ ← 02_orchestration
├─────────────────────────────────────────┤
│ Content Processing (Adapters, Templates) │ ← 01_modular_content
├─────────────────────────────────────────┤
│ Storage (AnyType, Neo4j, Git, GDrive)    │ ← 01_modular_content
├─────────────────────────────────────────┤
│ Visualization (Whiteboard, Diagrams)     │ ← 03_whiteboard
└─────────────────────────────────────────┘
```
