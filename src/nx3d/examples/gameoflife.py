""" This source implements the Game of Life on:
- a 2D gridded finite Graph

# TODO
- Use nx.grid_2d_graph
- a 3D gridded finite Graph
- a 2D gridded finite Graph embedded in 3D on a sphere
- a 2D gridded finite DiGraph embedded on a cylinder, taurus, mobius strip (need 2 layers z to orient), klein bottle

The rules are:
- node with 2 or 3 live neighbors lives
- dead node with 3 live neighbors lives
- all else is dead

Interior nodes have 8 neighbors
"""
import itertools as itt
import random

import networkx as nx
import numpy as np

from nx3d.core import Nx3D

BOARD_KINDS = ["2Dgrid"]
COLOR_DEAD = (0.2, 0.2, 0.2, 1)
COLOR_LIVE = (0.8, 0.8, 0.8, 1)


def _grid_neighbors_2d(nd, size):
    """handle edge cases for a finite grid"""
    ds = [1, 0, -1]
    for dy in ds:
        for dx in ds:
            if dx == 0 and dy == 0:
                continue
            y = nd[0] + dy
            x = nd[1] + dx
            if x < 0 or y < 0 or x >= size[1] or y >= size[0]:
                continue
            yield (y, x)


def _make_grid_2d(size: tuple[int, int]):
    """start from upper left origin, increase in y is down, increase in x is right"""
    g = nx.Graph()
    # g = nx.grid_2d_graph(*size)
    # g = nx.Graph()
    for y in range(size[0]):
        for x in range(size[1]):
            nd = (y, x)
            g.add_node(nd)
            g.nodes[nd]["color"] = COLOR_DEAD
            g.nodes[nd]["pos"] = np.array(
                (int(x - size[0] / 2), 0, int(size[1] / 2 - y))
            )
    for y in range(size[0]):
        for x in range(size[1]):
            n0 = (y, x)
            for n1 in _grid_neighbors_2d(n0, size):
                g.add_edge(n0, n1)
    return g


def _update_colors(g):
    """black if alive else white"""
    for nd in g:
        val = g.nodes[nd]["val"]
        g.nodes[nd]["color"] = COLOR_LIVE if val else COLOR_DEAD


def _grid_to_numpy(g):
    my = max(y for y, _ in g)
    mx = max(x for _, x in g)
    bd = np.empty((my + 1, mx + 1))
    for nd in g:
        bd[nd] = g.nodes[nd]["val"]
    return bd


def print_board(g):
    print(_grid_to_numpy(g))


def _clear_board(g):
    for nd in g:
        g.nodes[nd]["val"] = 0


def _reset_grid(g, n_live: int):
    _clear_board(g)
    bd = _grid_to_numpy(g)
    yixs = range(bd.shape[0])
    xixs = range(bd.shape[1])
    ixs = list(itt.product(yixs, xixs))
    for ix in random.sample(ixs, k=n_live):
        g.nodes[ix]["val"] = 1


def _make_board(kind: str, size: tuple[int, int]):
    if kind == "2Dgrid":
        g = _make_grid_2d(size)
        _reset_grid(g, 0)
    else:
        raise ValueError(f"board kind {kind} not supported")
    _update_colors(g)
    return g


def _do_life(g: nx.Graph, di: int, dt: float):
    if all(g.nodes[nd]["val"] == 0 for nd in g):
        _reset_grid(g, n_live=len(g) // 4)
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


def game_of_life(g=None, size=(32, 32), **kwargs):
    """This function opens a popup that runs the Game of Life.

    ``
    python -m nx3d life
    ``

    Args:
        kwargs: passed to Nx3D.__init__
    """
    if not g:
        g = _make_board("2Dgrid", size)
    for nd in g.nodes:
        assert len(g.nodes[nd]["pos"]) == 3
    app = Nx3D(g, state_trans_func=_do_life, **kwargs)
    app.run()
