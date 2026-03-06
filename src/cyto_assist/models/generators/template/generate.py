#!/usr/bin/env python3
"""
generate_template.py — Reverse template generation from a document.

Given a document, generates a _template.yml by detecting sections/structure
and mapping them to field types in our template schema format.

This is the reverse operation of content extraction:
  - Forward:  doc + _template.yml → content.yml
  - Reverse:  doc + config → _template.yml

Usage:
  python generate_template.py paper.pdf -o _template.yml
  python generate_template.py paper.pdf --name "Nature Article" -o _template.yml
  python generate_template.py paper.docx --include-content -o _template.yml
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

# Reuse the extraction functions from the extract module
from cytognosis_tools.extract import (
    detect_format,
    extract_docx,
    extract_latex,
    extract_markdown,
    extract_pdf,
)


def infer_field_type(value: str | None) -> str:
    """Infer field type from content."""
    if not value:
        return "text"
    if re.match(r"^https?://", str(value)):
        return "url"
    if re.match(r"^[\w.+-]+@[\w-]+\.[\w.-]+$", str(value)):
        return "email"
    if len(str(value)) > 200:
        return "section"
    if len(str(value)) > 50:
        return "textarea"
    return "text"


def content_to_template(
    data: dict,
    template_name: str = "Auto-Generated Template",
    source: str = "",
    include_content_hints: bool = False,
) -> dict:
    """Convert extracted content data into a _template.yml schema."""
    template = {
        "template": {
            "name": template_name,
            "version": "1.0",
            "output_formats": ["html", "pdf", "docx"],
        },
        "sections": [],
    }

    if source:
        template["template"]["source"] = source

    # ── Map extracted sections to template sections ──
    section_mapping = {
        "identifiers": "Identifiers",
        "citation": "Citation Details",
        "content": "Paper Content",
        "figures": "Figures & Tables",
        "references": "References",
        "associated": "Associated Materials",
    }

    for section_id, section_title in section_mapping.items():
        section_data = data.get(section_id, {})
        if not section_data or section_id.startswith("_"):
            continue

        fields = []
        for field_id, value in section_data.items():
            if field_id.startswith("_"):
                continue

            field_type = infer_field_type(value)

            # Special handling for known fields
            if field_id in ("doi", "pmid", "pmcid", "arxiv_id", "bibtex_key"):
                field_type = "text"
            elif field_id in ("url",):
                field_type = "url"
            elif field_id in ("email", "corresponding_email"):
                field_type = "email"
            elif field_id in ("reference_count",):
                field_type = "number"
            elif field_id in ("references_bib",):
                field_type = "file"
            elif field_id == "sections":
                field_type = "textarea"
            elif field_id in (
                "figure_list",
                "table_list",
                "code_repositories",
                "data_repositories",
            ):
                field_type = "textarea"

            label = field_id.replace("_", " ").title()
            is_required = field_id in (
                "title",
                "authors",
                "abstract",
                "year",
                "sections",
            )

            field_def = {
                "id": field_id,
                "label": label,
                "type": field_type,
                "required": is_required,
            }

            if include_content_hints and value:
                val_str = str(value)
                if len(val_str) > 100:
                    field_def["hint"] = f"Detected content: {val_str[:100]}..."
                else:
                    field_def["hint"] = f"Detected content: {val_str}"

            fields.append(field_def)

        if fields:
            template["sections"].append(
                {
                    "id": section_id,
                    "title": section_title,
                    "fields": fields,
                }
            )

    # ── Also generate from actual paper sections ──
    content_data = data.get("content", {})
    sections_json = content_data.get("sections")
    if sections_json:
        try:
            paper_sections = json.loads(sections_json)
            if paper_sections:
                section_fields = []
                for ps in paper_sections:
                    name = ps.get("name", "")
                    if name.lower() in ("references", "bibliography"):
                        continue  # Already handled
                    field_id = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
                    section_fields.append(
                        {
                            "id": field_id,
                            "label": name,
                            "type": "section",
                            "required": False,
                        }
                    )

                if section_fields:
                    template["sections"].append(
                        {
                            "id": "paper_sections",
                            "title": "Paper Sections (Detected)",
                            "note": "Auto-detected sections from the document structure",
                            "fields": section_fields,
                        }
                    )
        except (json.JSONDecodeError, TypeError):
            pass

    return template


def main():
    parser = argparse.ArgumentParser(
        description="Generate _template.yml from a document (reverse template generation)",
    )
    parser.add_argument("input", help="Input file path")
    parser.add_argument("-f", "--format", help="Force input format")
    parser.add_argument(
        "-o",
        "--output",
        default="_template.yml",
        help="Output path (default: _template.yml)",
    )
    parser.add_argument(
        "--name", default="Auto-Generated Template", help="Template name"
    )
    parser.add_argument(
        "--include-content",
        action="store_true",
        help="Include detected content as hints",
    )
    args = parser.parse_args()

    fmt = args.format or detect_format(args.input)
    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    extractors = {
        "pdf": extract_pdf,
        "docx": extract_docx,
        "latex": extract_latex,
        "markdown": extract_markdown,
    }

    if fmt not in extractors:
        print(f"ERROR: Unsupported format '{fmt}'", file=sys.stderr)
        sys.exit(1)

    print(f"→ Analyzing: {args.input} (format: {fmt})", file=sys.stderr)
    data = extractors[fmt](args.input, output_dir)

    template = content_to_template(
        data,
        template_name=args.name,
        source=args.input,
        include_content_hints=args.include_content,
    )

    with open(args.output, "w") as f:
        yaml.dump(
            template,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )

    print(f"✓ Template generated: {args.output}", file=sys.stderr)

    # Report stats
    total_fields = sum(len(s.get("fields", [])) for s in template.get("sections", []))
    total_sections = len(template.get("sections", []))
    print(
        f"  {total_sections} sections, {total_fields} fields detected", file=sys.stderr
    )


if __name__ == "__main__":
    main()
