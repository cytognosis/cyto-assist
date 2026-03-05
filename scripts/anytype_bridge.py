#!/usr/bin/env python3
"""Bidirectional sync between AnyType objects and Markdown files with YAML frontmatter.

This bridge enables the AnyType personal KG to coexist with our markdown-based
pipeline (git-tracked, LLM-compatible, template-engine-ready).

Architecture:
    AnyType (object store) <--> Bridge <--> Markdown (file store)

Each AnyType object maps to a markdown file:
    - YAML frontmatter: object metadata and properties
    - Markdown body: object content

Usage:
    python3 anytype_bridge.py export --space research    # AnyType → Markdown
    python3 anytype_bridge.py import --space research    # Markdown → AnyType
    python3 anytype_bridge.py sync --space research      # Bidirectional sync
    python3 anytype_bridge.py status                     # Show sync state
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_API_BASE = "http://127.0.0.1:31009"
DEFAULT_API_VERSION = "2025-11-08"
DEFAULT_OUTPUT_DIR = Path.home() / "knowledge"
SYNC_STATE_DIR = ".bridge"
SYNC_STATE_FILE = "sync_state.json"
CONFLICT_LOG_FILE = "conflict_log.json"

# Map AnyType type keys to output subdirectories
TYPE_DIR_MAP: dict[str, str] = {
    "paper": "papers",
    "author": "authors",
    "method": "methods",
    "note": "notes",
    "page": "pages",
    "task": "tasks",
    "bookmark": "bookmarks",
}

# Properties to exclude from YAML (system-managed)
SYSTEM_PROPERTIES = {
    "creator",
    "created_date",
    "last_modified_date",
    "last_modified_by",
    "backlinks",
    "links",
}

logger = logging.getLogger("anytype_bridge")


# ---------------------------------------------------------------------------
# AnyType API Client
# ---------------------------------------------------------------------------


class AnyTypeClient:
    """Thin wrapper around the AnyType REST API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_API_BASE,
        api_version: str = DEFAULT_API_VERSION,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Anytype-Version": api_version,
                "Content-Type": "application/json",
            }
        )
        self.session.timeout = 30

    def _get(self, path: str, **params: Any) -> dict:
        resp = self.session.get(f"{self.base_url}{path}", params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, data: dict | None = None) -> dict:
        resp = self.session.post(f"{self.base_url}{path}", json=data or {})
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path: str, data: dict) -> dict:
        resp = self.session.patch(f"{self.base_url}{path}", json=data)
        resp.raise_for_status()
        return resp.json()

    # -- Spaces --

    def list_spaces(self) -> list[dict]:
        result = self._get("/v1/spaces")
        return result.get("data", [])

    def find_space(self, name: str) -> dict | None:
        for space in self.list_spaces():
            if space["name"].lower() == name.lower():
                return space
        return None

    # -- Types --

    def list_types(self, space_id: str) -> list[dict]:
        result = self._get(f"/v1/spaces/{space_id}/types")
        return result.get("data", [])

    # -- Objects --

    def list_objects(
        self, space_id: str, limit: int = 100, offset: int = 0
    ) -> dict:
        return self._get(
            f"/v1/spaces/{space_id}/objects",
            limit=limit,
            offset=offset,
        )

    def get_object(self, space_id: str, object_id: str) -> dict:
        result = self._get(
            f"/v1/spaces/{space_id}/objects/{object_id}",
            format="md",
        )
        return result.get("object", result)

    def create_object(self, space_id: str, data: dict) -> dict:
        result = self._post(f"/v1/spaces/{space_id}/objects", data)
        return result.get("object", result)

    def update_object(
        self, space_id: str, object_id: str, data: dict
    ) -> dict:
        result = self._patch(
            f"/v1/spaces/{space_id}/objects/{object_id}", data
        )
        return result.get("object", result)

    def search_space(
        self, space_id: str, query: str = "", types: list[str] | None = None
    ) -> list[dict]:
        payload: dict[str, Any] = {"query": query}
        if types:
            payload["types"] = types
        result = self._post(f"/v1/spaces/{space_id}/search", payload)
        return result.get("data", [])

    def get_all_objects(self, space_id: str) -> list[dict]:
        """Fetch all objects with pagination."""
        all_objects: list[dict] = []
        offset = 0
        while True:
            result = self.list_objects(space_id, limit=100, offset=offset)
            data = result.get("data", [])
            all_objects.extend(data)
            pagination = result.get("pagination", {})
            if not pagination.get("has_more", False):
                break
            offset += len(data)
        return all_objects


# ---------------------------------------------------------------------------
# Markdown <-> AnyType Conversion
# ---------------------------------------------------------------------------


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80].strip("-")


