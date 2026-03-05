#!/usr/bin/env python3
"""
proposal_section_generator.py

A modular tool to generate or extract specific sections of a grant proposal
using Cytognosis templates and organizational constraints.

Usage:
    python proposal_section_generator.py --funder arpa-h --section "Solution Summary" --context "Microbiome sensing"
"""

import argparse
import sys


def load_funder_template(funder_name):
    # Stub for loading template configurations from materials/templates/
    templates = {
        "arpa-h": ["1. Scientific and Technical Merit", "2. Relevance to ARPA-H Mission", "3. Proposers Capabilities", "4. Budget"],
        "astera": ["Project Summary", "Technical Approach", "Team Fit", "Conviction", "Users", "Why Astera", "Scope", "Open Science"],
        "fro": ["What is the goal?", "Why FRO?", "Structural success?", "Public goods?"],
        "ea": ["Impact and scale", "Why LTFF?", "Catastrophic risks", "Track record"]
    }
    return templates.get(funder_name.lower())

def generate_section_prompt(funder, section, context):
    sections = load_funder_template(funder)
    if not sections:
        print(f"Error: Unknown funder '{funder}'. Supported: arpa-h, astera, fro, ea", file=sys.stderr)
        sys.exit(1)

    if section not in sections:
        print(f"Warning: '{section}' is not a standard section for {funder}.", file=sys.stderr)
        print(f"Standard sections are: {', '.join(sections)}")

    prompt = f"""
You are the Cytognosis Grant Writer AI.
Please draft the following specific section for a {funder.upper()} application:
**Section:** {section}

**Constraints:**
1. Ensure you incorporate the Helix Framework (The People's Equity, 15-year lifecycle) if applicable to commercialization or structural arguments.
2. Adhere to the Cytognosis values (Open Science, Health Equity, Pasteur's Quadrant).
3. Context provided by the user: {context}

Generate only this section in valid Markdown. Do not generate the entire proposal.
"""
    return prompt

def main():
    parser = argparse.ArgumentParser(description="Generate modular prompts for specific grant proposal sections.")
    parser.add_argument("--funder", required=True, help="Target funder (e.g., arpa-h, astera, fro, ea)")
    parser.add_argument("--section", required=True, help="Specific section to generate (e.g., '1. Scientific and Technical Merit')")
    parser.add_argument("--context", default="Standard Cytognosis OS framework", help="Additional context or specific technical focus")

    args = parser.parse_args()

    prompt = generate_section_prompt(args.funder, args.section, args.context)

    print("==========================================")
    print(f"GENERATED LLM PROMPT FOR {args.funder.upper()} - {args.section}")
    print("==========================================")
    print(prompt)

if __name__ == "__main__":
    main()
