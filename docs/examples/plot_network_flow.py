"""
Network Flow Graph
==================

Visualization of a directed flow network with edge capacities.
"""
import matplotlib.pyplot as plt
import networkx as nx

g = nx.DiGraph()
edges = [
    ('s', 'a', 10), ('s', 'b', 5),
    ('a', 'b', 15), ('a', 't', 10),
    ('b', 't', 10),
]
for u, v, c in edges:
    g.add_edge(u, v, capacity=c)

plt.figure(figsize=(7, 5))
pos = nx.spring_layout(g, seed=42)
nx.draw(g, pos, with_labels=True, node_color='lightgreen',
        node_size=800, arrowsize=25, font_weight='bold',
        font_size=14)
edge_labels = {(u, v): f'cap={d["capacity"]}'
               for u, v, d in g.edges(data=True)}
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,
                             font_size=11)
plt.title('Flow Network with Edge Capacities')
plt.grid(True, alpha=0.3)
