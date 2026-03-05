# Neo4j Graph Database — Comprehensive Guide

> **Version:** 1.0 | **Date:** 2026-03-03 | **Status:** Active
> **Local Installation:** Neo4j Community 2025.03.0 (Kernel 5.27.0) at `bolt://localhost:7687`

---

## 1. Architecture Overview

Neo4j is a native graph database using the **property graph model**:

| Concept | Description |
|---------|-------------|
| **Node** | Entity (vertex) with labels and properties |
| **Relationship** | Directed connection (edge) between nodes, with a type and properties |
| **Label** | Classifier for nodes (e.g., `:Person`, `:Disease`) — a node can have multiple labels |
| **Property** | Key-value pair on nodes or relationships |
| **Path** | Sequence of nodes connected by relationships |

### Storage Architecture
- **Record files**: Fixed-size records for nodes, relationships, properties, labels
- **Index-free adjacency**: Each node stores pointers to its relationships — O(1) neighbor traversal
- **ACID transactions**: Full transactional support with write-ahead logging

### Data Model Example
```
(:Paper {pmid: "12345", title: "..."})
  -[:AUTHORED_BY]-> (:Author {name: "Smith J"})
  -[:CITES]-> (:Paper {pmid: "67890"})
  -[:MENTIONS]-> (:BioEntity {id: "MONDO:0005090", name: "schizophrenia"})
```

---

## 2. Local Installation

### Our Setup
- **Edition:** Community 2025.03.0 (free, open-source, AGPL-3.0)
- **Location:** `/home/mohammadi/software/neo4j/` (symlink → `neo4j-community-2025.03.0`)
- **Java:** OpenJDK 21.0.10 (Temurin)
- **Auth:** `neo4j` / `cytognosis2025`

### Service Management
```bash
export NEO4J_HOME=/home/mohammadi/software/neo4j

# Start/stop/status
$NEO4J_HOME/bin/neo4j start
$NEO4J_HOME/bin/neo4j stop
$NEO4J_HOME/bin/neo4j status
$NEO4J_HOME/bin/neo4j console   # foreground mode

# Logs
tail -f $NEO4J_HOME/logs/neo4j.log
```

### Key Configuration (`conf/neo4j.conf`)
```properties
# Memory (adjust based on available RAM)
server.memory.heap.initial_size=512m
server.memory.heap.max_size=2g
server.memory.pagecache.size=1g

# Network
server.default_listen_address=0.0.0.0
server.bolt.listen_address=:7687
server.http.listen_address=:7474

# Data directory (change to externalize data)
server.directories.data=/home/mohammadi/software/neo4j/data
```

### Admin Commands
```bash
# Set/reset password
$NEO4J_HOME/bin/neo4j-admin dbms set-initial-password <password>

# Database dump/load
$NEO4J_HOME/bin/neo4j-admin database dump neo4j --to-path=/backup/
$NEO4J_HOME/bin/neo4j-admin database load neo4j --from-path=/backup/

# Import CSV data (bulk import)
$NEO4J_HOME/bin/neo4j-admin database import full neo4j \
  --nodes=papers.csv --relationships=citations.csv

# Migrate from 4.x to 5.x format
$NEO4J_HOME/bin/neo4j-admin database migrate neo4j
```

---

## 3. Cypher Query Language

Cypher is Neo4j's declarative graph query language (GQL-conformant via openCypher).

### Pattern Matching
```cypher
// Find all papers by an author
MATCH (a:Author {name: "Smith J"})<-[:AUTHORED_BY]-(p:Paper)
RETURN p.title, p.year ORDER BY p.year DESC

// Find 2-hop citation paths
MATCH path = (p1:Paper)-[:CITES*2]->(p3:Paper)
WHERE p1.pmid = "12345"
RETURN path

// Find diseases mentioned in papers with high citations
MATCH (p:Paper)-[:MENTIONS]->(d:Disease)
WHERE p.cited_count > 100
RETURN d.name, count(p) AS paper_count
ORDER BY paper_count DESC LIMIT 20
```

### CRUD Operations
```cypher
// Create
CREATE (p:Paper {pmid: "12345", title: "My Paper", year: 2024})
CREATE (a:Author {name: "Smith J"})
CREATE (p)-[:AUTHORED_BY]->(a)

// Read
MATCH (p:Paper) WHERE p.pmid = "12345" RETURN p

// Update
MATCH (p:Paper {pmid: "12345"})
SET p.cited_count = 42, p.last_updated = datetime()

// Delete (must delete relationships first)
MATCH (p:Paper {pmid: "12345"})-[r]-()
DELETE r, p
```

### Aggregation & Graph Algorithms
```cypher
// Degree distribution
MATCH (p:Paper)-[r:CITES]->()
RETURN p.pmid, count(r) AS out_degree
ORDER BY out_degree DESC LIMIT 10

// Shortest path
MATCH path = shortestPath(
  (p1:Paper {pmid: "111"})-[:CITES*..10]-(p2:Paper {pmid: "999"})
)
RETURN path, length(path)

// Community detection via connected components
CALL gds.wcc.stream('myGraph')
YIELD nodeId, componentId
RETURN gds.util.asNode(nodeId).name AS name, componentId
ORDER BY componentId
```

