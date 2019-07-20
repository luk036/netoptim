# import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from netoptim.min_cycle_ratio import min_cycle_ratio


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
    eta = eta / (N - 1)

    # generate perterbed grid positions for the nodes
    pos = dict(enumerate(pos))
    n = len(pos)

    # connect nodes with edges
    G = nx.random_geometric_graph(n, eta, pos=pos)
    G = SimpleDiGraph(nx.DiGraph(G))
    G.nodemap = range(G.number_of_nodes())
    return G


# if __name__ == "__main__":
def test_random_graph():
    N = 158
    M = 40
    #    r = 4

    T = N + M
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
    # pos = pos + [(1.5,.5)]
    for u, v in G.edges():
        h = np.array(G.node[u]['pos']) - np.array(G.node[v]['pos'])
        # G[u][v]['cost'] = np.sqrt(np.dot(h, h))
        G[u][v]['cost'] = h[0] + h[1]

    _, c, _ = min_cycle_ratio(G)
    assert c is not None

    pathlist = c
    print(pathlist)


#    pos2 = dict(enumerate(pos))
#    fig, ax = showPaths(G, pos2, N, path=pathlist)
#    plt.show()
