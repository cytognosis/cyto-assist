import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")

@app.cell
def __():
    import marimo as mo
    return (mo,)

@app.cell
def __(mo):
    mo.md(
        r"""
        # Cytognosis Ontology & OLS4 Experiments

        This notebook demonstrates:
        1. Fetching OLS4 statistics from our local Neo4j.
        2. Loading standard OWL ontologies from the CellxGene schema.
        3. Converting ontologies to NetworkX graphs.
        4. Verifying cross-ontology edges (e.g. MONDO vs DOID for neuropsychiatric diseases).
        """
    )
    return

@app.cell
def __():
    import networkx as nx
    from loguru import logger

    from cyto_assist.data.ols4_client import OLS4Client
    from cyto_assist.data.owl_loader import fetch_ontology, load_ontology_to_networkx
    return OLS4Client, fetch_ontology, load_ontology_to_networkx, logger, nx

@app.cell
def __(OLS4Client, mo):
    mo.md("## Part 1: OLS4 Statistics")
    return

@app.cell
def __(OLS4Client):
    client = OLS4Client()
    stats = client.get_neo4j_stats()
    client.close()
    stats
    return client, stats

@app.cell
def __(mo):
    mo.md(
        r"""
        ## Part 2: Load OWL Ontologies
        We will load MONDO and DOID (Disease Ontology) to verify hierarchical annotations.
        """
    )
    return

@app.cell
def __(fetch_ontology, load_ontology_to_networkx):
    mondo_path = fetch_ontology("mondo")
    mondo_graph = load_ontology_to_networkx(mondo_path)
    return mondo_graph, mondo_path

@app.cell
def __(fetch_ontology, load_ontology_to_networkx):
    doid_path = fetch_ontology("doid")
    doid_graph = load_ontology_to_networkx(doid_path)
    return doid_graph, doid_path

@app.cell
def __(mo):
    mo.md(
        r"""
        ## Part 3: Cross-Ontology Verification
        We verify the specified mappings between MONDO and DO for neuropsychiatric disorders.
        These should all be descendants of MONDO:0002025 (psychiatric disorder).
        """
    )
    return

@app.cell
def __(mondo_graph, nx):
    # Test checking if a term is a descendant of MONDO:0002025 (psychiatric disorder)

    disease_pairs = [
        ("Tourette Syndrome", "MONDO:0007661", "DOID:11118"),
        ("Anorexia Nervosa", "MONDO:0005351", "DOID:8670"),
        ("Obsessive-Compulsive Disorder", "MONDO:0008114", "DOID:446"),
        ("Schizophrenia", "MONDO:0005090", "DOID:5419"),
        ("Bipolar Disorder", "MONDO:0004985", "DOID:3312")
    ]

    results = []

    for name, mondo_id, do_id in disease_pairs:
        # NetworkX is_a edges go from child -> parent
        is_descendant = False
        try:
            if nx.has_path(mondo_graph, mondo_id, "MONDO:0002025"):
                is_descendant = True
        except nx.NetworkXError:
            pass

        results.append({
            "Disease": name,
            "MONDO ID": mondo_id,
            "Is Psychiatric Subclass?": is_descendant
        })
    results
    return disease_pairs, results

if __name__ == "__main__":
    app.run()
