# Research Documents

Component-level evaluations, benchmarks, and top-candidate selections across all domains.

## Documents

| # | Document | Focus Areas |
|---|----------|-------------|
| 01 | [Framework Assessment](01_framework_assessment.md) | Markdown, KGs, PDF, OCR, voice, diagrams, Google Workspace, orchestration, templates, slides, DOCX, images, tables, YAML/JSON — **top-3 per component** |
| 02 | [Edge AI Assessment](02_edge_ai_assessment.md) | Liquid AI LFM2 family + LEAP SDK, Google AI Edge Gallery + Gemini Nano, AI2 olmOCR + scispaCy + Tango, healthcare deployment |
| 03 | [Large-Scale Data Storage](03_large_scale_data.md) | AnnData, TileDB-SOMA, Zarr, xarray, Dask — comparison matrix for biomedical/ML workflows + PyTorch dataloaders |

## How These Feed Into Architecture

- **Framework Assessment → Modular Content Architecture**: Component choices become `ContentAdapter` implementations
- **Edge AI Assessment → Orchestration Design**: Edge model selection governs tiered deployment routing
- **Large-Scale Data → Paper Analysis Platform**: Storage choices for multi-omics and large-scale datasets
