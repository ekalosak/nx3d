from itertools import islice

import networkx as nx
import pytest

from nx3d.examples import gameoflife


@pytest.fixture
def gg(g):
    gameoflife._reset_board(g, n_live=0)
    g = nx.convert_node_labels_to_integers(g)
    return g


def test_gol_graph():
    dim = (3, 3, 3)
    g = gameoflife.grid_gol_graph(dim)
    gameoflife._init_pos(g)
    assert (1, 3, 0) not in g
    assert (0, 0, 0) in g[(1, 1, 1)]


def test_do_life_0(gg):
    for n in gg:
        break
    gg.nodes[n]["val"] = 1
    gameoflife._do_life(gg, None, None)
    for n in gg:
        assert gg.nodes[n]["val"] == 0, "lone node should die"


def test_do_life_1(gg):
    g = gg
    deg = [d[1] for d in nx.degree(g)]  # returns [(n, deg)]
    nnbs = [2, 3]
    if max(deg) < max(nnbs):
        pytest.skip(f"need at least one node with degree >= {max(nnbs)}")
    assert all(
        isinstance(n, int) for n in g
    ), "nodes should be all int by this point via _init_pos"
    n = deg.index(max(deg))
    g.nodes[n]["val"] = 1
    for nnb in nnbs:
        for nbr in islice(g[n].keys(), nnb):
            g.nodes[nbr]["val"] = 1
        gameoflife._do_life(g, 0, 0)
        assert g.nodes[n]["val"] == 1, f"node with {nnb} live neighbors shoud survive"


def test_do_life_2(gg):
    g = gg
    deg = [d[1] for d in nx.degree(g)]
    if max(deg) < 3:
        pytest.skip("need at least one node with degree >= 3")
    assert all(
        isinstance(n, int) for n in g
    ), "nodes should be all int by this point via _init_pos"
    n = deg.index(max(deg))
    for nbr in islice(g[n], 3):
        g.nodes[nbr]["val"] = 1
    gameoflife._do_life(g, 0, 0)
    assert g.nodes[n]["val"] == 1, "node with two live neighbors shoud survive"
