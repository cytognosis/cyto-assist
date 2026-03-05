# Template Schema Specification — `_template.yml`

> **Version:** 1.0 | **Date:** 2026-03-02

---

## 1. Overview

The `_template.yml` file is a YAML-based schema that defines the structure, field types, and constraints for any templated document — applications, grant proposals, forms, or structured reports. It is the **single source of truth** for what content a document requires.

Content is authored separately in `content.yml` (structured data) and/or `.qmd` files (long-form narrative). A validation pipeline (JSON Schema + Lua filter) checks content against the template before rendering.

---

## 2. Top-Level Schema

```yaml
template:
  name: string          # Human-readable template name
  version: string       # Template version (e.g., "2026-winter", "1.0")
  source: url           # Original source URL (if applicable)
  output_formats: list  # [html, pdf, docx, epub]
  footer: string        # Footer text for rendered output

sections: list          # Ordered list of section definitions
```

---

## 3. Section Definition

```yaml
sections:
  - id: string          # Machine-readable section identifier
    title: string       # Human-readable section heading
    note: string        # Optional callout note displayed above fields
    fields: list        # Ordered list of field definitions
```

---

## 4. Field Definition

```yaml
fields:
  - id: string          # Machine-readable field identifier
    label: string       # Display label / question text
    type: enum          # Field type (see §5)
    required: boolean   # Whether the field must be filled (default: false)
    placeholder: string # Example/placeholder text
    hint: string        # Helper text displayed below the field
    options: list       # For choice/multichoice: list of allowed values
    subfields: list     # For compound types (name, address): nested fields
    constraints: object # Validation constraints (see §6)
```

---

## 5. Field Types

| Type | Description | Value Format in `content.yml` |
|------|-------------|-------------------------------|
| `text` | Single-line text input | `string` |
| `textarea` | Multi-line text (Markdown allowed) | `string` (use YAML `\|` for multiline) |
| `email` | Email address | `string` (validated format) |
| `phone` | Phone number | `string` |
| `url` | URL | `string` (validated format) |
| `date` | Date value | `string` (ISO 8601: `YYYY-MM-DD`) |
| `number` | Numeric value | `integer` or `float` |
| `boolean` | True/false | `boolean` |
| `choice` | Single selection from `options` | `string` (must match one option) |
| `multichoice` | Multiple selections from `options` | `list` of `string` |
| `name` | Compound name with `subfields` | `object` with subfield keys |
| `address` | Compound address with `subfields` | `object` with subfield keys |
| `file` | File attachment reference | `string` (path) or `null` |
| `section` | Long-form Markdown content | `string` (Markdown) |

---

## 6. Constraint Keywords

| Keyword | Applies To | Type | Description |
|---------|-----------|------|-------------|
| `maxWords` | text, textarea, section | `integer` | Maximum number of words |
| `minWords` | text, textarea, section | `integer` | Minimum number of words |
| `maxChars` | text, textarea | `integer` | Maximum character count |
| `minChars` | text, textarea | `integer` | Minimum character count |
| `maxPages` | section | `integer` | Maximum page count (for PDF) |
| `pattern` | text, phone, url | `string` | Regex pattern for validation |
| `min` | number | `number` | Minimum numeric value |
| `max` | number | `number` | Maximum numeric value |
| `minDate` | date | `string` | Earliest allowed date (ISO 8601) |
| `maxDate` | date | `string` | Latest allowed date (ISO 8601) |
| `maxSizeMB` | file | `number` | Maximum file size in MB |
| `formats` | file | `list` | Allowed file extensions |
| `minSelect` | multichoice | `integer` | Minimum selections required |
| `maxSelect` | multichoice | `integer` | Maximum selections allowed |

---

## 7. Content File Format (`content.yml`)

Content is structured as a flat YAML file mirroring the section/field hierarchy:

```yaml
# Keys match section IDs from _template.yml
section_id:
  field_id: "value"
  compound_field_id:
    subfield_id: "value"
```

### Rules

1. **Top-level keys** must match section `id` values from the template
2. **Second-level keys** must match field `id` values within that section
3. **Compound fields** (name, address) use nested objects matching subfield `id` values
4. **Choice fields** must contain a value from the defined `options` list
5. **Multichoice fields** must contain a list of values from `options`
6. **File fields** use `null` for no upload or a relative file path
7. **Textarea/section fields** use YAML `|` block scalar for multiline content

---

## 8. Validation Pipeline

### Phase 1: Pre-render (Python CLI)

```bash
python validate.py --template _template.yml --content content.yml
```

Checks:
- All required fields present and non-empty
- Field types match (email format, date format, etc.)
- Choice values match allowed options
- File references exist

### Phase 2: At-render (Quarto Lua Filter)

Checks during `quarto render`:
- Word count constraints (`maxWords`, `minWords`)
- Character count constraints (`maxChars`, `minChars`)
- Emits warnings/errors in rendered output

---

## 9. Directory Structure

A complete template consists of:

```
templates/<template-name>/
├── _template.yml          # Schema definition (Layer 1)
├── content.yml            # Content data (Layer 2)
├── template.qmd           # Quarto renderer (Layer 3)
├── _quarto.yml            # Project config (optional)
└── attachments/           # Referenced files (optional)
```

---

## 10. Example

See the first reference implementation:

- **Template:** [`templates/qb3/_template.yml`](file:///home/mohammadi/repos/cytognosis/agents/templates/qb3/_template.yml)
- **Content:** [`templates/qb3/content.yml`](file:///home/mohammadi/repos/cytognosis/agents/templates/qb3/content.yml)
- **Renderer:** [`templates/qb3/template.qmd`](file:///home/mohammadi/repos/cytognosis/agents/templates/qb3/template.qmd)
