import json

import requests
from loguru import logger
from neo4j import GraphDatabase
from rich.console import Console
from rich.table import Table


class OLS4Client:
    """
    Client for interacting with local OLS4 Neo4j instance and external OLS4 API.
    """
    def __init__(self, neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_pass="cytognosis2025", api_url="https://www.ebi.ac.uk/ols4/api/"):
        self.api_url = api_url
        try:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
            self.driver.verify_connectivity()
            logger.success("Connected to local OLS4 Neo4j.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def get_neo4j_stats(self):
        """Query Neo4j for summary statistics of the OLS4 graph."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return None

        stats = {}
        with self.driver.session() as session:
            # Total Nodes
            res = session.run("MATCH (n) RETURN count(n) AS cnt").single()
            stats['total_nodes'] = res['cnt']

            # Total Edges
            res = session.run("MATCH ()-[r]->() RETURN count(r) AS cnt").single()
            stats['total_edges'] = res['cnt']

            # Node labels distribution
            res = session.run("""
                CALL db.labels() YIELD label
                RETURN label
            """)
            labels = [r['label'] for r in res]
            stats['node_types'] = {}
            for lbl in labels:
                c = session.run(f"MATCH (n:`{lbl}`) RETURN count(n) AS cnt").single()
                stats['node_types'][lbl] = c['cnt']

            # Edge types distribution
            res = session.run("""
                CALL db.relationshipTypes() YIELD relationshipType
                RETURN relationshipType
            """)
            rel_types = [r['relationshipType'] for r in res]
            stats['edge_types'] = {}
            for rel in rel_types:
                c = session.run(f"MATCH ()-[r:`{rel}`]->() RETURN count(r) AS cnt").single()
                stats['edge_types'][rel] = c['cnt']

            # Number of ontologies (assuming :Ontology nodes exist)
            res = session.run("MATCH (o:Ontology) RETURN count(o) AS cnt").single()
            stats['total_ontologies'] = res['cnt']
            if res['cnt'] == 0:
                # OLS4 graph format might use something else:
                res = session.run("MATCH (o:Resource) WHERE o.type = 'ontology' RETURN count(o) AS cnt").single()
                if res and res['cnt'] > 0:
                     stats['total_ontologies'] = res['cnt']

        return stats

    def get_api_stats(self):
        """Query OLS4 public API for basic statistics."""
        try:
            res = requests.get(f"{self.api_url}ontologies", params={"size": 1})
            res.raise_for_status()
            data = res.json()
            total_ontologies = data.get("page", {}).get("totalElements", 0)

            return {
                "total_ontologies": total_ontologies
            }
        except Exception as e:
            logger.error(f"Failed to query OLS4 API: {e}")
            return None

    def print_comparison(self):
        neo4j_stats = self.get_neo4j_stats()
        api_stats = self.get_api_stats()

        console = Console()
        console.print("\n[bold cyan]OLS4 Local vs Remote Statistics[/bold cyan]")

        if neo4j_stats:
            table = Table(title="Local Neo4j Graph Stats")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right", style="green")

            table.add_row("Total Nodes", f"{neo4j_stats.get('total_nodes', 0):,}")
            table.add_row("Total Edges", f"{neo4j_stats.get('total_edges', 0):,}")
            table.add_row("Total Ontologies", f"{neo4j_stats.get('total_ontologies', 0):,}")

            console.print(table)

            ntables = Table(title="Node Types (Labels)")
            ntables.add_column("Type")
            ntables.add_column("Count", justify="right")
            for k, v in sorted(neo4j_stats.get('node_types', {}).items(), key=lambda x: x[1], reverse=True)[:15]:
                ntables.add_row(k, f"{v:,}")
            console.print(ntables)

            etables = Table(title="Edge Types (Relationships)")
            etables.add_column("Type")
            etables.add_column("Count", justify="right")
            for k, v in sorted(neo4j_stats.get('edge_types', {}).items(), key=lambda x: x[1], reverse=True)[:15]:
                etables.add_row(k, f"{v:,}")
            console.print(etables)

            console.print(f"\n[yellow]Note: Displaying top 15 labels and relationships.[/yellow]")

        if api_stats:
            atable = Table(title="Public OLS4 API Stats")
            atable.add_column("Metric", style="cyan")
            atable.add_column("Value", justify="right", style="green")
            atable.add_row("Total Ontologies", f"{api_stats.get('total_ontologies', 0):,}")
            console.print(atable)

if __name__ == "__main__":
    client = OLS4Client()
    client.print_comparison()
    client.close()
