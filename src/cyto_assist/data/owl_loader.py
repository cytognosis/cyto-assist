import os
from pathlib import Path
from urllib.request import urlretrieve

import networkx as nx
import pronto
from loguru import logger

ONTOLOGIES = {
    "uberon": "http://purl.obolibrary.org/obo/uberon.owl",
    "cl": "http://purl.obolibrary.org/obo/cl.owl",
    "pato": "http://purl.obolibrary.org/obo/pato.owl",
    "mondo": "http://purl.obolibrary.org/obo/mondo.owl",
    "cellosaurus": "https://ftp.expasy.org/databases/cellosaurus/cellosaurus.owl",
    "doid": "http://purl.obolibrary.org/obo/doid.owl"
}

def fetch_ontology(name: str, cache_dir: str = "/home/mohammadi/datasets/ontologies") -> Path:
    """Download the specified ontology in OWL format."""
    if name not in ONTOLOGIES:
        raise ValueError(f"Unknown ontology {name}. Available: {list(ONTOLOGIES.keys())}")

    url = ONTOLOGIES[name]
    os.makedirs(cache_dir, exist_ok=True)
    filepath = Path(cache_dir) / f"{name}.owl"

    if not filepath.exists():
        logger.info(f"Downloading {name} ontology from {url}...")
        urlretrieve(url, filepath)
        logger.success(f"Downloaded {name} to {filepath}")
    else:
        logger.info(f"Using cached {name} ontology at {filepath}")

    return filepath

def load_ontology_to_networkx(filepath: Path) -> nx.DiGraph:
    """
    Parse an ontology file with pronto and convert it into a pure NetworkX DiGraph.
    Nodes track names and namespaces. Edges indicate 'is_a' hierarchical parents.
    """
    logger.info(f"Loading ontology with pronto: {filepath}")
    ont = pronto.Ontology(str(filepath))

    logger.info("Converting ontology to NetworkX DiGraph...")
    G = nx.DiGraph()

    for term in ont.terms():
        # Store term ID and basic attributes
        G.add_node(term.id, name=term.name, namespace=term.namespace)

        # Add is_a relationships from the term to its direct superclasses (parents)
        for parent in term.superclasses(distance=1, with_self=False):
            G.add_edge(term.id, parent.id, type="is_a")

    logger.success(f"Created NetworkX graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G

def get_ontology_graph(name: str) -> nx.DiGraph:
    """High-level function to fetch and load an ontology as a NetworkX graph."""
    filepath = fetch_ontology(name)
    return load_ontology_to_networkx(filepath)