def object_to_filename(obj: dict) -> str:
    """Generate a filename from an AnyType object."""
    name = obj.get("name", "untitled")
    type_key = obj.get("type", {}).get("key", "page")

    # Use citation_key for papers if available
    if type_key == "paper":
        for prop in obj.get("properties", []):
            if prop.get("key") == "citation_key" and prop.get("text"):
                return f"{prop['text']}.md"

    # Use ORCID for authors if available
    if type_key == "author":
        orcid = None
        for prop in obj.get("properties", []):
            if prop.get("key") == "orcid" and prop.get("text"):
                orcid = prop["text"]
        if orcid:
            return f"{slugify(name)}_{orcid}.md"

    # Use ontology_id for methods if available
    if type_key == "method":
        for prop in obj.get("properties", []):
            if prop.get("key") == "ontology_id" and prop.get("text"):
                ont_id = prop["text"].replace(":", "-")
                return f"{slugify(name)}_{ont_id}.md"

    return f"{slugify(name)}.md"


def extract_properties(obj: dict) -> dict[str, Any]:
    """Extract user-facing properties from an AnyType object."""
    props: dict[str, Any] = {}
    for prop in obj.get("properties", []):
        key = prop.get("key", "")
        if key in SYSTEM_PROPERTIES:
            continue

        fmt = prop.get("format", "")
        if fmt == "text" and prop.get("text") is not None:
            props[key] = prop["text"]
        elif fmt == "number" and prop.get("number") is not None:
            props[key] = prop["number"]
        elif fmt == "url" and prop.get("url") is not None:
            props[key] = prop["url"]
        elif fmt == "email" and prop.get("email") is not None:
            props[key] = prop["email"]
        elif fmt == "phone" and prop.get("phone") is not None:
            props[key] = prop["phone"]
        elif fmt == "checkbox" and prop.get("checkbox") is not None:
            props[key] = prop["checkbox"]
        elif fmt == "date" and prop.get("date") is not None:
            props[key] = prop["date"]
        elif fmt == "select" and prop.get("select") is not None:
            props[key] = prop["select"]
        elif fmt == "multi_select" and prop.get("multi_select") is not None:
            props[key] = prop["multi_select"]
        elif fmt == "objects" and prop.get("objects") is not None:
            props[key] = prop["objects"]

    return props


def object_to_markdown(obj: dict, space_name: str = "") -> str:
    """Convert an AnyType object to markdown with YAML frontmatter."""
    # Build frontmatter
    fm: dict[str, Any] = {
        "anytype_id": obj.get("id", ""),
        "anytype_type": obj.get("type", {}).get("key", "page"),
        "anytype_space": space_name,
        "last_synced": datetime.now(UTC).isoformat(),
    }

    # Add name
    if obj.get("name"):
        fm["title"] = obj["name"]

    # Add icon
    icon = obj.get("icon")
    if icon and icon.get("format") == "emoji":
        fm["icon"] = icon["emoji"]

    # Add user properties
    props = extract_properties(obj)
    fm.update(props)

    # Build YAML
    yaml_str = yaml.dump(
        fm, default_flow_style=False, allow_unicode=True, sort_keys=False
    )

    # Get markdown body
    body = obj.get("markdown", "")
    # Clean up extra trailing whitespace from AnyType
    if body:
        lines = body.split("\n")
        body = "\n".join(line.rstrip() for line in lines).strip()

    return f"---\n{yaml_str}---\n\n{body}\n"


def parse_markdown_file(path: Path) -> tuple[dict, str]:
    """Parse a markdown file into YAML frontmatter dict and body string."""
    content = path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()

    return frontmatter, body


def markdown_to_object_data(
    frontmatter: dict, body: str
) -> dict[str, Any]:
    """Convert YAML frontmatter + body into AnyType create/update payload."""
    data: dict[str, Any] = {}

    if "title" in frontmatter:
        data["name"] = frontmatter["title"]

    if "anytype_type" in frontmatter:
        data["type_key"] = frontmatter["anytype_type"]

    if "icon" in frontmatter:
        data["icon"] = {"format": "emoji", "emoji": frontmatter["icon"]}

    if body:
        data["body"] = body

    # Build properties list
    skip_keys = {
        "anytype_id",
        "anytype_type",
        "anytype_space",
        "last_synced",
        "title",
        "icon",
    }
    properties = []
    for key, value in frontmatter.items():
        if key in skip_keys:
            continue

        prop: dict[str, Any] = {"key": key}
        if isinstance(value, bool):
            prop["checkbox"] = value
        elif isinstance(value, int | float):
            prop["number"] = value
        elif isinstance(value, str):
            # Heuristic: URLs, emails, dates
            if value.startswith("http://") or value.startswith("https://"):
                prop["url"] = value
            elif "@" in value and "." in value:
                prop["email"] = value
            else:
                prop["text"] = value
        elif isinstance(value, list):
            prop["multi_select"] = value

        if len(prop) > 1:  # Has more than just "key"
            properties.append(prop)

    if properties:
        data["properties"] = properties

    return data


