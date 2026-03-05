#!/usr/bin/env python3
"""
compare_templates.py — Cross-template analysis for similarity/difference detection.

Compares multiple _template.yml files to identify:
  - Shared questions/fields across templates (for joint answer planning)
  - Unique questions per template
  - Structural differences (sections, field types, constraints)

Usage:
  python compare_templates.py templates/qb3/_template.yml templates/nih/_template.yml
  python compare_templates.py templates/*/_template.yml -o comparison_report.md
  python compare_templates.py templates/*/_template.yml --similarity-threshold 0.6
"""

import argparse
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import yaml


def load_template(path: str) -> dict:
    """Load and parse a _template.yml file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    data["_source_path"] = str(path)
    return data


def extract_fields(template: dict) -> list[dict]:
    """Extract a flat list of fields with section context."""
    fields = []
    tmpl_name = template.get("template", {}).get(
        "name", Path(template["_source_path"]).parent.name
    )
    for section in template.get("sections", []):
        for field in section.get("fields", []):
            fields.append(
                {
                    "template": tmpl_name,
                    "section_id": section["id"],
                    "section_title": section["title"],
                    "field_id": field["id"],
                    "label": field["label"],
                    "type": field.get("type", "text"),
                    "required": field.get("required", False),
                    "constraints": field.get("constraints", {}),
                }
            )
    return fields


def label_similarity(a: str, b: str) -> float:
    """Compute similarity ratio between two field labels."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_similar_fields(
    all_fields: list[dict],
    threshold: float = 0.55,
) -> list[dict]:
    """Find field pairs across templates with similar labels."""
    templates = set(f["template"] for f in all_fields)
    if len(templates) < 2:
        return []

    # Group fields by template
    by_template = defaultdict(list)
    for f in all_fields:
        by_template[f["template"]].append(f)

    template_names = sorted(templates)
    matches = []

    for i, t1 in enumerate(template_names):
        for t2 in template_names[i + 1 :]:
            for f1 in by_template[t1]:
                for f2 in by_template[t2]:
                    sim = label_similarity(f1["label"], f2["label"])
                    if sim >= threshold:
                        matches.append(
                            {
                                "similarity": sim,
                                "field_a": f1,
                                "field_b": f2,
                            }
                        )

    matches.sort(key=lambda m: m["similarity"], reverse=True)
    return matches


def generate_report(templates: list[dict], threshold: float = 0.55) -> str:
    """Generate a full Markdown comparison report."""
    all_fields = []
    for t in templates:
        all_fields.extend(extract_fields(t))

    tmpl_names = [t.get("template", {}).get("name", "?") for t in templates]
    lines = []

    # ── Header ──
    lines.append("# Cross-Template Comparison Report\n")
    lines.append(
        f"> Comparing {len(templates)} templates | Similarity threshold: {threshold:.0%}\n"
    )
    lines.append("---\n")

    # ── Template Summary ──
    lines.append("## Templates Compared\n")
    lines.append("| # | Template | Sections | Fields | Required |")
    lines.append("|:-:|----------|:--------:|:------:|:--------:|")
    for i, t in enumerate(templates, 1):
        meta = t.get("template", {})
        name = meta.get("name", "?")
        sections = t.get("sections", [])
        total = sum(len(s.get("fields", [])) for s in sections)
        req = sum(1 for s in sections for f in s.get("fields", []) if f.get("required"))
        lines.append(f"| {i} | **{name}** | {len(sections)} | {total} | {req} |")
    lines.append("")

    # ── Similar Fields ──
    matches = find_similar_fields(all_fields, threshold)
    if matches:
        lines.append("---\n")
        lines.append("## Similar Fields Across Templates\n")
        lines.append(
            "These field pairs have high label similarity and likely ask the same/similar question. "
            "**Plan joint, consistent answers for these.**\n"
        )
        lines.append(
            "| Similarity | Template A | Field A | Template B | Field B | Same Type? |"
        )
        lines.append(
            "|:----------:|------------|---------|------------|---------|:----------:|"
        )
        for m in matches:
            fa = m["field_a"]
            fb = m["field_b"]
            sim_pct = f"{m['similarity']:.0%}"
            same_type = (
                "✅"
                if fa["type"] == fb["type"]
                else f"❌ ({fa['type']} vs {fb['type']})"
            )
            lines.append(
                f"| {sim_pct} | {fa['template'][:25]} | {fa['label'][:50]} | "
                f"{fb['template'][:25]} | {fb['label'][:50]} | {same_type} |"
            )
        lines.append("")

    # ── Shared Themes (section-level) ──
    section_titles = defaultdict(list)
    for t in templates:
        meta = t.get("template", {})
        name = meta.get("name", "?")
        for s in t.get("sections", []):
            section_titles[s["title"].lower()].append(name)

    shared_sections = {k: v for k, v in section_titles.items() if len(v) > 1}
    if shared_sections:
        lines.append("---\n")
        lines.append("## Shared Section Themes\n")
        lines.append("| Section Title | Appears In |")
        lines.append("|---------------|------------|")
        for title, tmpl_list in sorted(shared_sections.items()):
            lines.append(f"| {title.title()} | {', '.join(tmpl_list)} |")
        lines.append("")

    # ── Unique Fields (per template) ──
    lines.append("---\n")
    lines.append("## Unique Fields Per Template\n")
    lines.append(
        "Fields that have **no match** (below threshold) in any other template.\n"
    )

    matched_keys = set()
    for m in matches:
        fa = m["field_a"]
        fb = m["field_b"]
        matched_keys.add((fa["template"], fa["section_id"], fa["field_id"]))
        matched_keys.add((fb["template"], fb["section_id"], fb["field_id"]))

    by_template = defaultdict(list)
    for f in all_fields:
        key = (f["template"], f["section_id"], f["field_id"])
        if key not in matched_keys:
            by_template[f["template"]].append(f)

    for tmpl_name, fields in by_template.items():
        lines.append(f"### {tmpl_name}\n")
        for f in fields:
            req = " *" if f["required"] else ""
            lines.append(f"- **{f['label']}**{req} (`{f['type']}`)")
        lines.append("")

    # ── Field Type Distribution ──
    lines.append("---\n")
    lines.append("## Field Type Distribution\n")
    type_counts = defaultdict(lambda: defaultdict(int))
    for f in all_fields:
        type_counts[f["template"]][f["type"]] += 1

    all_types = sorted(set(f["type"] for f in all_fields))
    header = (
        "| Template | " + " | ".join(f"`{t}`" for t in all_types) + " | **Total** |"
    )
    sep = (
        "|----------|"
        + "|".join(":" + "-" * max(len(t) + 1, 3) + ":" for t in all_types)
        + "|:---------:|"
    )
    lines.append(header)
    lines.append(sep)
    for tmpl_name in tmpl_names:
        counts = type_counts[tmpl_name]
        cells = [str(counts.get(t, 0)) for t in all_types]
        total = sum(counts.values())
        lines.append(f"| {tmpl_name[:30]} | " + " | ".join(cells) + f" | **{total}** |")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare multiple _template.yml files for cross-template analysis",
    )
    parser.add_argument(
        "templates",
        nargs="+",
        help="Paths to _template.yml files",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output Markdown report path (default: stdout)",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.55,
        help="Minimum label similarity ratio (0–1) to flag as shared (default: 0.55)",
    )
    args = parser.parse_args()

    templates = [load_template(p) for p in args.templates]
    report = generate_report(templates, threshold=args.similarity_threshold)

    if args.output:
        Path(args.output).write_text(report + "\n")
        print(f"✓ Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