### Indexes & Constraints
```cypher
// Create index for faster lookups
CREATE INDEX paper_pmid FOR (p:Paper) ON (p.pmid)
CREATE INDEX disease_mondo FOR (d:Disease) ON (d.mondo_id)

// Unique constraint
CREATE CONSTRAINT unique_pmid FOR (p:Paper) REQUIRE p.pmid IS UNIQUE

// Show indexes
SHOW INDEXES
```

---

## 4. Python Driver (`neo4j` package)

### Installation
```bash
pip install neo4j   # Current: v6.1.0
```

### Connection & Basic Queries
```python
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "cytognosis2025")

# Context manager pattern (recommended)
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    # Simple query
    records, summary, keys = driver.execute_query(
        "MATCH (p:Paper) RETURN p.title AS title LIMIT 10"
    )
    for record in records:
        print(record["title"])

    # Parameterized query (always use parameters, never string concat!)
    records, _, _ = driver.execute_query(
        "MATCH (p:Paper {pmid: $pmid}) RETURN p",
        pmid="12345"
    )
```

### Session-Based Transactions
```python
def create_paper(tx, pmid, title, year):
    tx.run(
        "CREATE (p:Paper {pmid: $pmid, title: $title, year: $year})",
        pmid=pmid, title=title, year=year
    )

with driver.session() as session:
    # Write transaction (auto-retry on transient errors)
    session.execute_write(create_paper, "12345", "My Paper", 2024)

    # Read transaction
    result = session.execute_read(
        lambda tx: tx.run("MATCH (p:Paper) RETURN count(p) AS cnt").single()
    )
    print(f"Total papers: {result['cnt']}")
```

### Batch Import Pattern
```python
def batch_create_papers(tx, papers: list[dict]):
    tx.run(
        """
        UNWIND $papers AS paper
        CREATE (p:Paper)
        SET p = paper
        """,
        papers=papers
    )

# Process in chunks
BATCH_SIZE = 5000
for i in range(0, len(all_papers), BATCH_SIZE):
    chunk = all_papers[i:i + BATCH_SIZE]
    with driver.session() as session:
        session.execute_write(batch_create_papers, chunk)
```

### NetworkX Integration
```python
import networkx as nx

def neo4j_to_networkx(driver, query):
    """Export Neo4j subgraph to NetworkX."""
    G = nx.DiGraph()
    records, _, _ = driver.execute_query(query)
    for record in records:
        # Assuming query returns source, target, relationship info
        G.add_edge(
            record["source_id"],
            record["target_id"],
            type=record["rel_type"]
        )
    return G

# Example: citation network
G = neo4j_to_networkx(driver, """
    MATCH (p1:Paper)-[r:CITES]->(p2:Paper)
    RETURN p1.pmid AS source_id, p2.pmid AS target_id, type(r) AS rel_type
    LIMIT 10000
""")
print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
```

---

## 5. Neo4j MCP Server

The Neo4j MCP server enables AI agents to query Neo4j directly.

### Setup
```bash
# Install via npm
npm install -g @neo4j/mcp-server

# Or configure in MCP settings
{
  "mcpServers": {
    "neo4j": {
      "command": "npx",
      "args": ["-y", "@neo4j/mcp-server"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "cytognosis2025"
      }
    }
  }
}
```

### Available Tools
| Tool | Description |
|------|-------------|
| `read_neo4j_cypher` | Execute read-only Cypher queries |
| `write_neo4j_cypher` | Execute write Cypher queries |
| `get_neo4j_schema` | Retrieve database schema (labels, relationship types, properties) |

---

## 6. Database Migration (4.x → 5.x)

The OLS4 Neo4j dump uses legacy `neostore.*` format (Neo4j 4.x). To use with 5.x:

```bash
# Stop Neo4j
$NEO4J_HOME/bin/neo4j stop

# Copy legacy database files to data/databases/<dbname>/
cp -r /path/to/legacy/neo4j/* $NEO4J_HOME/data/databases/ols4/

# Run migration
$NEO4J_HOME/bin/neo4j-admin database migrate ols4

# Register the database
# In cypher-shell:
CREATE DATABASE ols4

# Start Neo4j
$NEO4J_HOME/bin/neo4j start
```

> **Note:** Community Edition only supports a single active database (`neo4j`). To use the OLS4 database, you may need to replace the default `neo4j` database or upgrade to Enterprise for multi-database support.

---

## 7. Best Practices

1. **Always use parameterized queries** — never concatenate strings into Cypher
2. **Index properties used in WHERE/MATCH** — especially IDs like pmid, mondo_id
3. **Batch writes with UNWIND** — process thousands of records per transaction
4. **Use labels judiciously** — labels are indexes, don't over-label
5. **Profile queries** — use `EXPLAIN` and `PROFILE` to optimize
6. **Externalize data directory** — keep data separate from Neo4j binaries for easy upgrades
7. **Regular backups** — use `neo4j-admin database dump` before major operations
