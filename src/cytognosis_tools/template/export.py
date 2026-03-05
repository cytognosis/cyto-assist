#!/usr/bin/env python3
"""
export_template.py — Export a _template.yml to human-readable Markdown.

Generates a clean, questions-only Markdown document suitable for:
  - Sharing with humans to read and fill out
  - Storing in a collection of human-readable templates
  - Cross-template analysis (similarity/difference detection)

Usage:
  python export_template.py templates/qb3/_template.yml
  python export_template.py templates/qb3/_template.yml -o templates/qb3/exported.md
  python export_template.py templates/qb3/_template.yml --with-metadata
"""

import argparse
import sys
from pathlib import Path

import yaml


def load_template(path: str) -> dict:
    """Load and parse a _template.yml file."""
    with open(path) as f:
        return yaml.safe_load(f)


def render_field_markdown(field: dict, field_num: int) -> list[str]:
    """Render a single field definition as Markdown lines."""
    label = field["label"]
    required = " *" if field.get("required") else ""
    ftype = field.get("type", "text")
    hint = field.get("hint")
    placeholder = field.get("placeholder")
    constraints = field.get("constraints", {})

    lines = [f"### {label}{required}\n"]

    # ── Metadata line (type + constraints) ──
    meta_parts = [f"Type: `{ftype}`"]
    if constraints.get("maxWords"):
        meta_parts.append(f"Max {constraints['maxWords']} words")
    if constraints.get("minWords"):
        meta_parts.append(f"Min {constraints['minWords']} words")
    if constraints.get("maxChars"):
        meta_parts.append(f"Max {constraints['maxChars']} chars")
    if constraints.get("maxSizeMB"):
        meta_parts.append(f"Max {constraints['maxSizeMB']} MB")
    if constraints.get("formats"):
        meta_parts.append(f"Formats: {', '.join(constraints['formats'])}")
    if constraints.get("maxPages"):
        meta_parts.append(f"Max {constraints['maxPages']} pages")
    lines.append(f"> {' · '.join(meta_parts)}\n")

    # ── Hint ──
    if hint:
        lines.append(f"> _{hint}_\n")

    # ── Placeholder ──
    if placeholder:
        lines.append(f"> _Format: {placeholder}_\n")

    # ── Field-type-specific rendering ──
    if ftype == "choice":
        options = field.get("options", [])
        for opt in options:
            lines.append(f"- [ ] {opt}")
        lines.append("")
    elif ftype == "multichoice":
        options = field.get("options", [])
        for opt in options:
            lines.append(f"- [ ] {opt}")
        lines.append("")
    elif ftype in ("name", "address"):
        subfields = field.get("subfields", [])
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        for sf in subfields:
            req = " *" if sf.get("required") else ""
            lines.append(f"| {sf['label']}{req} |       |")
        lines.append("")
    elif ftype == "file":
        lines.append("```")
        lines.append("[ Upload file ]")
        lines.append("```\n")
    elif ftype in ("text",):
        lines.append("```text\n\n```\n")
    elif ftype in ("textarea", "section"):
        lines.append("```text\n\n```\n")
    elif ftype == "boolean":
        lines.append("- [ ] Yes")
        lines.append("- [ ] No\n")
    elif ftype == "date":
        lines.append("```text\nYYYY-MM-DD\n```\n")
    elif ftype == "number":
        lines.append("```text\n\n```\n")
    else:
        lines.append("```text\n\n```\n")

    return lines


def export_template(
    template: dict,
    *,
    with_metadata: bool = False,
    with_ids: bool = False,
) -> str:
    """Convert a template dict to a human-readable Markdown string."""
    tmpl_meta = template.get("template", {})
    sections = template.get("sections", [])

    lines = []

    # ── Title ──
    name = tmpl_meta.get("name", "Untitled Template")
    lines.append(f"# {name}\n")

    # ── Source / metadata ──
    if tmpl_meta.get("source"):
        lines.append(f"> Source: <{tmpl_meta['source']}>")
    if tmpl_meta.get("version"):
        lines.append(f"> Version: {tmpl_meta['version']}")
    if lines[-1] != "":
        lines.append("")

    if with_metadata:
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        for k, v in tmpl_meta.items():
            if k not in ("name",):
                lines.append(f"| {k} | {v} |")
        lines.append("")

    lines.append("---\n")

    # ── Sections ──
    field_num = 0
    for section in sections:
        title = section["title"]
        note = section.get("note")
        section_id = section["id"]

        lines.append(f"## {title}\n")

        if with_ids:
            lines.append(f"> _Section ID: `{section_id}`_\n")

        if note:
            lines.append("> [!NOTE]")
            lines.append(f"> {note}\n")

        for field in section.get("fields", []):
            field_num += 1
            if with_ids:
                lines.append(f"> _Field ID: `{section_id}.{field['id']}`_\n")
            lines.extend(render_field_markdown(field, field_num))

        lines.append("---\n")

    # ── Footer ──
    footer = tmpl_meta.get("footer")
    if footer:
        lines.append(f"_{footer}_\n")

    lines.append("> **\\* = Required field**\n")

    # ── Stats ──
    total_fields = sum(len(s.get("fields", [])) for s in sections)
    required_fields = sum(
        1 for s in sections for f in s.get("fields", []) if f.get("required")
    )
    lines.append("---\n")
    lines.append(
        f"_Template: {total_fields} fields ({required_fields} required) across {len(sections)} sections._"
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Export a _template.yml to human-readable Markdown",
    )
    parser.add_argument(
        "template",
        help="Path to _template.yml file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output Markdown file path (default: stdout)",
    )
    parser.add_argument(
        "--with-metadata",
        action="store_true",
        help="Include full template metadata table",
    )
    parser.add_argument(
        "--with-ids",
        action="store_true",
        help="Include section/field IDs (for cross-referencing)",
    )
    args = parser.parse_args()

    template = load_template(args.template)
    md = export_template(
        template,
        with_metadata=args.with_metadata,
        with_ids=args.with_ids,
    )

    if args.output:
        Path(args.output).write_text(md + "\n")
        print(f"✓ Exported to {args.output}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
