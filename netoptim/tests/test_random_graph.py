# import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from ..min_cycle_ratio import *


def vdc(n, base=2):
    vdc, denom = 0.0, 1.0
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc


def vdcorput(n, base=2):
    '''
    n - number of vectors
    base - seeds
    '''
    return [vdc(i, base) for i in range(n)]


class SimpleDiGraph(nx.DiGraph):
    nodemap = {}

def formGraph(T, pos, eta, seed=None):
    ''' Form N by N grid of nodes, connect nodes within eta.
        mu and eta are relative to 1/(N-1)
    '''
    if seed is not None:
        np.random.seed(seed)

    N = np.sqrt(T)
    eta = eta/(N-1)

    # generate perterbed grid positions for the nodes
    pos = dict(enumerate(pos))
    n = len(pos)

    # connect nodes with edges
    G = nx.random_geometric_graph(n, eta, pos=pos)
    G = SimpleDiGraph(nx.DiGraph(G))
    G.nodemap = range(G.number_of_nodes())
    return G


# def showPaths(G, pos, N, edgeProbs=1.0, path=None, visibleNodes=None, guards=None):
#     ''' Takes directed graph G, node positions pos, and edge probabilities.
#         Optionally uses path (a list of edge indices) to plot the smuggler's path.

#         edgeProbd gives the probabilities for all the edges, including hidden ones.

#         path includes all the edges, including the hidden ones

#         Gnodes and Rnodes denote the source and destination nodes, to be plotted green
#         and red respectively.

#         guards is a list of node indices for denoting guards with a black dot on the plot
#     '''
#     fig = plt.figure(figsize=(8, 6))
#     ax = fig.add_subplot(111, aspect='equal')

#     n = G.number_of_nodes()
#     if visibleNodes is None:
#         visibleNodes = G.nodes()
#     primalNodes = range(0, N)
#     spareNodes = range(N, n)
#     # draw the regular interior nodes in the graph
#     nx.draw_networkx_nodes(G, pos, nodelist=primalNodes,
#                            node_color='c', node_size=50, ax=ax)
#     nx.draw_networkx_nodes(G, pos, nodelist=spareNodes,
#                            node_color='r', node_size=50, ax=ax)

#     # draw guard nodes
#     if guards is not None:
#         nx.draw_networkx_nodes(G, pos, nodelist=guards,
#                                node_color='.0', node_size=100, ax=ax)

#     if path is None:
#         alpha = 1
#     else:
#         alpha = .15

#     # start messing with edges
#     edge2ind = {e: i for i, e in enumerate(G.edges())}
#     ind2edge = {i: e for i, e in enumerate(G.edges())}

#     # only display edges between non-dummy nodes
#     visibleEdges = [i for i in range(len(
#         edge2ind)) if ind2edge[i][0] in visibleNodes and ind2edge[i][1] in visibleNodes]

#     edgelist = [ind2edge[i] for i in visibleEdges]

#     if isinstance(edgeProbs, float):
#         edgeProbs = [edgeProbs]*G.number_of_edges()

#     p = [edgeProbs[i] for i in visibleEdges]

#     # draw edges of graph, make transparent if we're drawing a path over them
#     edges = nx.draw_networkx_edges(G, pos, edge_color=p, width=1,
#                                    edge_cmap=plt.cm.RdYlGn, arrows=False, edgelist=edgelist, edge_vmin=0.0,
#                                    edge_vmax=1.0, ax=ax, alpha=alpha)

#     # draw the path, only between visible nodes
#     if path is not None:
#         #visiblePath = [i for i in path if ind2edge[i][0] in visibleNodes and ind2edge[i][1] in visibleNodes]
#         #path_pairs = [ind2edge[i] for i in visiblePath]
#         #path_colors = [edgeProbs[i] for i in visiblePath]
#         edges = nx.draw_networkx_edges(G, pos, edge_color='b', width=1,
#                                        edge_cmap=plt.cm.RdYlGn, edgelist=path, arrows=True, edge_vmin=0.0,
#                                        edge_vmax=1.0)

#     ## fig.colorbar(edges,label='??? graph')

#     ax.axis([-0.05, 1.05, -0.05, 1.05])
#     # ax.axis('tight')
#     # ax.axis('equal')
#     ax.axis('off')

#     return fig, ax


# if __name__ == "__main__":
def test_random_graph():
    N = 158
    M = 40
#    r = 4

    T = N+M
    xbase = 2
    ybase = 3
    x = [i for i in vdcorput(T, xbase)]
    y = [i for i in vdcorput(T, ybase)]
    pos = zip(x, y)
    G = formGraph(T, pos, 1.6, seed=5)
#    n = G.number_of_nodes()
#    pos2 = dict(enumerate(pos))
#    fig, ax = showPaths(G, pos2, N)
#    plt.show()

    # Add a sink, connect all spareTSV to it.
    ## pos = pos + [(1.5,.5)]
    for u, v in G.edges():
        h = np.array(G.node[u]['pos']) - np.array(G.node[v]['pos'])
        #G[u][v]['cost'] = np.sqrt(np.dot(h, h))
        G[u][v]['cost'] = h[0] + h[1]

    r, c, _ = min_cycle_ratio(G)
    assert c != None

    pathlist = c
    print(pathlist)
#    pos2 = dict(enumerate(pos))
#    fig, ax = showPaths(G, pos2, N, path=pathlist)
#    plt.show()