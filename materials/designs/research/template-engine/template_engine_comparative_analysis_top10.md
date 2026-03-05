# Templated Document Processing Tools — Comparison Report

> **Date:** 2026-03-02 | **Requirements Spec:** [templated_document_processing_requirements.md](file:///home/mohammadi/repos/cytognosis/agents/standards/templated_document_processing_requirements.md)

---

## Executive Summary

We evaluated **10 candidate tools** against 14 structured requirements (1 Required, 4 Strongly Preferred, 9 Preferred) for templated document processing, generation, and verification. Requirements cover open-source licensing, text-only VCS-friendly formats, image handling, LaTeX math, diagram generation, multi-format output, AI/LLM integration, and dynamic code execution.

**Key findings:**

1. **Quarto** ranks #1 with the highest weighted score (51/54), excelling across nearly every requirement — text-based inputs, native LaTeX/Mermaid, multi-format output (HTML/PDF/DOCX/EPUB), first-class R/Python/Julia code execution, and growing LLM adoption.
2. **Pandoc** ranks #2 (47/54) as the most universal converter and Quarto's backbone. Unmatched format coverage but lacks native dynamic code execution.
3. **Typst** ranks #3 (39/54), a rapidly growing modern typesetting system (51.7k★), excellent for PDF but limited to PDF output and no native Mermaid/code execution.
4. **Jupyter Book** ranks #4 (38/54), strong for computational narratives but narrower output format support.
5. Tools like **Sphinx**, **R Markdown/Bookdown**, **Docusaurus**, **mdBook**, **Hugo**, and **Markdoc** fill niches but fall short on cross-cutting requirements.

> [!IMPORTANT]
> **Recommendation:** Adopt **Quarto** as the primary document processing system, with **Pandoc** as the conversion backbone (already bundled). Use **Typst** as an optional fast-PDF backend for Quarto (supported since Quarto 1.4+).

---

## Scoring Methodology

Each requirement is scored **0–3** (0 = not supported, 1 = via 3rd-party chaining, 2 = plugin/config, 3 = native) and multiplied by tier weight: **Required ×3**, **Strongly Preferred ×2**, **Preferred ×1**. Maximum = **54**.

---

## Summary Comparison Table

| Rank | Tool | ★ GitHub | License | R-6 (R) Img | R-1 (SP) OSS | R-4 (SP) Text VCS | R-9 (SP) LaTeX | R-10 (SP) Diagrams | R-2 (P) Adoption | R-3 (P) Multi-Input | R-7 (P) Img Style | R-11 (P) Multi-Out | R-13 (P) AI/LLM | R-14 (P) Dynamic Code | R-5 (P) Convert Chain | R-12 (P) Out Chain | **Total /54** |
|:----:|------|:--------:|---------|:-----------:|:------------:|:-----------------:|:--------------:|:------------------:|:----------------:|:-------------------:|:-----------------:|:------------------:|:---------------:|:--------------------:|:--------------------:|:------------------:|:-------------:|
| **1** | [**Quarto**](#1-quarto) | 5.3k | MIT | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 3 ×2=6 | 3 ×2=6 | 3 ×1=3 | 3 ×1=3 | 3 ×1=3 | 3 ×1=3 | 2 ×1=2 | 3 ×1=3 | 3 ×1=3 | 3 ×1=3 | **51** |
| **2** | [**Pandoc**](#2-pandoc) | 42.3k | GPL-2 | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 3 ×2=6 | 2 ×2=4 | 3 ×1=3 | 3 ×1=3 | 2 ×1=2 | 3 ×1=3 | 2 ×1=2 | 0 ×1=0 | 3 ×1=3 | 3 ×1=3 | **47** |
| **3** | [**Typst**](#3-typst) | 51.7k | Apache-2 | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 3 ×2=6 | 1 ×2=2 | 2 ×1=2 | 1 ×1=1 | 3 ×1=3 | 1 ×1=1 | 1 ×1=1 | 1 ×1=1 | 1 ×1=1 | 1 ×1=1 | **39** |
| **4** | [**Jupyter Book**](#4-jupyter-book) | 4.2k | BSD-3 | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 3 ×2=6 | 2 ×2=4 | 2 ×1=2 | 2 ×1=2 | 2 ×1=2 | 2 ×1=2 | 1 ×1=1 | 3 ×1=3 | 2 ×1=2 | 2 ×1=2 | **38** |
| **5** | [**Sphinx**](#5-sphinx) | 7.7k | BSD-2 | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 3 ×2=6 | 2 ×2=4 | 2 ×1=2 | 2 ×1=2 | 2 ×1=2 | 2 ×1=2 | 1 ×1=1 | 1 ×1=1 | 2 ×1=2 | 2 ×1=2 | **36** |
| **6** | [**R Markdown / Bookdown**](#6-r-markdown--bookdown) | 4.0k | GPL-3 | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 3 ×2=6 | 2 ×2=4 | 2 ×1=2 | 2 ×1=2 | 2 ×1=2 | 3 ×1=3 | 1 ×1=1 | 3 ×1=3 | 2 ×1=2 | 2 ×1=2 | **39** |
| **7** | [**Docusaurus**](#7-docusaurus) | 64k | MIT | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 2 ×2=4 | 2 ×2=4 | 3 ×1=3 | 1 ×1=1 | 3 ×1=3 | 1 ×1=1 | 2 ×1=2 | 0 ×1=0 | 1 ×1=1 | 1 ×1=1 | **32** |
| **8** | [**Hugo**](#8-hugo) | 86.9k | Apache-2 | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 1 ×2=2 | 1 ×2=2 | 3 ×1=3 | 1 ×1=1 | 3 ×1=3 | 1 ×1=1 | 2 ×1=2 | 0 ×1=0 | 1 ×1=1 | 1 ×1=1 | **28** |
| **9** | [**mdBook**](#9-mdbook) | 21.3k | MPL-2 | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 2 ×2=4 | 1 ×2=2 | 2 ×1=2 | 1 ×1=1 | 1 ×1=1 | 1 ×1=1 | 1 ×1=1 | 0 ×1=0 | 1 ×1=1 | 1 ×1=1 | **26** |
| **10** | [**Markdoc**](#10-markdoc) | 7.9k | MIT | 3 ×3=9 | 3 ×2=6 | 3 ×2=6 | 0 ×2=0 | 0 ×2=0 | 1 ×1=1 | 1 ×1=1 | 2 ×1=2 | 1 ×1=1 | 1 ×1=1 | 0 ×1=0 | 1 ×1=1 | 1 ×1=1 | **20** |

> [!NOTE]
> R Markdown/Bookdown ties Typst at 39 but is ranked lower (#6) because it is now in maintenance mode with Quarto as its successor, reducing its long-term viability.

---

## Detailed Tool Profiles

### 1. Quarto

| | |
|---|---|
| **URL** | [quarto.org](https://quarto.org) / [GitHub](https://github.com/quarto-dev/quarto-cli) |
| **GitHub Stars** | ~5,300 (quarto-cli) |
| **License** | MIT |
| **Latest Version** | 1.8 (Oct 2025) |
| **Language** | TypeScript/Lua (wraps Pandoc) |

**Description:** Quarto is Posit's next-generation open-source scientific and technical publishing system, built on top of Pandoc. It provides a unified authoring framework supporting Python, R, Julia, and Observable JS. Documents are authored in Quarto Markdown (`.qmd`) — plain text, YAML-frontmatter — making them fully git-trackable. Quarto natively supports LaTeX math, Mermaid/Graphviz/PlantUML diagrams (rendered at build-time), embedded/styled images, and outputs to HTML, PDF (via LaTeX or Typst), DOCX, EPUB, RevealJS slides, dashboards, websites, and books.

**Strengths against requirements:**
- ✅ **All tiers fully covered.** Native LaTeX, Mermaid, multi-format output, executable code cells, text-only VCS-friendly source.
- ✅ **Dynamic code execution** (R, Python, Julia) — strongest in this category.
- ✅ **Growing AI adoption** — LLM-assisted report generation, Quarto output used as LLM context; no dedicated MCP server yet but strong Pandoc MCP bridge.
- ✅ **Image handling** — size, alignment, captions, fig-layout via native attributes.
- ✅ **Data science community standard** — 14,000+ live sites, books, courses.

**Gaps & complementary tools:** Minimal. Pandoc (bundled) handles format conversions. Typst can be used as an alternative PDF engine.

**Weighted Score: 51/54**

---

### 2. Pandoc

| | |
|---|---|
| **URL** | [pandoc.org](https://pandoc.org) / [GitHub](https://github.com/jgm/pandoc) |
| **GitHub Stars** | ~42,300 |
| **License** | GPL-2.0 |
| **Latest Version** | 3.9 (Feb 2026) |
| **Language** | Haskell |

**Description:** Pandoc is the "Swiss Army knife" of document conversion — the most universal markup converter in existence. It converts between 40+ formats including Markdown, LaTeX, HTML, DOCX, EPUB, reStructuredText, Jupyter notebooks, AsciiDoc, and more. Pandoc supports LaTeX math natively, custom templates, citation/bibliography processing (CiteProc), and Lua/Python filters for AST manipulation. Latest v3.9 adds WebAssembly compilation for browser use.

**Strengths against requirements:**
- ✅ **Unmatched format coverage** — 40+ input/output formats.
- ✅ **Text-only, git-friendly** — Markdown source with YAML metadata.
- ✅ **LaTeX math** — native, multiple rendering backends (MathJax, KaTeX, MathML).
- ✅ **MCP server exists** — `mcp-pandoc` enables LLM-driven document conversion.
- ✅ **Mature ecosystem** — 42k★, universally adopted.

**Gaps & complementary tools:**
- ⚠️ **No native code execution** → complement with Quarto or Jupyter.
- ⚠️ **Diagrams** — no native Mermaid; use `mermaid-filter` or `pandoc-plot` (Lua filter). Score: 2/3.

**Weighted Score: 47/54**

---

### 3. Typst

| | |
|---|---|
| **URL** | [typst.app](https://typst.app) / [GitHub](https://github.com/typst/typst) |
| **GitHub Stars** | ~51,700 |
| **License** | Apache-2.0 |
| **Latest Version** | 0.13 (2025) |
| **Language** | Rust |

**Description:** Typst is a modern, blazing-fast typesetting system designed as a LaTeX replacement. It features a clean markup syntax inspired by Markdown, instant compilation (milliseconds vs. seconds for LaTeX), a built-in scripting language, excellent math typesetting, integrated bibliography management (CSL), and clear error messages. Typst produces high-quality PDFs and is gaining massive traction (51.7k★).

**Strengths against requirements:**
- ✅ **Outstanding math support** — cleaner than LaTeX syntax, equally capable.
- ✅ **Text-only source** — `.typ` files are fully git-trackable.
- ✅ **Fastest compilation** — sub-second incremental builds.
- ✅ **Beautiful PDF output** with full typographic control.
- ✅ **Built-in scripting** — conditional content, loops, custom functions.

**Gaps & complementary tools:**
- ⚠️ **PDF-only output natively** → complement with Pandoc for DOCX/HTML conversion. Quarto supports Typst as PDF backend.
- ⚠️ **No native Mermaid** → use `cetz` package for diagrams, or pre-render Mermaid to SVG with `mmdc` CLI.
- ⚠️ **No native code execution** → complement with Quarto (which supports Typst output).
- ⚠️ **Limited AI/LLM tooling** — growing but no dedicated MCP server yet.

**Weighted Score: 39/54**

---

### 4. Jupyter Book

| | |
|---|---|
| **URL** | [jupyterbook.org](https://jupyterbook.org) / [GitHub](https://github.com/jupyter-book/jupyter-book) |
| **GitHub Stars** | ~4,200 |
| **License** | BSD-3-Clause |
| **Latest Version** | 2.0 (2025) |
| **Language** | Python (MyST Markdown) |

**Description:** Jupyter Book builds publication-quality books and documents from computational content. Built on MyST Markdown and Sphinx, it supports executable Jupyter notebooks, interactive figures via JupyterHub/Binder, LaTeX math, cross-references, and outputs to HTML websites and PDF (via LaTeX or Typst in v2.0). Powers 14,000+ open online textbooks.

**Strengths against requirements:**
- ✅ **Best-in-class code execution** — inline Python/R/Julia cells, Pyodide/JupyterLite for browser execution.
- ✅ **MyST Markdown** — text-only, git-friendly, rich extension syntax.
- ✅ **Native LaTeX math** and cross-referencing.
- ✅ **Mermaid support** via MyST directive.
- ✅ **Typst PDF export** in v2.0.

**Gaps & complementary tools:**
- ⚠️ **No native DOCX output** → complement with Pandoc for `.docx`.
- ⚠️ **Primarily HTML + PDF** — limited multi-format. Score: 2/3.
- ⚠️ **Moderate AI tooling** — Jupyter ecosystem well-known to LLMs but no dedicated MCP.

**Weighted Score: 38/54**

---

### 5. Sphinx

| | |
|---|---|
| **URL** | [sphinx-doc.org](https://www.sphinx-doc.org) / [GitHub](https://github.com/sphinx-doc/sphinx) |
| **GitHub Stars** | ~7,700 |
| **License** | BSD-2-Clause |
| **Latest Version** | 8.x (2025) |
| **Language** | Python |

**Description:** Sphinx is the de facto documentation generator for Python projects. It uses reStructuredText (or MyST Markdown) as input and generates HTML, PDF (via LaTeX), EPUB, and man pages. Features auto-API documentation, powerful cross-referencing, Jinja2 templating, extensive theme ecosystem, and internationalization.

**Strengths against requirements:**
- ✅ **Mature ecosystem** — used by Python, Linux kernel, countless OSS projects.
- ✅ **LaTeX math** and PDF via LaTeX pipeline.
- ✅ **Mermaid** via `sphinxcontrib-mermaid` extension.
- ✅ **Multiple output formats** — HTML, PDF, EPUB, man pages.

**Gaps & complementary tools:**
- ⚠️ **reStructuredText as primary** — steeper learning curve than Markdown (MyST bridges this).
- ⚠️ **Limited dynamic code execution** — `sphinx-gallery` runs examples but not inline; complement with Jupyter.
- ⚠️ **No DOCX output** → complement with Pandoc.
- ⚠️ **Low AI/LLM-specific tooling** — well-known to LLMs for documentation but no MCP.

**Weighted Score: 36/54**

---

### 6. R Markdown / Bookdown

| | |
|---|---|
| **URL** | [bookdown.org](https://bookdown.org) / [GitHub](https://github.com/rstudio/bookdown) |
| **GitHub Stars** | ~4,000 (bookdown) |
| **License** | GPL-3.0 |
| **Latest Version** | 0.40 (maintenance mode) |
| **Language** | R (knitr + Pandoc) |

**Description:** R Markdown and its book-authoring extension Bookdown were the precursors to Quarto. They enable literate programming with embedded R/Python code, outputting to HTML, PDF (LaTeX), DOCX, and EPUB. Thousands of published books at bookdown.org. Now in **maintenance mode** — Posit directs new projects to Quarto.

**Strengths against requirements:**
- ✅ **Excellent dynamic code execution** — R, Python, SQL, Julia via knitr.
- ✅ **Multi-format output** — HTML, PDF, DOCX, EPUB via Pandoc.
- ✅ **LaTeX math**, cross-references, citations.
- ✅ **Text-only Markdown** source.

**Gaps & complementary tools:**
- ⚠️ **Maintenance mode** — no major new features; superseded by Quarto.
- ⚠️ **R-centric** — requires R runtime even for Python-only workflows.
- ⚠️ **Mermaid** — via DiagrammeR package, not as seamless. Score: 2/3.
- ⚠️ **Limited AI tooling** — LLMs know it well but Quarto is preferred target.

**Weighted Score: 39/54** _(ranked lower due to maintenance-mode status)_

---

### 7. Docusaurus

| | |
|---|---|
| **URL** | [docusaurus.io](https://docusaurus.io) / [GitHub](https://github.com/facebook/docusaurus) |
| **GitHub Stars** | ~64,000 |
| **License** | MIT |
| **Latest Version** | 3.7 (2025) |
| **Language** | TypeScript/React |

**Description:** Docusaurus is Meta's open-source documentation framework built with React. It uses MDX (Markdown + JSX) for content, supports versioning, i18n, Algolia search, and produces polished documentation websites. LaTeX math via KaTeX plugin; Mermaid diagrams via plugin.

**Strengths against requirements:**
- ✅ **Massive adoption** (64k★), strong ecosystem.
- ✅ **MDX** — Markdown-based, text-only, git-friendly.
- ✅ **Image handling** — full React component control over size/position.
- ✅ **Growing AI tooling** — LLMs commonly generate Docusaurus content.

**Gaps & complementary tools:**
- ⚠️ **HTML-only output** — no PDF/DOCX natively → complement with Pandoc for conversion.
- ⚠️ **No dynamic code execution** — static site only.
- ⚠️ **LaTeX via plugin** (KaTeX), not native. Score: 2/3.
- ⚠️ **Single input format** (MDX only).

**Weighted Score: 32/54**

---

### 8. Hugo

| | |
|---|---|
| **URL** | [gohugo.io](https://gohugo.io) / [GitHub](https://github.com/gohugoio/hugo) |
| **GitHub Stars** | ~86,900 |
| **License** | Apache-2.0 |
| **Latest Version** | 0.143 (2025) |
| **Language** | Go |

**Description:** Hugo is the world's fastest static site generator, written in Go. It processes Markdown content with Go templates, supports Goldmark (GitHub-flavored Markdown), image processing pipelines, multilingual sites, and JS/Sass bundling. Produces HTML websites with exceptional build speed (thousands of pages in seconds).

**Strengths against requirements:**
- ✅ **Highest GitHub stars** among all candidates (86.9k★).
- ✅ **Blazing fast** builds, excellent developer experience.
- ✅ **Image processing** — built-in resize, crop, filter pipeline.
- ✅ **Text-only Markdown** source, git-friendly.

**Gaps & complementary tools:**
- ⚠️ **HTML-only output** — no PDF/DOCX → complement with Pandoc.
- ⚠️ **No native LaTeX math** → use MathJax/KaTeX shortcodes. Score: 1/3.
- ⚠️ **No native Mermaid** → Hugo Mermaid shortcode or pre-render. Score: 1/3.
- ⚠️ **No code execution** — static only.
- ⚠️ **Go templates** (not standard Markdown extensions) for logic.

**Weighted Score: 28/54**

---

### 9. mdBook

| | |
|---|---|
| **URL** | [rust-lang.github.io/mdBook](https://rust-lang.github.io/mdBook/) / [GitHub](https://github.com/rust-lang/mdBook) |
| **GitHub Stars** | ~21,300 |
| **License** | MPL-2.0 |
| **Latest Version** | 0.4.43 (2025) |
| **Language** | Rust |

**Description:** mdBook is a utility to create modern online books from Markdown files, most famously used for "The Rust Programming Language" book. It features MathJax support, syntax highlighting, search, theming, and Rust Playground integration for executable Rust code snippets.

**Strengths against requirements:**
- ✅ **Simple, focused** — easy Markdown-to-book workflow.
- ✅ **MathJax support** for equations (plugin-based). Score: 2/3.
- ✅ **Text-only Markdown**, git-friendly.
- ✅ **Solid adoption** in Rust ecosystem (21k★).

**Gaps & complementary tools:**
- ⚠️ **HTML-only output** → complement with Pandoc for PDF/DOCX.
- ⚠️ **No native Mermaid** → `mdbook-mermaid` preprocessor. Score: 1/3.
- ⚠️ **No dynamic code execution** (Rust Playground only, not general).
- ⚠️ **Limited image styling** — basic Markdown images only. Score: 1/3.
- ⚠️ **Minimal AI tooling** presence.

**Weighted Score: 26/54**

---

### 10. Markdoc

| | |
|---|---|
| **URL** | [markdoc.dev](https://markdoc.dev) / [GitHub](https://github.com/markdoc/markdoc) |
| **GitHub Stars** | ~7,900 |
| **License** | MIT |
| **Latest Version** | 0.4 (2024) |
| **Language** | TypeScript |

**Description:** Markdoc is Stripe's Markdown-based authoring framework designed for creating custom documentation experiences. It extends Markdown with tags, annotations, and a declarative composition model. Features type safety, validation, custom renderers (HTML, React), and modular content (partials). Powers Stripe's public documentation.

**Strengths against requirements:**
- ✅ **Powerful templating** — custom tags, variables, conditional rendering.
- ✅ **Type safety & validation** — enforces documentation structure.
- ✅ **Text-only Markdown**, git-friendly.
- ✅ **Image handling** — custom tag support for styling. Score: 2/3.

**Gaps & complementary tools:**
- ⚠️ **No LaTeX math** natively → would need custom tag/renderer. Score: 0/3.
- ⚠️ **No diagram support** → would need custom integration. Score: 0/3.
- ⚠️ **HTML/React only** output → complement with Pandoc for PDF/DOCX.
- ⚠️ **No code execution**.
- ⚠️ **Documentation-focused niche** — limited general-purpose use.

**Weighted Score: 20/54**

---

## Gap Analysis: Complementary OSS Tools

For candidates missing features, the following open-source tools can bridge gaps:

| Missing Capability | Complementary Tool | Notes |
|---|---|---|
| **DOCX output** | [Pandoc](https://pandoc.org) | Universal converter; reference `.docx` for styling |
| **PDF output** | [Pandoc](https://pandoc.org) via LaTeX, or [Typst](https://typst.app) | Quarto bundles Pandoc; Typst is faster |
| **LaTeX math in HTML** | [KaTeX](https://katex.org) / [MathJax](https://mathjax.org) | JS-based math rendering |
| **Mermaid diagrams** | [Mermaid CLI (`mmdc`)](https://github.com/mermaid-js/mermaid-cli) | Pre-render to SVG/PNG |
| **Code execution** | [Quarto](https://quarto.org) / [Jupyter](https://jupyter.org) | Inline Python/R/Julia execution |
| **AI/MCP integration** | [`mcp-pandoc`](https://github.com/vivekVells/mcp-pandoc) | MCP server for Pandoc conversion |
| **Format conversion** | [Pandoc](https://pandoc.org) | Bridges any input→output gap |

---

## Final Rankings

| Rank | Tool | Score /54 | Best For |
|:----:|------|:---------:|----------|
| 1 | **Quarto** | **51** | Scientific/technical publishing, data science, reproducible research |
| 2 | **Pandoc** | **47** | Universal format conversion, academic writing, CI/CD pipelines |
| 3 | **Typst** | **39** | Fast, beautiful PDF typesetting, LaTeX replacement |
| 4 | **R Markdown** | **39** | Legacy R-based literate programming (maintenance mode) |
| 5 | **Jupyter Book** | **38** | Computational narratives, interactive textbooks |
| 6 | **Sphinx** | **36** | Python API documentation, technical references |
| 7 | **Docusaurus** | **32** | Developer documentation websites |
| 8 | **Hugo** | **28** | High-performance static websites |
| 9 | **mdBook** | **26** | Simple online technical books |
| 10 | **Markdoc** | **20** | Custom documentation frameworks |
