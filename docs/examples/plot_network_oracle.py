"""
Network Oracle Example
======================

Demonstrates a parametric network with an oracle for cutting-plane optimization.
"""
import matplotlib.pyplot as plt
import networkx as nx

gra = {
    "v1": {"v2": {"w": 3}, "v3": {"w": 4}},
    "v2": {"v1": {"w": -2}, "v3": {"w": 1}},
    "v3": {"v1": {"w": -3}, "v2": {"w": -2}},
}

g = nx.DiGraph()
for u, neighbors in gra.items():
    for v, attr in neighbors.items():
        g.add_edge(u, v, w=attr['w'])

plt.figure(figsize=(7, 5))
pos = nx.spring_layout(g, seed=42)
nx.draw(g, pos, with_labels=True, node_color='lightblue',
        node_size=800, arrowsize=25, font_weight='bold')
edge_labels = {(u, v): f"w={d['w']}" for u, v, d in g.edges(data=True)}
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
plt.title('Parametric Network Oracle Graph')
plt.grid(True, alpha=0.3)
