> **Navigation**: [← Design Index](../README.md) · [Research](README.md) · [Architecture](../architecture/README.md) · [Products](../products/README.md)

# Comprehensive Framework Assessment
## Document Processing, Knowledge Management & AI Agent Ecosystem

---

# Table of Contents

1. [Markdown Ecosystem](#1-markdown-ecosystem)
2. [YAML/JSON & Data Schemas](#2-yamljson-data-schemas)
3. [OCR & Scanned Document Processing](#3-ocr-scanned-document-processing)
4. [PDF Ecosystem](#4-pdf-ecosystem)
5. [DOCX Ecosystem](#5-docx-ecosystem)
6. [Diagramming & Whiteboard](#6-diagramming-whiteboard)
7. [Image Processing](#7-image-processing)
8. [Tables](#8-tables)
9. [Slides & Presentations](#9-slides-presentations)
10. [Google Workspace Integration](#10-google-workspace-integration)
11. [Template Engines](#11-template-engines)

---

# 1. Markdown Ecosystem

Markdown is our **canonical format** for LLM/agent workflows, git-tracked knowledge, and content storage.

## Top-3 Tools

| Rank | Tool | Role | License | Key Strengths |
|------|------|------|---------|---------------|
| 🥇 | **MarkItDown** (Microsoft) | Conversion TO Markdown | MIT | 20+ input formats, LLM-optimized, preserves structure, Python-native |
| 🥈 | **Pandoc** (via `pypandoc`) | Bidirectional conversion | GPL | De facto standard, 40+ formats, highest fidelity, LaTeX/PDF support |
| 🥉 | **markdown-it-py** | Parsing/AST manipulation | MIT | 100% CommonMark, plugin system, AST access, basis for mdformat |

## Supporting Tools

| Tool | Role | Notes |
|------|------|-------|
| `mdformat` | Formatting/linting | CommonMark-compliant, plugin-extensible, CI/CD ready |
| `Python-Markdown` | MD→HTML rendering | Extension-rich, widely used |
| `mistune` | Fast parsing | Single-file, extensible, good for lightweight needs |
| `remark` (JS) | AST processing | JS ecosystem; use `markdown-it-py` as Python equivalent |

## Recommendation

- **Ingest pipeline**: MarkItDown for converting any document → Markdown
- **Rich conversion (MD→PDF/DOCX/HTML)**: Pandoc via `pypandoc`
- **AST manipulation/validation**: `markdown-it-py` + `mdformat` for consistency
- **Storage**: Plain Markdown files in git repos, with frontmatter (YAML) for metadata

---

# 2. YAML/JSON & Data Schemas

| Rank | Tool | Role | Key Strengths |
|------|------|------|---------------|
| 🥇 | **Pydantic v2** | Schema validation, serialization | Python standard for data validation, JSON Schema export, Settings management |
| 🥈 | **ruamel.yaml** | YAML parsing (preserves comments) | Round-trip YAML, preserves formatting/comments, superior to PyYAML |
| 🥉 | **orjson** / `msgspec` | High-performance JSON | 10x faster than `json`, good for high-throughput data pipelines |

### Integration with Templating

- Pydantic models define data schemas → Jinja2 templates consume them → output in any format
- YAML frontmatter in Markdown files (parsed by `ruamel.yaml`) for metadata
- JSON Schema exported from Pydantic for API contracts, MCP tool definitions

---

# 3. OCR & Scanned Document Processing

## Comprehensive Tesseract Assessment

### Strengths ✅
- Battle-tested, Google-backed, 100+ languages
- Excellent for clean, machine-printed text
- Custom training for domain-specific vocabularies
- Zero cost, no API dependencies
- Integrated into PyMuPDF for in-library OCR

### Weaknesses ❌
- **Complex layouts**: Struggles with multi-column, tables, mixed formatting
- **Handwritten text**: Poor performance
- **Heavy preprocessing needed**: Requires image cleanup for optimal accuracy
- **Speed**: Slower on large volumes vs. deep-learning approaches
- **No structural understanding**: Treats pages as flat text

### Complementary Tools

| Tool | Best For | Complements Tesseract? |
|------|----------|----------------------|
| **PaddleOCR** | Multi-language, complex layouts, speed (GPU) | ✅ Better layout analysis, structured JSON output, table detection |
| **docTR** (Mindee) | Document understanding (receipts, forms) | ✅ Two-stage detection+recognition, PyTorch-native |
| **Surya OCR** | Layout analysis + text extraction | ✅ Specifically designed for document structure |
| **EasyOCR** | Quick extraction, simple API | ⚠️ Similar tier to Tesseract, less complex layout support |

### VLM-Based OCR (Next Generation)

| Model | Key Advantage | Status |
|-------|--------------|--------|
| **DeepSeek-OCR** | Long documents, token compression | Open-source, efficient |
| **PaddleOCR-VL** | Best technical performance in benchmarks | Open-source |
| **Nanonets OCR 2** | High accuracy, structured output | Commercial with free tier |
| **olmOCR-2** | End-to-end document understanding | Open-source |
| **dots.OCR** | Best throughput + accuracy balance | Open-source |

## Recommendation

- **Primary (local/embedded)**: Tesseract via PyMuPDF for simple pages + PaddleOCR for complex layouts
- **Advanced**: Surya OCR for layout analysis, docTR for forms
- **Future**: VLM-based models (DeepSeek-OCR, PaddleOCR-VL) as they mature for edge deployment

---

# 4. PDF Ecosystem

## PyMuPDF Comprehensive Assessment

### Base PyMuPDF (AGPL, Free)

| Feature | Support | Quality |
|---------|---------|---------|
| Text extraction | ✅ | Good for simple layouts |
| Table detection/extraction | ✅ (v1.23+) | Good, exports to DataFrames/MD |
| Image extraction | ✅ | Excellent |
| Vector graphics extraction | ✅ | Good ("line art") |
| Annotation read/write | ✅ | Comprehensive (all types) |
| Multi-column detection | ✅ | Basic |
| Rendering | ✅ | High quality |
| OCR integration (Tesseract) | ✅ | Via built-in API |
| Format support | PDF + images | Core formats |

### PyMuPDF4LLM (Free)

| Feature | Notes |
|---------|-------|
| Markdown output optimized for LLMs | Structured headers, tables in MD format |
| Table extraction as MD | Improved over base |
| Image descriptions | Via LLM integration |
| Chunking for RAG | Built-in page/section chunking |

### PyMuPDF Pro + Layout (Paid, contact Artifex for pricing)

| Feature | Free Alternative? | Performance Gap |
|---------|------------------|----------------|
| **Office file support** (DOCX/PPTX/XLSX) | `python-docx`, `python-pptx`, `openpyxl` | ⚠️ Moderate: individual libs match for most features |
| **Advanced layout analysis** (10x faster, no GPU) | Surya OCR, PaddleOCR layout | ⚠️ Moderate: open-source achieves comparable results with more setup |
| **Multi-column reading order** | Custom implementation with PaddleOCR layout | ⚠️ Moderate gap |
| **Semantic document understanding** | VLM-based OCR models | ✅ Open-source VLMs competitive |
| **Commercial license** | N/A | Required for non-AGPL projects |

> **Pricing**: Not publicly listed. Contact Artifex. Believed to be annual seat-based license. The service is **local processing only** (no API/cloud calls), meaning no hidden LLM costs.

### Recommended Free Stack Matching Pro Features

| Pro Feature | Free Replacement |
|-------------|-----------------|
| Office parsing | `python-docx` + `python-pptx` + `openpyxl` |
| Layout analysis | PaddleOCR PP-Structure / Surya OCR |
| LLM-ready output | PyMuPDF4LLM (free) + custom post-processing |
| Multi-column | PaddleOCR layout detection → reorder text blocks |
| Table formatting | `camelot-py` / `tabula-py` for complex tables |

## PDF Annotation Standards

### How Annotations Work
- Annotations are **overlay objects** on page content (not inline text modifications)
- Stored as PDF objects with coordinates, type, content, color, author, date
- Can be **flattened** (merged into visual layer) or kept **editable**

### Annotation Types (ISO 32000 PDF Standard)
- **Markup**: Highlight, Underline, StrikeOut, Squiggly, Sticky Notes, FreeText, Ink
- **Shapes**: Square, Circle, Line, Polygon, PolyLine
- **Non-markup**: Links, Sound, File Attachment, Stamp

### Cross-Application Compatibility

| Reader/Manager | Reads Standard Annotations? | Creates Standard Annotations? | Interop Quality |
|---------------|---------------------------|-------------------------------|----------------|
| Adobe Acrobat | ✅ Full | ✅ Full | 🟢 Reference implementation |
| Zotero | ✅ Imports external | ✅ Own format (needs export) | 🟡 Export step needed |
| Mendeley | ✅ Basic | ⚠️ Proprietary storage | 🟡 Limited interop |
| Paperpile (MetaPDF) | ✅ Good | ✅ Embedded in PDF | 🟢 Good standard compliance |
| ReadCube Papers | ✅ Good | ⚠️ Ecosystem-specific | 🟡 Migration challenges |
| Preview (macOS) | ✅ Good | ✅ Standard | 🟢 Good |
| Xodo | ✅ Full | ✅ Full | 🟢 Excellent |

> **Key finding**: No universal editable annotation standard across reference managers. Paperpile (MetaPDF) has best standard compliance. PyMuPDF is the best programmatic tool for reading/writing annotations.

### Python Libraries for Annotations

| Library | Read | Write | Best For |
|---------|------|-------|----------|
| **PyMuPDF** | ✅ All types | ✅ All types | Primary choice — fastest, most complete |
| **pypdf** | ✅ Good | ✅ Highlights | Lightweight alternative |
| **PDFPlumber** | ✅ Good | ❌ | Read-only extraction |
| `txtmarker` | ❌ | ✅ Highlights | Programmatic highlighting with QA |

### Cross-Format Annotation Standard
- **W3C Web Annotation Model**: JSON-LD based, format-agnostic, supports any document type
- **Hypothesis**: Open annotation platform using W3C standard → works on web, PDFs, EPUB
- **IIIF (International Image Interoperability Framework)**: For image/manuscript annotations
- 🔑 **Best bet for cross-format**: Build on W3C Web Annotation Data Model with custom renderers per format

---

# 5. DOCX Ecosystem

| Rank | Tool | Role | Key Strengths |
|------|------|------|---------------|
| 🥇 | **python-docx** | Create/read/modify DOCX | Comprehensive formatting, styles, images, tables; comments (v1.2+) |
| 🥈 | **docxtpl** | Template-based DOCX generation | Jinja2 templates IN Word docs, rich text, loops, conditionals |
| 🥉 | **Pandoc** | Format conversion | DOCX↔MD↔HTML↔PDF with highest fidelity |

### Feature Matrix

| Feature | python-docx | docxtpl | Pandoc |
|---------|------------|---------|--------|
| Create from scratch | ✅ | ❌ (template only) | ✅ |
| Template-based generation | ⚠️ Manual | ✅ Jinja2 native | ⚠️ Basic |
| Parse/extract text | ✅ | ⚠️ Limited | ✅ |
| Comments | ✅ (v1.2+) | ❌ | ⚠️ |
| Tracked changes | ❌ (use `docx-revisions`) | ❌ | ❌ |
| Tables | ✅ | ✅ | ✅ |
| Images | ✅ | ✅ (inline) | ✅ |
| Styles/formatting | ✅ Full | ✅ Via template | ✅ Via reference doc |

---

# 6. Diagramming & Whiteboard

## Diagramming Tools Comparison

| Feature | **Mermaid** | **Excalidraw** | **draw.io** |
|---------|-----------|--------------|-----------|
| **Paradigm** | Text-based (code) | Visual (hand-drawn) | Visual (structured) |
| **License** | MIT | MIT | Apache 2.0 |
| **Version control** | 🟢 Perfect (text) | 🟡 JSON-based | 🟡 XML-based |
| **Diagram types** | 24+ (flowchart, sequence, ER, Gantt, etc.) | Free-form | Extensive libraries |
| **AI generation** | ✅ From text/images | ⚠️ Limited | ✅ From screenshots/Mermaid |
| **Export formats** | SVG, PNG, PDF | SVG, PNG | SVG, PNG, JPEG, PDF, Visio |
| **Import from others** | ✅ convert2mermaid (Visio, draw.io, Excalidraw) | ✅ Mermaid paste | ✅ Visio, Gliffy, Mermaid |
| **LLM-friendly** | 🟢 Best (text input/output) | 🟡 JSON scene | 🟡 XML |
| **Whiteboard mode** | ✅ Mermaid Whiteboard (paid) | ✅ Native | ✅ Board mode |
| **VS Code plugin** | ✅ Excellent | ✅ Extension | ✅ Extension |
| **Embeddable** | ✅ In Markdown | ✅ React component | ✅ Iframe/React |
| **Collaboration** | Via Mermaid Whiteboard | ✅ Real-time, E2E encrypted | ✅ Real-time |

### Conversion Tools

| From → To | Tool |
|-----------|------|
| Mermaid → SVG/PNG/PDF | `mermaid-cli` (`mmdc`) |
| Image → Mermaid | Mermaid AI (image recognition) |
| Visio/draw.io/Excalidraw → Mermaid | `convert2mermaid` CLI |
| Mermaid → Excalidraw | Excalidraw native paste |
| Any → draw.io | draw.io AI import |
| Excalidraw → draw.io/Gliffy | Community converters |

### Our Standard: **Mermaid as source of truth**
- Text-based = version-controlled, LLM-native, diff-friendly
- Render to visual formats (SVG/PNG) for documents
- Use Excalidraw for quick brainstorming, export to Mermaid for persistence
- Use draw.io for complex structured diagrams when Mermaid lacks features

---

# 7. Image Processing

## Tool Stack

| Category | Tool | Role |
|----------|------|------|
| **Core manipulation** | `Pillow` (PIL) | Resize, crop, rotate, format conversion, basic filters |
| **SVG handling** | `CairoSVG` | SVG → PNG/PDF rasterization |
| **SVG parsing** | `svgpathtools`, `lxml` | Parse SVG elements programmatically |
| **Background removal** | `rembg` | AI-powered background removal (U2-Net) |
| **Upscaling** | `Real-ESRGAN` | AI super-resolution (4x), artifact removal |
| **Quality assessment** | `pyiqa` | No-reference image quality metrics |
| **Vector → Bitmap** | `CairoSVG` + `Pillow` | SVG → PNG at target resolution |
| **OCR on images** | Tesseract / PaddleOCR | Text extraction from images |
| **Semantic understanding** | VLM models (GPT-4V, Gemini Vision) | Image description, diagram understanding |

### Structured Image Analysis Pipeline
1. **Detect type**: Diagram vs photo vs chart → route to appropriate analyzer
2. **Diagrams**: Parse with SVG tools → extract text → validate with OCR → convert to Mermaid
3. **Charts/plots**: Extract data with VLM → validate text/labels with OCR → assess readability
4. **Photos**: Quality assessment (`pyiqa`) → upscale if needed (Real-ESRGAN) → semantic description (VLM)

---

# 8. Tables

## Small/Medium Tables (Papers, Reports)

| Rank | Format/Tool | Best For | Inline Rendering | Template Support |
|------|-------------|----------|-----------------|-----------------|
| 🥇 | **Markdown tables** + extensions | In-document, version-controlled | ✅ In MD renderers | ✅ Via Jinja2 |
| 🥈 | **openpyxl** (XLSX) | Rich formatting, formulas | ❌ (external viewer) | ⚠️ Manual |
| 🥉 | **tabulate** / `rich` | Terminal/console display | ✅ Terminal | ⚠️ |

### Supporting Tools
- `pandas` → table manipulation, CSV/XLSX I/O
- `camelot-py` → extract tables from PDFs
- `tabula-py` → Java-based PDF table extraction
- `great_tables` → publication-ready table rendering (Python)
- LaTeX formulas in tables → `KaTeX` / `MathJax` for rendering

## Large-Scale Data Storage

> See dedicated document: `large_scale_data.md`

---

# 9. Slides & Presentations

| Rank | Tool | Role | Key Strengths |
|------|------|------|---------------|
| 🥇 | **python-pptx** | Create/modify PPTX | Full programmatic control, templates, no Office needed |
| 🥈 | **Google Slides API** | Cloud-native slides | Programmatic CRUD, template placeholders, Sheets integration |
| 🥉 | **Canva Connect API** | Design-centric | Brand kits, design templates, requires Teams/Enterprise tier |

### Branding/Style Guide Storage

| Approach | Tool | Format |
|----------|------|--------|
| **Brand kit** | Canva Brand Kit / custom YAML | Colors (hex), fonts (Google Fonts), logos (SVG/PNG) |
| **PPTX template** | python-pptx slide masters | .pptx with defined masters/layouts |
| **Google Slides theme** | Slides API theme manipulation | Theme ID + JSON config |
| **CSS variables** | Custom | CSS custom properties → consumed by all renderers |

### Cross-Platform Fixes (PPTX compatibility)
- **Missing fonts**: Embed fonts OR use Google Fonts (universally available)
- **Layout shifts**: Use python-pptx to normalize dimensions, anchor positions
- **Color profiles**: Convert to sRGB for consistency

---

# 10. Google Workspace Integration

## Core Libraries

| Service | Library | Auth |
|---------|---------|------|
| **All Google APIs** | `google-api-python-client` | OAuth 2.0 / Service Account |
| **Google Sheets** | `gspread` (wrapper) | OAuth 2.0 / Service Account |
| **Authentication** | `google-auth-oauthlib` | OAuth 2.0 flow |
| **Drive** | Drive API v3 | OAuth 2.0 |
| **Docs** | Docs API v1 | OAuth 2.0 |
| **Slides** | Slides API v1 | OAuth 2.0 |

## Bidirectional Sync Architecture

```
Our Framework ←→ Google Workspace Adapter ←→ Google APIs
                        ↕
              Auth Manager (OAuth 2.0)
              - Company service account
              - Personal user tokens
              - Token refresh
```

### Capabilities by Service

| Service | Read | Write | Real-time Sync |
|---------|------|-------|---------------|
| **Drive** | ✅ List, download, metadata | ✅ Upload, create, update | ⚠️ Via Changes API (polling) |
| **Docs** | ✅ Full document content | ✅ Create, insert, replace | ⚠️ Batch updates |
| **Sheets** | ✅ Cell data, formulas | ✅ CRUD operations | ⚠️ Via push notifications |
| **Slides** | ✅ Slide content, notes | ✅ Create, update, replace elements | ⚠️ Batch updates |

### Authentication Strategy
- **Service account**: For automated agents/pipelines (no user interaction)
- **OAuth 2.0 flow**: For personal accounts (one-time consent, token stored securely)
- **Domain-wide delegation**: For company-wide access via admin consent

---

# 11. Template Engines

| Rank | Engine | Language | Key Strengths | Best For |
|------|--------|----------|---------------|----------|
| 🥇 | **Jinja2** | Python | Flexible, template inheritance, custom filters, autoescaping | Cross-format document generation |
| 🥈 | **docxtpl** | Python (Jinja2 + python-docx) | Jinja2 tags IN Word templates | DOCX template generation |
| 🥉 | **Mako** | Python | Fastest, full Python in templates | Performance-critical rendering |

### Cross-Format Template Strategy

```
Jinja2 Template (universal)
     ↓
Markdown output → Pandoc → PDF / DOCX / HTML / LaTeX
     ↓
docxtpl → branded DOCX (with Word template)
     ↓
python-pptx → branded PPTX (with slide template)
     ↓
Google Slides API → branded Google Slides
```

---

# Existing Skills Gap Analysis

## Skills to Revise

| Current Skill | What to Add/Change |
|--------------|-------------------|
| `markdown-mermaid-writing` | Add MarkItDown integration, mdformat, cross-format conversion via Pandoc |
| `document-skills/pdf` | Add PyMuPDF4LLM, annotation extraction/creation, VLM-based OCR options |
| `document-skills/docx` | Add docxtpl for template generation, tracked changes via docx-revisions |
| `document-skills/xlsx` | Add great_tables, camelot-py, large-scale data pointer |
| `document-skills/pptx` | Add Google Slides API, Canva API, branding/style guide integration |
| `markitdown` | Update to latest version, add streaming, plugin system documentation |

## New Skills Needed

| New Skill | Purpose |
|-----------|---------|
| `knowledge-graph` | Neo4j + GraphRAG + vector store integration |
| `ocr-pipeline` | Multi-engine OCR routing (Tesseract→PaddleOCR→VLM) |
| `google-workspace` | Drive/Docs/Sheets/Slides bidirectional sync |
| `diagramming` | Consolidated Mermaid + Excalidraw + draw.io + conversions |
| `whiteboard` | Whiteboard feature set and implementation guide |
| `image-processing` | Pillow + rembg + CairoSVG + Real-ESRGAN pipeline |
| `template-engine` | Jinja2 cross-format generation system |
| `multi-agent-orchestration` | LangGraph patterns and best practices |
| `paper-analysis` | Automated paper parsing → KG storage pipeline |
| `personal-assistant` | Voice → framework → output pipeline |
| `large-scale-data` | TileDB-SOMA/Zarr/xarray/Dask for biomedical ML |
