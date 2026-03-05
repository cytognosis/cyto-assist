# Quarto Template Engine — Format Specification

> **Version:** 1.0 | **Date:** 2026-03-02 | **Engine:** [Quarto](https://quarto.org) v1.8+

---

## 1. Overview

Quarto is an open-source scientific and technical publishing system built on [Pandoc](https://pandoc.org). This document specifies the input formats, configuration schema, content authoring features, extension mechanisms, and output formats that Quarto accepts and produces.

All Quarto source files are **plain-text** and fully compatible with standard VCS tools (git).

---

## 2. Input File Formats

Quarto accepts four input file formats:

| Extension | Name | Description | Execution Engine |
|-----------|------|-------------|-----------------|
| `.qmd` | **Quarto Markdown** | Native format. Pandoc Markdown + Quarto extensions + YAML frontmatter. Recommended for all new documents. | knitr (R), Jupyter (Python/Julia), OJS |
| `.md` | **Markdown** | Standard/GFM Markdown. Quarto enhances it with Pandoc extensions. No executable code by default. | None (static) |
| `.ipynb` | **Jupyter Notebook** | JSON-based notebook with embedded code cells and outputs. Quarto renders without re-execution by default. | Jupyter |
| `.Rmd` | **R Markdown** | Legacy format, backward-compatible. Quarto renders via knitr. New projects should use `.qmd`. | knitr |

> [!TIP]
> **Recommended format:** `.qmd` — it combines the readability of Markdown with the power of executable code cells, and is the most feature-complete format in Quarto.

---

## 3. YAML Frontmatter Schema

Every `.qmd`/`.md` file begins with a YAML frontmatter block delimited by `---`. The frontmatter defines document metadata and output configuration.

### 3.1 Core Metadata Fields

```yaml
---
title: "Document Title"
subtitle: "Optional subtitle"
author:
  - name: "Author Name"
    email: "author@example.org"
    affiliation: "Organization"
    orcid: "0000-0000-0000-0000"
date: "2026-03-02"              # or: today, last-modified
date-format: "MMMM D, YYYY"
abstract: |
  Multi-line abstract text.
keywords: [keyword1, keyword2]
lang: en
bibliography: references.bib
csl: citation-style.csl
---
```

### 3.2 Format-Specific Output Options

```yaml
---
format:
  html:
    toc: true
    toc-depth: 3
    number-sections: true
    theme: cosmo                 # Bootstrap theme
    css: custom.css
    code-fold: true
    self-contained: true
  pdf:
    documentclass: article
    papersize: letter
    margin-left: 1in
    margin-right: 1in
    fontsize: 11pt
    pdf-engine: lualatex         # or: xelatex, typst
    keep-tex: true
  docx:
    reference-doc: template.docx # Style reference document
    toc: true
  typst:
    papersize: us-letter
    margin: (x: 1in, y: 1in)
  epub:
    cover-image: cover.png
  revealjs:
    slide-number: true
    theme: dark
---
```

### 3.3 Execution Options

```yaml
---
execute:
  echo: true          # Show source code
  eval: true           # Execute code cells
  warning: false       # Suppress warnings
  freeze: auto         # Cache: auto | true | false
  cache: true          # Fine-grained caching
jupyter: python3       # Kernel specification
---
```

---

## 4. Project Configuration (`_quarto.yml`)

Multi-document projects use a `_quarto.yml` file at the project root. Options defined here apply as defaults across all documents, overridable per-file.

### 4.1 Schema Overview

```yaml
project:
  type: default        # default | website | book | manuscript
  output-dir: _output
  render:
    - "*.qmd"
  
# Shared metadata (applied to all documents)
title: "Project Title"
author: "Author Name"
date: today

# Format defaults
format:
  html:
    theme: cosmo
    toc: true
  pdf:
    documentclass: report

# Profiles (dev vs. production)
profile:
  default: production
  group:
    - [light, dark]
```

### 4.2 Project Types

| Type | Description | Additional Config |
|------|-------------|-------------------|
| `default` | Standalone documents | Minimal |
| `website` | Multi-page website with navigation | `website:` block with `navbar`, `sidebar`, `search` |
| `book` | Multi-chapter book | `book:` block with `chapters`, `appendices`, `references` |
| `manuscript` | Academic manuscript with notebooks | `manuscript:` block with `article`, `notebooks` |

---

## 5. Content Authoring Features

### 5.1 Text Formatting

Quarto uses Pandoc Markdown, which includes all standard Markdown plus:

- **Superscript/subscript:** `H~2~O`, `x^2^`
- **Strikethrough:** `~~deleted~~`
- **Small caps:** `[text]{.smallcaps}`
- **Inline spans:** `[styled text]{style="color: red;"}`
- **Footnotes:** `[^1]` with definitions
- **Definition lists, task lists, pipe tables, grid tables**

### 5.2 Callout Blocks

Five built-in types with cross-referencing support:

```markdown
:::{.callout-note}
## Optional Title
Content here.
:::

:::{.callout-warning}
Warning content.
:::

:::{.callout-tip}
:::{.callout-important}
:::{.callout-caution}
```

### 5.3 Cross-References

Prefix-based labeling system with automatic numbering:

| Element | Label Prefix | Usage |
|---------|-------------|-------|
| Figures | `#fig-` | `@fig-name` |
| Tables | `#tbl-` | `@tbl-name` |
| Equations | `#eq-` | `@eq-name` |
| Sections | `#sec-` | `@sec-name` |
| Code listings | `#lst-` | `@lst-name` |
| Theorems | `#thm-` | `@thm-name` |

### 5.4 Citations & Bibliography

```markdown
Single citation: [@smith2020]
Multiple: [@smith2020; @jones2021]
Narrative: @smith2020 argues that...
Suppress author: [-@smith2020]
```

Requires `bibliography: references.bib` in frontmatter. Supports BibTeX, BibLaTeX, CSL JSON/YAML. Auto-generated bibliography section.

### 5.5 Mathematical Equations

LaTeX math syntax, rendered in all output formats:

```markdown
Inline: $E = mc^2$

Display:
$$
\int_0^\infty f(x) \, dx = 1
$$ {#eq-integral}
```

### 5.6 Figures & Images

```markdown
![Caption text](image.png){#fig-example fig-alt="Alt text" width="80%"}

Subfigure layout:
::: {#fig-panel layout-ncol=2}
![Sub A](a.png){#fig-a}
![Sub B](b.png){#fig-b}

Combined caption
:::
```

Attributes: `width`, `height`, `fig-align` (left/center/right), `fig-cap`, `fig-alt`, `fig-link`.

### 5.7 Diagrams (Rendered at Build-Time)

Native support via code blocks with language identifiers:

````markdown
```{mermaid}
graph LR
  A --> B --> C
```

```{dot}
digraph { A -> B -> C }
```

```{plantuml}
@startuml
Alice -> Bob: Hello
@enduml
```
````

### 5.8 Tables

- **Pipe tables** — simple Markdown syntax
- **Grid tables** — complex layouts with multi-line cells, row/column spans
- **Computational tables** — generated from R/Python code cells
- **Captions and cross-references** via `#tbl-` labels

### 5.9 Executable Code Cells

````markdown
```{python}
#| label: fig-scatter
#| fig-cap: "Scatter plot of x vs y"
#| echo: false

import matplotlib.pyplot as plt
plt.scatter(x, y)
plt.show()
```

```{r}
#| label: tbl-summary
#| tbl-cap: "Summary statistics"

knitr::kable(summary(df))
```
````

Supported languages: **Python**, **R**, **Julia**, **Observable JS**.
Cell options: `label`, `fig-cap`, `tbl-cap`, `echo`, `eval`, `output`, `warning`, `code-fold`, `code-summary`.

### 5.10 Divs and Spans (Layout)

```markdown
:::{.columns}
:::{.column width="50%"}
Left column content
:::
:::{.column width="50%"}
Right column content
:::
:::

[highlighted]{.mark}
[small caps]{.smallcaps}
```

### 5.11 Includes and Parameters

```markdown
{{< include _shared-content.qmd >}}
{{< meta title >}}
{{< var organization.name >}}
```

Parameters enable parameterized reports:

```yaml
---
params:
  region: "US-West"
  year: 2025
---
```

---

## 6. Extension Mechanism

### 6.1 Extension Types

| Type | Description | Creation Command |
|------|-------------|-----------------|
| **Custom Format** | New output format with bundled styles, templates, filters | `quarto create extension format` |
| **Shortcode** | Custom inline/block content directives | `quarto create extension shortcode` |
| **Filter** | Lua-based AST transformations | `quarto create extension filter` |
| **RevealJS Plugin** | Presentation plugin | `quarto create extension revealjs-plugin` |

### 6.2 Extension Structure

```
_extensions/
  my-extension/
    _extension.yml       # Metadata + contributed components
    my-filter.lua        # Lua filter (optional)
    my-shortcode.lua     # Shortcode handler (optional)
    styles.css           # Custom styles (optional)
    template.tex         # Custom LaTeX template (optional)
```

### 6.3 `_extension.yml` Schema

```yaml
title: My Extension
author: Author Name
version: 1.0.0
quarto-required: ">=1.4.0"
contributes:
  formats:
    html:
      css: [styles.css]
      filters: [my-filter.lua]
    pdf:
      template: template.tex
  shortcodes:
    - my-shortcode.lua
  filters:
    - my-filter.lua
```

---

## 7. Output Formats

### 7.1 Complete Output Format List

| Category | Format | Key |
|----------|--------|-----|
| **Documents** | HTML | `html` |
| | PDF (LaTeX) | `pdf` |
| | PDF (Typst) | `typst` |
| | Microsoft Word | `docx` |
| | OpenDocument | `odt` |
| | Rich Text | `rtf` |
| | EPUB | `epub` |
| | Jupyter Notebook | `ipynb` |
| | JATS (XML) | `jats` |
| | AsciiDoc | `asciidoc` |
| | reStructuredText | `rst` |
| | ConTeXt | `context` |
| **Presentations** | RevealJS (HTML) | `revealjs` |
| | PowerPoint | `pptx` |
| | Beamer (LaTeX) | `beamer` |
| **Markdown** | GitHub-flavored | `gfm` |
| | CommonMark | `commonmark` |
| | Hugo | `hugo-md` |
| | Docusaurus | `docusaurus-md` |
| **Projects** | Website | `project: website` |
| | Book | `project: book` |
| | Dashboard | `dashboard` |
| | Manuscript | `project: manuscript` |

### 7.2 Rendering

```bash
# Single document
quarto render document.qmd                  # All formats in YAML
quarto render document.qmd --to pdf         # Specific format
quarto render document.qmd --to html,pdf    # Multiple formats

# Project
quarto render                               # Entire project
quarto preview                              # Live dev server
quarto publish gh-pages                     # Deploy to GitHub Pages
```

---

## 8. File Taxonomy Summary

| File | Purpose | Format | VCS-Friendly |
|------|---------|--------|:------------:|
| `*.qmd` | Source document (content + code) | Plain text (Markdown + YAML) | ✅ |
| `*.md` | Source document (content only) | Plain text (Markdown + YAML) | ✅ |
| `*.ipynb` | Jupyter notebook source | JSON | ⚠️ (large diffs) |
| `*.Rmd` | Legacy R Markdown source | Plain text (Markdown + YAML) | ✅ |
| `_quarto.yml` | Project configuration | YAML | ✅ |
| `_metadata.yml` | Directory-level metadata | YAML | ✅ |
| `_brand.yml` | Visual branding (v1.8+) | YAML | ✅ |
| `_variables.yml` | Reusable variables | YAML | ✅ |
| `references.bib` | Bibliography | BibTeX | ✅ |
| `*.csl` | Citation style | XML | ✅ |
| `_extensions/*/` | Extensions | YAML + Lua | ✅ |
| `template.docx` | DOCX style reference | Binary | ❌ |
| `template.tex` | LaTeX template | Plain text | ✅ |
