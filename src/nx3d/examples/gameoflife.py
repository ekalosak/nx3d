""" This source implements the Game of Life on:
- a 2D gridded finite Graph
- a 3D gridded finite Graph
- a 2D gridded finite Graph embedded in 3D on a sphere
- a 2D gridded finite DiGraph embedded on a cylinder
"""
import random

import networkx as nx
import numpy as np

from nx3d.core import Nx3D


def _grid_neighbors_2d(nd, size):
    """handle edge cases for a finite grid"""
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for delta in deltas:
        y = nd[0] + delta[0]
        x = nd[1] + delta[1]
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


def _make_board(kind: str, size: int):
    if kind == "2Dgrid":
        return _make_grid_2d(size)
    else:
        raise ValueError(f"board kind {kind} not supported")


def _do_life(g: nx.Graph, di: int, dt: float):
    assert 0


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
