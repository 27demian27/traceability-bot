import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from typing import List, Tuple, Dict

def build_similarity_graph(requirements: List[Dict], 
                           functions: List[Dict], 
                           similarities: List[Tuple[str, List[Tuple[str, float]]]], 
                           threshold: float = 0.3) -> nx.Graph:
    G = nx.Graph()

    # Requirement nodes
    for req in requirements:
        G.add_node(req['id'], label=req['id'], type='requirement', description=req.get('description', ''))

    print(functions)
    # Function nodes
    for func in functions:
        nodetype = 'function'
        if(func['type'] == "arrow_function"):
            continue
        if "test" in func['name']:
            nodetype = 'test'
        G.add_node(func['name'], label=func['name'], type=nodetype, code=func.get('code', ''))

    # Edges based on similarity threshold
    for req_id, matches in similarities:
        for func_name, score in matches:
            if score >= threshold:
                G.add_edge(req_id, func_name, weight=round(score, 3), label=f"{score:.2f}")

    return G


def draw_graph(G: nx.Graph, filename='graph.png'):
    pos = nx.spring_layout(G, seed=42, k=1.5)

    req_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'requirement']
    func_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'function']
    test_func_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'test']

    plt.figure(figsize=(20, 15))
    
    nx.draw_networkx_nodes(G, pos, nodelist=req_nodes, node_color='red', label='Requirements')
    nx.draw_networkx_nodes(G, pos, nodelist=func_nodes, node_color='skyblue', label='Functions')
    nx.draw_networkx_nodes(G, pos, nodelist=test_func_nodes, node_color='lightgreen', label='Tests')
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=9)
    
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.title("Requirement-Test Similarity Graph")
    plt.legend()
    plt.axis('off')
    plt.tight_layout()

    plt.savefig(filename, format='png', dpi=300)
    plt.close()

