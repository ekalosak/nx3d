import random

import networkx as nx

from nx3d.core import Nx3D

""" Graph diffusion
"""

RATE = 3.0  # scale diffusion rate
AVG_NODE_VAL = 0.8


def _init_diff_graph(g):
    """must init color val label"""
    for nd in g.nodes:
        elm = g.nodes[nd]
        elm["val"] = random.random()
        elm["color"] = (0, 0, elm["val"], 1)
        elm["label"] = elm["val"]


def _diffuse(g: nx.Graph, di: int, dt: float):
    """state transfer function for graph diffusion"""
    out = [str(di), f"{dt:.4f}"]
    for nd in g:
        e0 = g.nodes[nd]
        nbrs = list(g.adj[nd].keys())
        for nbr in nbrs:
            e1 = g.nodes[nbr]
            dv = dt * RATE
            e0["val"] -= dv
            e1["val"] += dv
        e0["color"] = (0, 0, e0["val"], 1)
        e0["label"] = e0["val"]
        out.append(f'{nd}-{e0["val"]}')
    print(", ".join(out))


def diffusion_example(**kwargs):
    """example state transition function; diffusion on undirected graph"""
    print("\nBEGIN\n")
    g = nx.barbell_graph(4, 2)
    _init_diff_graph(g)
    app = Nx3D(g, state_trans_func=_diffuse, **kwargs)
    app.run()
    print("\nEND\n")