# ---------------------------------------------------------------------------
# Sync State Management
# ---------------------------------------------------------------------------


class SyncState:
    """Track sync timestamps for bidirectional conflict resolution."""

    def __init__(self, output_dir: Path) -> None:
        self.state_dir = output_dir / SYNC_STATE_DIR
        self.state_file = self.state_dir / SYNC_STATE_FILE
        self.conflict_file = self.state_dir / CONFLICT_LOG_FILE
        self.state: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self.state_file.exists():
            self.state = json.loads(
                self.state_file.read_text(encoding="utf-8")
            )

    def save(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(
            json.dumps(self.state, indent=2, default=str) + "\n",
            encoding="utf-8",
        )

    def get_last_sync(self, anytype_id: str) -> str | None:
        entry = self.state.get(anytype_id)
        return entry.get("last_synced") if entry else None

    def update(
        self, anytype_id: str, filepath: str, direction: str
    ) -> None:
        self.state[anytype_id] = {
            "filepath": filepath,
            "last_synced": datetime.now(UTC).isoformat(),
            "direction": direction,
        }

    def log_conflict(
        self,
        anytype_id: str,
        filepath: str,
        resolution: str,
    ) -> None:
        conflicts = []
        if self.conflict_file.exists():
            conflicts = json.loads(
                self.conflict_file.read_text(encoding="utf-8")
            )
        conflicts.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "anytype_id": anytype_id,
                "filepath": filepath,
                "resolution": resolution,
            }
        )
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.conflict_file.write_text(
            json.dumps(conflicts, indent=2) + "\n", encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# Bridge Operations
# ---------------------------------------------------------------------------


def export_space(
    client: AnyTypeClient,
    space_id: str,
    space_name: str,
    output_dir: Path,
    type_filter: list[str] | None = None,
) -> int:
    """Export AnyType objects to markdown files."""
    sync = SyncState(output_dir)
    objects = client.get_all_objects(space_id)
    exported = 0

    for obj_summary in objects:
        type_key = obj_summary.get("type", {}).get("key", "page")

        # Skip system types
        if type_key in ("template", "participant", "set", "collection"):
            continue

        # Apply type filter
        if type_filter and type_key not in type_filter:
            continue

        # Fetch full object with markdown body
        obj = client.get_object(space_id, obj_summary["id"])

        # Determine output path
        subdir = TYPE_DIR_MAP.get(type_key, "other")
        dir_path = output_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)

        filename = object_to_filename(obj)
        filepath = dir_path / filename

        # Convert and write
        md_content = object_to_markdown(obj, space_name)
        filepath.write_text(md_content, encoding="utf-8")

        # Update sync state
        sync.update(
            obj["id"],
            str(filepath.relative_to(output_dir)),
            "export",
        )
        exported += 1
        logger.info("Exported: %s → %s", obj.get("name", "?"), filepath)

    sync.save()
    return exported


def import_to_space(
    client: AnyTypeClient,
    space_id: str,
    output_dir: Path,
) -> int:
    """Import markdown files to AnyType objects."""
    sync = SyncState(output_dir)
    imported = 0

    for md_file in output_dir.rglob("*.md"):
        # Skip bridge state files
        if SYNC_STATE_DIR in str(md_file):
            continue

        frontmatter, body = parse_markdown_file(md_file)
        if not frontmatter:
            logger.warning("No frontmatter in %s, skipping", md_file)
            continue

        anytype_id = frontmatter.get("anytype_id")
        data = markdown_to_object_data(frontmatter, body)

        if anytype_id:
            # Update existing object
            try:
                update_payload: dict[str, Any] = {}
                if "name" in data:
                    update_payload["name"] = data["name"]
                if "body" in data:
                    update_payload["markdown"] = data["body"]
                if "icon" in data:
                    update_payload["icon"] = data["icon"]
                if "properties" in data:
                    update_payload["properties"] = data["properties"]

                client.update_object(space_id, anytype_id, update_payload)
                sync.update(
                    anytype_id,
                    str(md_file.relative_to(output_dir)),
                    "import",
                )
                imported += 1
                logger.info(
                    "Updated: %s → %s",
                    md_file.name,
                    frontmatter.get("title", "?"),
                )
            except requests.HTTPError as e:
                logger.error("Failed to update %s: %s", anytype_id, e)
        else:
            # Create new object
            if "type_key" not in data:
                # Infer type from directory
                parent = md_file.parent.name
                reverse_map = {v: k for k, v in TYPE_DIR_MAP.items()}
                data["type_key"] = reverse_map.get(parent, "page")

            try:
                result = client.create_object(space_id, data)
                new_id = result.get("id", "")

                # Update the file with the new AnyType ID
                frontmatter["anytype_id"] = new_id
                frontmatter["last_synced"] = datetime.now(
                    UTC
                ).isoformat()
                new_content = object_to_markdown(
                    {
                        "id": new_id,
                        "name": data.get("name", ""),
                        "type": {"key": data.get("type_key", "page")},
                        "icon": data.get("icon"),
                        "properties": [],
                        "markdown": body,
                    },
                    frontmatter.get("anytype_space", ""),
                )
                md_file.write_text(new_content, encoding="utf-8")

                sync.update(
                    new_id,
                    str(md_file.relative_to(output_dir)),
                    "import",
                )
                imported += 1
                logger.info(
                    "Created: %s → %s", md_file.name, data.get("name", "?")
                )
            except requests.HTTPError as e:
                logger.error("Failed to create from %s: %s", md_file, e)

    sync.save()
    return imported


