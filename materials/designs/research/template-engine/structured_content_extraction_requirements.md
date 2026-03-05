# Structured Content Extraction — Standards & Requirements

> **Version:** 1.0 | **Date:** 2026-03-02 | **Status:** Draft

---

## 1. Purpose

This document defines the requirements for a **structured content extraction system** that can parse scientific papers, technical reports, and online application forms across multiple input formats and extract their content into the Quarto/YAML template engine format defined in our [`template_schema_specification.md`](file:///home/mohammadi/repos/cytognosis/agents/standards/template_schema_specification.md).

The system supports two modes:
1. **Template → Content** (forward): Given a document + template, extract structured content into `content.yml`
2. **Document → Template** (reverse): Given a document + content description config, generate a `_template.yml` schema

---

## 2. Requirements Classification

| Tier | Label | Weight | Meaning |
|------|-------|--------|---------|
| **R** | Required | ×3 | Disqualified without this |
| **SP** | Strongly Preferred | ×2 | Significant penalty for absence |
| **P** | Preferred | ×1 | Positive differentiator |

---

## 3. Input Format Requirements

### 3.1 Format Support

| ID | Tier | Requirement |
|----|:----:|-------------|
| **F-1** | **R** | **PDF** — Extract text, sections, figures, tables from rendered (text-based) PDF documents. |
| **F-2** | **SP** | **DOCX** — Extract from Microsoft Word and Google Docs exported files. |
| **F-3** | **SP** | **LaTeX/BibTeX** — Parse `.tex` source and `.bib` bibliography files, including Overleaf projects. |
| **F-4** | **SP** | **HTML** — Extract from online journal pages (Nature, Science, PubMed, etc.) with structured DOM parsing. |
| **F-5** | **P** | **Markdown** — Parse structured Markdown documents (headers, sections, frontmatter). |
| **F-6** | **P** | **Google Docs** — Direct API access without export, via Google Docs API or MCP. |

### 3.2 Pre-Processing

| ID | Tier | Requirement |
|----|:----:|-------------|
| **F-7** | **P** | **OCR** — For scanned/image-based PDFs, chain a best-in-class OCR tool prior to extraction (not the primary tool itself). |

---

## 4. Web/Interactive Extraction Requirements

| ID | Tier | Requirement |
|----|:----:|-------------|
| **W-1** | **SP** | **Static HTML scraping** — Extract structured content from publisher websites with standard DOM parsing (CSS selectors, XPath). |
| **W-2** | **SP** | **Dynamic/JS-rendered pages** — Handle SPA/JS-heavy publisher sites via headless browser (Playwright, Puppeteer). |
| **W-3** | **P** | **Interactive form scraping** — Click through form elements (dropdowns, radio buttons) to reveal conditional fields, as done for QB3 mentoring. |
| **W-4** | **P** | **Conditional/branching forms** — Handle forms where selected choices change subsequent visible fields (e.g., Effective Altruism multi-program applications). |

---

## 5. Extracted Content Requirements (Scientific Papers)

### 5.1 Metadata & Identifiers

| ID | Tier | Requirement |
|----|:----:|-------------|
| **E-1** | **R** | **DOI** — Extract or resolve DOI from the paper. If not present, query CrossRef/PubMed APIs. |
| **E-2** | **SP** | **PubMed ID (PMID)** — Extract or resolve via PubMed API for bio/med papers. |
| **E-3** | **R** | **Full citation details** — Authors, title, journal/conference, volume, issue, pages, year, publisher. Store as BibTeX entry. |
| **E-4** | **SP** | **Author roles** — Identify first author(s), senior/last author(s), and co-first/co-senior annotations (e.g., "these authors contributed equally"). |
| **E-5** | **P** | **Author contributions** — Extract dedicated author contribution section if present. |
| **E-6** | **P** | **Author affiliations & correspondence** — Extract institutional affiliations and corresponding author email(s). |

### 5.2 Content Structure

| ID | Tier | Requirement |
|----|:----:|-------------|
| **E-7** | **R** | **Abstract** — Extract full abstract text. |
| **E-8** | **R** | **Section names & full text** — Extract every named section (Introduction, Methods, Results, Discussion, etc.) with full text as separate content blocks. |
| **E-9** | **SP** | **Figures** — Export individual figures/images in their original quality with captions and labels. |
| **E-10** | **SP** | **Tables** — Export individual tables in structured format (CSV/TSV) with captions. |
| **E-11** | **P** | **Equations** — Extract mathematical equations in LaTeX notation. |

### 5.3 References & Associated Materials

| ID | Tier | Requirement |
|----|:----:|-------------|
| **E-12** | **R** | **References/citations** — Extract all citations and export as a complete `.bib` (BibTeX) file with harmonized entries. |
| **E-13** | **SP** | **Code availability** — Extract links to associated code repositories (GitHub, GitLab, Zenodo, etc.). |
| **E-14** | **SP** | **Data availability** — Extract links to deposited datasets (GEO, CellxGene, NIH NDA, etc.) with accession numbers. |
| **E-15** | **P** | **Supplementary materials** — Download index of supplements and individual supplementary documents/files. |

---

## 6. Template Engine Integration Requirements

| ID | Tier | Requirement |
|----|:----:|-------------|
| **T-1** | **R** | **Content export** — Output extracted content as `content.yml` conforming to our `_template.yml` schema format. |
| **T-2** | **SP** | **Template generation** (reverse mode) — Given a document and a content description config, generate a `_template.yml` describing the document's structure. |
| **T-3** | **P** | **Template matching** — Given a document and a template, validate that the document's structure matches the template and report gaps. |
| **T-4** | **P** | **Batch extraction** — Process multiple documents against the same template in a single run. |

---

## 7. Tooling & Integration Requirements

| ID | Tier | Requirement |
|----|:----:|-------------|
| **I-1** | **SP** | Tools/libraries **should be open-source** (OSI-approved license). |
| **I-2** | **P** | Tools should be **Python-based** or have Python bindings for integration with our toolchain. |
| **I-3** | **P** | Should support **reproducible, scriptable workflows** (CLI and/or Python API). |
| **I-4** | **P** | Should integrate with **agentic AI workflows** (MCP servers, LLM-callable APIs). |

---

## 8. Tool Landscape Analysis

### 8.1 PDF Extraction

| Tool | GitHub ★ | License | Key Capabilities | Limitations |
|------|:--------:|---------|-------------------|-------------|
| **[GROBID](https://github.com/kermitt2/grobid)** | ~10k | Apache-2.0 | ML-based scholarly PDF parsing: header metadata, sections, figures, tables, references. CRF + deep learning models. REST API. The gold standard for scientific PDF extraction. | Java-based (needs Docker or JVM); focuses on scholarly papers only |
| **[PyMuPDF (fitz)](https://github.com/pymupdf/PyMuPDF)** | ~5.5k | AGPL-3.0 | Fast PDF text/image extraction, page-level layout analysis, table detection, annotations. Python-native. | No ML-based section understanding; low-level |
| **[pdfplumber](https://github.com/jsvine/pdfplumber)** | ~7k | MIT | Table extraction, visual debugging, character-level text extraction. Built on pdfminer.six. | No section/metadata understanding |
| **[Marker](https://github.com/VikParuchuri/marker)** | ~20k | GPL-3.0 | Converts PDF → Markdown with high fidelity using ML (surya OCR + layout detection). Handles equations, figures, tables. | ML-heavy (GPU recommended); converts but doesn't structure |
| **[Docling](https://github.com/DS4SD/docling)** | ~16k | MIT | IBM's document understanding: PDF, DOCX, HTML, images. Exports to Markdown/JSON. Layout analysis, table structure, OCR. | Newer project; may need validation |
| **[ScienceBeam](https://github.com/elifesciences/sciencebeam)** | ~500 | MIT | eLife's tool for structured extraction from scholarly PDFs (built on GROBID). | Smaller community |
| **[CERMINE](https://github.com/CeON/CERMINE)** | ~500 | AGPL-3.0 | Content extraction and mining from scientific articles. | Java-based; less maintained |
| **[paperetl](https://github.com/neuml/paperetl)** | ~1k | Apache-2.0 | ETL pipeline for scientific papers: PDF → structured data, GROBID integration. | Thin wrapper |

> [!IMPORTANT]
> **Top pick for PDF:** **GROBID** (gold standard for scholarly papers) + **Docling** (broader format support, MIT license) + **PyMuPDF** (for low-level operations)

### 8.2 DOCX Extraction

| Tool | GitHub ★ | License | Key Capabilities | Limitations |
|------|:--------:|---------|-------------------|-------------|
| **[python-docx](https://github.com/python-openxml/python-docx)** | ~5k | MIT | Full DOCX reading/writing: paragraphs, tables, images, styles, headers. Python standard. | No Google Docs API integration |
| **[docx2python](https://github.com/ShayHill/docx2python)** | ~500 | MIT | Extracts text, images, tables with nesting structure. Simpler API than python-docx. | Less granular control |
| **[Pandoc](https://pandoc.org)** | ~42k | GPL-2.0 | DOCX → Markdown/JSON AST conversion. Preserves structure. | External binary dependency |
| **[Docling](https://github.com/DS4SD/docling)** | ~16k | MIT | Also handles DOCX extraction with layout understanding. | See above |

### 8.3 Google Docs Direct Access

| Tool | License | Key Capabilities | Limitations |
|------|---------|-------------------|-------------|
| **[Google Docs API](https://developers.google.com/docs/api)** | Proprietary API | Full read/write access to Google Docs structure (paragraphs, tables, images, styles). | Requires OAuth; API quotas |
| **[gdown](https://github.com/wkentaro/gdown)** | MIT | Download Google Drive files by URL. | Download-only, no structure |
| **[google-docs-mcp](https://github.com/AeroHand/google-docs-mcp)** | MIT | MCP server for Google Docs CRUD operations. | Early-stage |

### 8.4 LaTeX/BibTeX Parsing

| Tool | GitHub ★ | License | Key Capabilities | Limitations |
|------|:--------:|---------|-------------------|-------------|
| **[TexSoup](https://github.com/alvinwan/TexSoup)** | ~500 | BSD-2 | Parse LaTeX into navigable tree (BeautifulSoup-like API). Extract sections, commands, environments. | Not a full LaTeX compiler; edge cases |
| **[pylatexenc](https://github.com/phfaist/pylatexenc)** | ~300 | MIT | LaTeX → Unicode text conversion, LaTeX tokenizer. | Conversion-focused, not structure |
| **[bibtexparser](https://github.com/sciunto-org/python-bibtexparser)** | ~700 | MIT | Full BibTeX parser: entries, fields, customization. Widely used. | BibTeX only |
| **[Pandoc](https://pandoc.org)** | ~42k | GPL-2.0 | LaTeX → Markdown/JSON AST. CiteProc for citation processing. | Needs full LaTeX tree for complex docs |
| **[LaTeXML](https://github.com/brucemiller/LaTeXML)** | ~1k | Public Domain | LaTeX → XML/HTML with full semantic preservation. arXiv uses it. | Perl-based; heavy |

> [!IMPORTANT]
> **Top pick for LaTeX:** **TexSoup** (section/structure extraction) + **bibtexparser** (bibliography) + **Pandoc** (format conversion)

### 8.5 HTML / Web Scraping

| Tool | GitHub ★ | License | Key Capabilities | Limitations |
|------|:--------:|---------|-------------------|-------------|
| **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** | ~(pip)~ | MIT | HTML/XML parsing with CSS selectors. Python standard for web scraping. | Static HTML only |
| **[Playwright](https://github.com/microsoft/playwright-python)** | ~12k | Apache-2.0 | Headless browser automation. Handles JS rendering, clicks, form interaction. | Heavier than static parsing |
| **[Scrapy](https://github.com/scrapy/scrapy)** | ~55k | BSD-3 | Full web scraping framework with spiders, pipelines, middleware. | Complex for simple tasks |
| **[trafilatura](https://github.com/adbar/trafilatura)** | ~3.5k | Apache-2.0 | Web content extraction optimized for text. Handles boilerplate removal, metadata, date parsing. | Not scholarly-specific |
| **[newspaper3k](https://github.com/codelucas/newspaper)** | ~14k | MIT | Article extraction from news/web. NLP-based. | Not designed for papers |
| **[lxml](https://github.com/lxml/lxml)** | ~2.5k | BSD-3 | Fast XML/HTML parsing with XPath. C-extension performance. | Lower-level API |

> [!IMPORTANT]
> **Top pick for HTML:** **BeautifulSoup4** (static parsing) + **Playwright** (JS rendering + form interaction) + **trafilatura** (content extraction)

### 8.6 Citation/Metadata Resolution

| Tool | License | Key Capabilities |
|------|---------|-------------------|
| **[CrossRef API](https://www.crossref.org/documentation/retrieve-metadata/)** | Free | DOI resolution → full metadata (JSON). No auth required. |
| **[PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/)** | Free | PMID lookup, DOI→PMID, full citation metadata. |
| **[Semantic Scholar API](https://api.semanticscholar.org/)** | Free | Paper search, citation graphs, author info. |
| **[habanero](https://github.com/sckott/habanero)** (Python) | MIT | Python client for CrossRef API. |
| **[biopython (Entrez)](https://biopython.org)** | BSD-3 | PubMed/Entrez API client for Python. |
| **[doi2bib](https://github.com/davidagraf/doi2bib)** | MIT | DOI → BibTeX conversion web service/API. |

### 8.7 Figure/Table Extraction

| Tool | GitHub ★ | License | Key Capabilities |
|------|:--------:|---------|-------------------|
| **[PyMuPDF](https://github.com/pymupdf/PyMuPDF)** | ~5.5k | AGPL-3.0 | Extract embedded images from PDF pages. |
| **[camelot](https://github.com/camelot-dev/camelot)** | ~3k | MIT | Table extraction from PDFs → pandas DataFrames → CSV. |
| **[tabula-py](https://github.com/chezou/tabula-py)** | ~2.2k | MIT | Wrapper for Tabula (Java) — PDF table extraction. |
| **[img2table](https://github.com/xavctn/img2table)** | ~600 | MIT | Table detection from images and PDFs. |
| **[pdffigures2](https://github.com/allenai/pdffigures2)** | ~500 | Apache-2.0 | Allen AI's tool for extracting figures/tables from scholarly PDFs. |
| **[Docling](https://github.com/DS4SD/docling)** | ~16k | MIT | Integrated figure and table extraction with layout analysis. |

### 8.8 OCR (Pre-Processing for Image-Based PDFs)

| Tool | GitHub ★ | License | Key Capabilities |
|------|:--------:|---------|-------------------|
| **[Tesseract](https://github.com/tesseract-ocr/tesseract)** | ~65k | Apache-2.0 | Industry-standard OCR engine. 100+ languages. |
| **[surya](https://github.com/VikParuchuri/surya)** | ~15k | GPL-3.0 | ML-based OCR + layout analysis + table recognition. Multilingual. |
| **[EasyOCR](https://github.com/JaidedAI/EasyOCR)** | ~25k | Apache-2.0 | Deep learning OCR. 80+ languages. Simple API. |
| **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** | ~48k | Apache-2.0 | State-of-the-art OCR with layout analysis. |

> [!TIP]
> **OCR recommendation:** **Tesseract** (CPU, universal) or **surya** (GPU, modern ML, used by Marker)

---

## 9. Recommended Tool Stack

### Primary Stack

| Function | Primary Tool | Backup/Complement |
|----------|-------------|-------------------|
| **PDF (scholarly)** | GROBID | Docling, PyMuPDF |
| **PDF (general)** | Docling | Marker (PDF→Markdown) |
| **DOCX** | python-docx | Pandoc (DOCX→Markdown) |
| **LaTeX** | TexSoup + Pandoc | pylatexenc |
| **BibTeX** | bibtexparser | Pandoc CiteProc |
| **HTML (static)** | BeautifulSoup4 + trafilatura | lxml |
| **HTML (dynamic)** | Playwright | Browser agent |
| **Interactive forms** | Playwright + browser agent | — |
| **DOI resolution** | habanero (CrossRef) | doi2bib |
| **PubMed lookup** | biopython (Entrez) | PubMed E-utilities |
| **Figures** | PyMuPDF + pdffigures2 | Docling |
| **Tables** | camelot + Docling | tabula-py |
| **OCR (if needed)** | Tesseract + surya | EasyOCR |
| **Google Docs** | Google Docs API | gdown + python-docx |

### Architecture

```
Input Document (PDF/DOCX/LaTeX/HTML/Markdown)
       │
       ├── Format Detection
       │
       ├── Format-Specific Parser
       │     ├── PDF → GROBID / Docling
       │     ├── DOCX → python-docx
       │     ├── LaTeX → TexSoup + bibtexparser
       │     ├── HTML → Playwright + BeautifulSoup
       │     └── Markdown → Python markdown/frontmatter
       │
       ├── Unified Intermediate Representation
       │     (section tree + metadata + content blocks)
       │
       ├── Template Matching / Generation
       │     ├── Forward: doc + _template.yml → content.yml
       │     └── Reverse: doc + config → _template.yml
       │
       ├── Post-Processing
       │     ├── Citation resolution (CrossRef / PubMed)
       │     ├── Figure export (PyMuPDF)
       │     ├── Table export (camelot → CSV)
       │     └── BibTeX harmonization (bibtexparser)
       │
       └── Output
             ├── content.yml (structured content)
             ├── _template.yml (if reverse mode)
             ├── figures/ (exported images)
             ├── tables/ (exported CSVs)
             ├── references.bib (harmonized)
             └── supplements/ (downloaded materials)
```

---

## 10. Feasibility Assessment

### Immediately Feasible (implement now)

| Capability | Tools | Notes |
|------------|-------|-------|
| PDF metadata + sections + abstract | GROBID, Docling | Mature, well-tested |
| DOCX parsing | python-docx, Pandoc | Standard |
| LaTeX/BibTeX parsing | TexSoup, bibtexparser | Straightforward |
| HTML static scraping | BeautifulSoup4, trafilatura | Mature |
| HTML dynamic/forms | Playwright, browser agent | Already used for QB3 |
| DOI/PMID resolution | habanero, biopython | API-based, simple |
| Figure & table extraction | PyMuPDF, camelot | Established tools |
| BibTeX harmonization | bibtexparser + CrossRef | Standard workflow |
| content.yml export | Custom Python | Build on our schema |
| Template generation (reverse) | Custom Python | Section headers → template |

### Deferred (address later)

| Capability | Difficulty | Reason |
|------------|:----------:|--------|
| Google Docs direct API | Medium | Requires OAuth setup, API key provisioning |
| Conditional/branching form detection | Hard | Requires runtime DOM diffing across states |
| Author role inference (co-first/co-senior) | Medium | NLP-based; varies wildly across journals |
| Equation extraction as LaTeX | Medium | GROBID handles some; not universal |
| Full reproducible flow formalization | Medium | Needs workflow engine (skills/agents) |
| Cross-publisher HTML normalization | Hard | Each publisher has unique DOM structure |

---

## 11. Deliverables

| # | Artifact | Path |
|:-:|----------|------|
| 1 | This requirements document | `standards/structured_content_extraction_requirements.md` |
| 2 | Paper extraction tool | `tools/paper-extractor/extract.py` |
| 3 | Scientific paper template | `templates/scientific-paper/_template.yml` |
| 4 | Reverse template generator | `tools/template-tools/generate_template.py` |
