import random

import networkx as nx
import numpy as np

from nx3d.core import Nx3D

""" Graph diffusion
"""

RATE = 0.1  # scale diffusion rate per update call
EPS = 2.3  # when total delta gets under this value, restart


def _init_diff_graph(g):
    """must init color val label"""
    for nd in g.nodes:
        elm = g.nodes[nd]
        color = [random.randint(0, 1) * 0.5, random.random(), random.randint(0, 1), 1]
        elm["color"] = tuple(color)
        elm["label"] = f"{(sum(color) - 1):.4f}"


def _diffuse(g: nx.Graph, di: int, dt: float):
    """state transfer function for graph diffusion"""
    # NOTE use out to show that di and dt are incorrect NX-19
    out = [str(di), f"{dt:.4f}"]  # noqa: F841
    total_delta = 0.0
    for ed in g.edges:
        e0 = g.nodes[ed[0]]
        e1 = g.nodes[ed[1]]
        col0 = np.array(e0["color"])
        col1 = np.array(e1["color"])
        dc = col0 - col1
        total_delta += abs(dc).sum()
        new_col0 = col0 - dc * RATE
        new_col1 = col1 + dc * RATE
        e0["color"] = tuple(new_col0)
        e0["label"] = f"{(sum(new_col0) - 1):.4f}"
        e1["color"] = tuple(new_col1)
        e0["label"] = f"{(sum(new_col1) - 1):.4f}"
    print(f"total_delta: {total_delta}")
    if total_delta < EPS:
        print("\nRESTART\n")
        _init_diff_graph(g)


def diffusion_example(**kwargs):
    """example state transition function; diffusion on undirected graph"""
    print("\nBEGIN\n")
    g = nx.frucht_graph()
    pos = None
    _init_diff_graph(g)
    app = Nx3D(g, pos=pos, state_trans_func=_diffuse, **kwargs)
    app.run()
    print("\nEND\n")
