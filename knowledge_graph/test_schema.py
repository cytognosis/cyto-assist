from pathlib import Path

import yaml
from loguru import logger

SCHEMA_PATH = Path("schema-config.yaml")

def validate_schema():
    logger.info(f"Validating {SCHEMA_PATH}")
    if not SCHEMA_PATH.exists():
        logger.error(f"{SCHEMA_PATH} is missing!")
        return

    try:
        with open(SCHEMA_PATH) as f:
            schema = yaml.safe_load(f)

        node_count = sum(1 for k, v in schema.items() if isinstance(v, dict) and v.get("represented_as") == "node")
        edge_count = sum(1 for k, v in schema.items() if isinstance(v, dict) and v.get("represented_as") == "edge")

        logger.success(f"Schema loaded successfully! Nodes: {node_count}, Edges: {edge_count}")

    except Exception as e:
        logger.error(f"Failed to parse YAML schema: {e}")

if __name__ == "__main__":
    validate_schema()