def show_status(output_dir: Path) -> None:
    """Display sync status."""
    sync = SyncState(output_dir)
    if not sync.state:
        print("No sync state found. Run export or import first.")
        return

    print(f"Synced objects: {len(sync.state)}")
    print(f"Output dir: {output_dir}")
    print()

    for _anytype_id, info in sorted(
        sync.state.items(), key=lambda x: x[1].get("filepath", "")
    ):
        filepath = info.get("filepath", "?")
        last_sync = info.get("last_synced", "?")
        direction = info.get("direction", "?")
        print(f"  {direction:6s} | {filepath:50s} | {last_sync[:19]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def load_api_key() -> str:
    """Load API key from central MCP config."""
    config_paths = [
        Path.home() / ".agents" / "mcp.json",
        Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
    ]

    for path in config_paths:
        if not path.exists():
            continue
        try:
            config = json.loads(path.read_text())
            headers_str = (
                config.get("mcpServers", {})
                .get("anytype", {})
                .get("env", {})
                .get("OPENAPI_MCP_HEADERS", "")
            )
            if headers_str:
                headers = json.loads(headers_str)
                auth = headers.get("Authorization", "")
                if auth.startswith("Bearer "):
                    return auth[7:]
        except (json.JSONDecodeError, KeyError):
            continue

    print(
        "Error: No API key found. Set in ~/.agents/mcp.json or pass --api-key",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="AnyType ↔ Markdown bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--api-key",
        help="AnyType API key (default: from ~/.agents/mcp.json)",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_API_BASE,
        help=f"API base URL (default: {DEFAULT_API_BASE})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # export
    p_export = sub.add_parser("export", help="AnyType → Markdown")
    p_export.add_argument(
        "--space", required=True, help="Space name to export"
    )
    p_export.add_argument(
        "--types",
        nargs="+",
        help="Filter by type keys (e.g. paper author method)",
    )

    # import
    p_import = sub.add_parser("import", help="Markdown → AnyType")
    p_import.add_argument(
        "--space", required=True, help="Space name to import into"
    )

    # sync
    p_sync = sub.add_parser("sync", help="Bidirectional sync")
    p_sync.add_argument("--space", required=True, help="Space name")
    p_sync.add_argument(
        "--types",
        nargs="+",
        help="Filter by type keys",
    )

    # status
    sub.add_parser("status", help="Show sync status")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    api_key = args.api_key or load_api_key()
    client = AnyTypeClient(api_key, args.base_url)

    if args.command == "status":
        show_status(args.output_dir)
        return

    # Find space
    space = client.find_space(args.space)
    if not space:
        available = [s["name"] for s in client.list_spaces()]
        print(
            f"Error: Space '{args.space}' not found. "
            f"Available: {available}",
            file=sys.stderr,
        )
        sys.exit(1)

    space_id = space["id"]
    space_name = space["name"]

    if args.command == "export":
        count = export_space(
            client, space_id, space_name, args.output_dir, args.types
        )
        print(f"Exported {count} objects from '{space_name}'")

    elif args.command == "import":
        count = import_to_space(client, space_id, args.output_dir)
        print(f"Imported {count} objects to '{space_name}'")

    elif args.command == "sync":
        # Sync = export first, then import new/changed files
        export_count = export_space(
            client, space_id, space_name, args.output_dir, args.types
        )
        import_count = import_to_space(client, space_id, args.output_dir)
        print(
            f"Sync complete: {export_count} exported, "
            f"{import_count} imported"
        )


if __name__ == "__main__":
    main()
