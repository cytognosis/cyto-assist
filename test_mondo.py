from cyto_assist.data.owl_loader import fetch_ontology, load_ontology_to_networkx
import networkx as nx

mondo_path = fetch_ontology("mondo")
G = load_ontology_to_networkx(mondo_path)

disease_pairs = [
    ("Tourette Syndrome", "MONDO:0007661", "DOID:11118"),
    ("Anorexia Nervosa", "MONDO:0005351", "DOID:8670"),
    ("Obsessive-Compulsive Disorder", "MONDO:0008114", "DOID:446"),
    ("Major Depressive Disorder", "MONDO:0002009", "DOID:1474"),
    ("Anxiety Disorder", "MONDO:0005618", "DOID:2030")
]

print("\n--- Verification Results ---")
for name, m, d in disease_pairs:
    try:
        if nx.has_path(G, m, "MONDO:0002025"):
            print(f"✅ {name} ({m}) is a descendant of Psychiatric Disorder (MONDO:0002025).")
        else:
            print(f"❌ {name} ({m}) has NO PATH to MONDO:0002025.")
    except Exception as e:
        print(f"Error checking {m}: {e}")
