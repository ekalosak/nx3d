""" This source implements the Game of Life on arbitrary graphs.

The rules are:
- node with 2 or 3 live neighbors lives
- dead node with 3 live neighbors lives
- all else is dead

Interior nodes have 8 neighbors
"""
import itertools as itt
import random
from typing import Optional

import networkx as nx
from loguru import logger

from nx3d.core import Nx3D

COLOR_DEAD = (0.2, 0.2, 0.2, 1)
COLOR_LIVE = (0.8, 0.8, 0.8, 1)


def grid_gol_graph(dim):
    # n1 connected to nodes on 2x2 hypercube centered at n1
    # that is, add in the diagonals
    g = nx.grid_graph(dim)
    edges = set()
    for n in g:
        for nbr in g[n]:
            for i in range(len(dim)):
                if n[i] == nbr[i]:
                    planar_nodes = set()
                    for adja in itt.combinations_with_replacement([-1, 0, 1], len(dim)):
                        n1 = tuple([ni - ai for ni, ai in zip(nbr, adja)])
                        planar_nodes.add(n1)
                    edges.update([(n, pn) for pn in planar_nodes])
    g.add_edges_from(edges)
    g1 = nx.grid_graph(dim)
    return nx.induced_subgraph(g, g1.nodes)


def _update_colors(g):
    """black if alive else white"""
    for _, nd in g.nodes(data=True):
        val = nd["val"]
        nd["color"] = COLOR_LIVE if val else COLOR_DEAD


def _clear_board(g):
    for n in g:
        g.nodes[n]["val"] = 0
        g.nodes[n]["last_val"] = 0


def _reset_board(g, n_live: Optional[int] = None):
    _clear_board(g)
    g.graph["reset"] = True
    if n_live is None:
        n_live = len(g) // 2
    elif n_live <= 0:
        return
    for n in random.sample(g.nodes, k=n_live):
        g.nodes[n]["val"] = 1
    _update_colors(g)


def _do_life(g: nx.Graph, di, dt):
    if all(nd["val"] == nd["last_val"] for _, nd in g.nodes(data=True)):
        logger.success("dead board, resetting")
        _reset_board(g)
    else:
        g.graph["reset"] = False
        for n in g:
            g.nodes[n]["last_val"] = g.nodes[n]["val"]
        vals = {}
        for nd, nbrsdict in g.adjacency():
            live_nbrs = 0
            nbrs = list(nbrsdict.keys())
            live_nbrs = sum(g.nodes[nbr]["val"] for nbr in nbrs)
            if live_nbrs == 3:
                vals[nd] = 1
            elif g.nodes[nd]["val"] and live_nbrs == 2:
                vals[nd] = 1
            else:
                vals[nd] = 0
        for nd in g:
            g.nodes[nd]["val"] = vals[nd]
    _update_colors(g)


def game_of_life(g=grid_gol_graph((16, 16)), **kwargs):
    """This function opens a popup that runs the Game of Life.

    ``
    python -m nx3d life
    ``

    Args:
        kwargs: passed to Nx3D.__init__
    """
    _reset_board(g)
    g = nx.convert_node_labels_to_integers(g)
    app = Nx3D(g, state_trans_func=_do_life, **kwargs)
    app.run()
