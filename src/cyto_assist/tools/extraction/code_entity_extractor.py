#!/usr/bin/env python3
"""Code Entity Extractor — Extract and assess code repositories from papers.

Gathers metadata about code repositories linked from papers: license,
languages, ML frameworks, documentation, quality metrics.

Usage:
    python code_entity_extractor.py extract --url "https://github.com/user/repo"
    python code_entity_extractor.py batch --input repos.txt --output code_entities.json
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

import requests

GITHUB_API = "https://api.github.com"

# ML/DL framework patterns in requirements/imports
ML_FRAMEWORKS = {
    "pytorch": ["torch", "pytorch"],
    "tensorflow": ["tensorflow", "tf"],
    "jax": ["jax", "flax"],
    "scikit-learn": ["sklearn", "scikit-learn"],
    "pytorch-lightning": ["pytorch_lightning", "lightning"],
    "pytorch-geometric": ["torch_geometric", "pyg"],
    "huggingface": ["transformers", "huggingface"],
    "keras": ["keras"],
    "xgboost": ["xgboost"],
    "lightgbm": ["lightgbm"],
}


def extract_github_metadata(repo_url: str) -> dict[str, Any]:
    """Extract metadata from a GitHub repository.

    Args:
        repo_url: GitHub URL (e.g., https://github.com/user/repo)

    Returns:
        Dict with license, languages, stars, etc.
    """
    result: dict[str, Any] = {
        "url": repo_url,
        "platform": "github",
        "license": None,
        "languages": {},
        "stars": 0,
        "forks": 0,
        "last_commit": None,
        "contributors_count": 0,
        "ml_frameworks": [],
        "has_readme": False,
        "has_docs": False,
        "has_tests": False,
        "has_docker": False,
        "quality_score": 0.0,
    }

    # Parse owner/repo
    match = re.search(r"github\.com/([^/]+)/([^/\s]+)", repo_url)
    if not match:
        result["error"] = "Invalid GitHub URL"
        return result

    owner, repo = match.group(1), match.group(2).rstrip("/")
    result["owner"] = owner
    result["repo"] = repo

    headers = {"Accept": "application/vnd.github.v3+json"}

    # Repo metadata
    try:
        resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}",
            headers=headers,
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            result["stars"] = data.get("stargazers_count", 0)
            result["forks"] = data.get("forks_count", 0)
            result["last_commit"] = data.get("pushed_at", "")[:10]
            result["description"] = data.get("description", "")

            lic = data.get("license")
            if lic:
                result["license"] = lic.get("spdx_id") or lic.get("name")
    except Exception as e:
        result["error"] = str(e)

    # Languages
    try:
        resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/languages",
            headers=headers,
            timeout=10,
        )
        if resp.ok:
            result["languages"] = resp.json()
    except Exception:
        pass

    # Check for key files
    try:
        resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/",
            headers=headers,
            timeout=10,
        )
        if resp.ok:
            files = [f["name"].lower() for f in resp.json() if isinstance(f, dict)]
            result["has_readme"] = any("readme" in f for f in files)
            result["has_docker"] = any("dockerfile" in f or "docker-compose" in f for f in files)
            result["has_tests"] = any(
                f in ("tests", "test", "pytest.ini", "tox.ini")
                for f in files
            )
            result["has_docs"] = any(
                f in ("docs", "documentation", "readthedocs.yml",
                      ".readthedocs.yml")
                for f in files
            )

            # Check for ML frameworks in requirements
            req_files = [
                f for f in files
                if "requirement" in f
                or f == "setup.py"
                or f == "pyproject.toml"
            ]
            if req_files:
                for req_file in req_files[:2]:
                    try:
                        resp2 = requests.get(
                            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{req_file}",
                            headers={**headers, "Accept": "application/vnd.github.v3.raw"},
                            timeout=10,
                        )
                        if resp2.ok:
                            content = resp2.text.lower()
                            for framework, patterns in ML_FRAMEWORKS.items():
                                if any(p in content for p in patterns):
                                    result["ml_frameworks"].append(framework)
                    except Exception:
                        pass
    except Exception:
        pass

    # Quality score
    score = 0.0
    if result["stars"] > 100:
        score += 0.2
    elif result["stars"] > 10:
        score += 0.1
    if result["has_readme"]:
        score += 0.2
    if result["has_tests"]:
        score += 0.2
    if result["has_docs"]:
        score += 0.15
    if result["has_docker"]:
        score += 0.1
    if result["license"]:
        score += 0.15
    result["quality_score"] = round(min(score, 1.0), 2)

    return result


# ── CLI ──────────────────────────────────────────────────────────────


def cmd_extract(args: list[str]) -> int:
    """Extract code entity metadata."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract code entity")
    parser.add_argument("--url", "-u", required=True, help="Repository URL")
    parser.add_argument("--output", help="Output JSON")
    parsed = parser.parse_args(args)

    result = extract_github_metadata(parsed.url)

    print(f"\n  Repository: {result.get('owner', '')}/{result.get('repo', '')}")
    print(f"  License: {result.get('license', 'Unknown')}")
    print(f"  Stars: {result.get('stars', 0):,}")
    print(f"  Forks: {result.get('forks', 0):,}")
    print(f"  Languages: {result.get('languages', {})}")
    print(f"  ML Frameworks: {result.get('ml_frameworks', [])}")
    print(f"  README: {'✅' if result.get('has_readme') else '❌'}")
    print(f"  Tests: {'✅' if result.get('has_tests') else '❌'}")
    print(f"  Docs: {'✅' if result.get('has_docs') else '❌'}")
    print(f"  Docker: {'✅' if result.get('has_docker') else '❌'}")
    print(f"  Quality: {result.get('quality_score', 0)}")

    if parsed.output:
        with open(parsed.output, "w") as f:
            json.dump(result, f, indent=2)

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: code_entity_extractor.py <command> [args]")
        print("Commands: extract")
        return 1

    commands = {"extract": cmd_extract}
    command = sys.argv[1]
    if command not in commands:
        return 1
    return commands[command](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
