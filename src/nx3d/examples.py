import random

import networkx as nx
import numpy as np

from nx3d.core import Nx3D

""" Graph diffusion
"""

RATE = 0.08  # scale diffusion rate per update call


def _init_diff_graph(g):
    """must init color val label"""
    for nd in g.nodes:
        elm = g.nodes[nd]
        color = [random.random() for _ in range(3)] + [1]
        elm["color"] = tuple(color)
        elm["label"] = tuple(color)


def _diffuse(g: nx.Graph, di: int, dt: float):
    """state transfer function for graph diffusion"""
    out = [str(di), f"{dt:.4f}"]  # NOTE use to show that di and dt are incorrect NX-19
    total_delta = 0.0
    for ed in g.edges:
        e0 = g.nodes[ed[0]]
        e1 = g.nodes[ed[1]]
        col0 = np.array(e0["color"])
        col1 = np.array(e1["color"])
        dc = col0 - col1
        total_delta += abs(dc)
        new_col0 = col0 - dc * RATE
        new_col1 = col1 + dc * RATE
        e0["color"] = tuple(new_col0)
        e0["label"] = e0["color"]
        e1["color"] = tuple(new_col1)
        e1["label"] = e1["color"]
    print(f"total_delta: {total_delta.sum()}")


def diffusion_example(**kwargs):
    """example state transition function; diffusion on undirected graph"""
    print("\nBEGIN\n")
    g = nx.barbell_graph(2, 0)
    _init_diff_graph(g)
    app = Nx3D(g, state_trans_func=_diffuse, **kwargs)
    app.run()
    print("\nEND\n")
