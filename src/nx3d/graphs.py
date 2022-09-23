import networkx as nx


def multi_graph(init_func, n: int, alter=False) -> nx.MultiGraph:
    g = nx.MultiGraph()
    weighted_edges = []
    for n0, n1 in init_func().edges:
        for i in range(n):
            weighted_edges.append((n0, n1, i) if alter and i % 2 else (n1, n0, i))
    g.add_weighted_edges_from(weighted_edges)
    assert isinstance(g, nx.MultiGraph)
    assert len(weighted_edges) == len(g.edges)
    return g
