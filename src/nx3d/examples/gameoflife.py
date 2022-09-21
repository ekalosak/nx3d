""" This source implements the Game of Life on:
- a 2D gridded finite Graph
- a 3D gridded finite Graph
- a 2D gridded finite Graph embedded in 3D on a sphere
- a 2D gridded finite DiGraph embedded on a cylinder

The rules are:
- node with 2 or 3 live neighbors lives
- dead node with 3 live neighbors lives
- all else is dead

Interior nodes have 8 neighbors
"""
import random

import networkx as nx
import numpy as np

from nx3d.core import Nx3D

BOARD_KINDS = ["2Dgrid"]


def _grid_neighbors_2d(nd, size):
    """handle edge cases for a finite grid"""
    ds = [1, 0, -1]
    for dy in ds:
        for dx in ds:
            if dx == 0 and dy == 0:
                continue
            y = nd[0] + dy
            x = nd[1] + dx
            if x < 0 or y < 0 or x >= size or y >= size:
                continue
            yield (y, x)


def _make_grid_2d(size: int):
    """start from upper left origin, increase in y is down, increase in x is right"""
    g = nx.Graph()
    for y in range(size):
        for x in range(size):
            nd = (y, x)
            g.add_node(nd)
    for y in range(size):
        for x in range(size):
            n0 = (y, x)
            for n1 in _grid_neighbors_2d(n0, size):
                g.add_edge(n0, n1)
    return g


def _update_colors(g):
    """black if alive else white"""
    for nd in g:
        val = g.nodes[nd]["val"]
        g.nodes[nd]["color"] = (0, 0, 0, 1) if val else (1, 1, 1, 0)


def _clear_board(g):
    for nd in g:
        g.nodes[nd]["val"] = 0


def _make_board(kind: str, size: int):
    if kind == "2Dgrid":
        g = _make_grid_2d(size)
    else:
        raise ValueError(f"board kind {kind} not supported")
    _clear_board(g)
    _update_colors(g)
    return g


def _do_life(g: nx.Graph, di: int, dt: float):
    vals = {}
    for nd in g:
        live_nbrs = 0
        for nbr, _ in g.adjacency():
            live_nbrs += g.nodes[nbr]["val"]
        if live_nbrs == 3:
            vals[nd] = 1
        elif g.nodes[nd]["val"] and live_nbrs == 2:
            vals[nd] = 1
        else:
            vals[nd] = 0
    for nd in g:
        g.nodes[nd]["val"] = vals[nd]


def game_of_life_example(**kwargs):
    """This function opens a popup that runs the Game of Life on various graphs

    ```
    python -m nx3d life
    ```

    Args:
        kwargs: passed to Nx3D.__init__
    """
    g = _make_board("2Dgrid", 48)
    for nd in g.nodes:
        assert len(g.nodes[nd]["pos"]) == 3
    app = Nx3D(g, state_trans_func=_do_life, **kwargs)
    app.run()
