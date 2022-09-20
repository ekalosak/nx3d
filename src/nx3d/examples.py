""" This source implements graph diffusion to demo the dynamic graph state support """
import random

import networkx as nx
import numpy as np

from nx3d.core import Nx3D

RATE = 0.05  # scale diffusion rate per update call
EPS = 1.35  # when total delta gets under this value, restart


def _init_diff_graph(g):
    """must init color val label"""
    for nd in g.nodes:
        elm = g.nodes[nd]
        color = [random.random() * 0.8, random.random() * 0.8, random.random() * 0.8, 1]
        elm["color"] = tuple(color)
        elm["label"] = f"{(sum(color) - 1):.4f}"


def _diffuse(g: nx.Graph, di: int, dt: float):
    """state transfer function for graph diffusion"""
    # NOTE use out to show that di and dt are incorrect NX-19
    out = [str(di), f"{dt:.4f}"]  # noqa: F841
    total_delta = 0.0
    for ed in g.edges:
        col0 = np.array(g.nodes[ed[0]]["color"])
        col1 = np.array(g.nodes[ed[1]]["color"])
        dc = col0 - col1
        total_delta += abs(dc).sum()
        new_col0 = col0 - dc * RATE
        new_col1 = col1 + dc * RATE
        g.nodes[ed[0]]["color"] = tuple(new_col0)
        g.nodes[ed[0]]["label"] = f"{(sum(new_col0)):.3f}"
        g.nodes[ed[1]]["color"] = tuple(new_col1)
        g.nodes[ed[1]]["label"] = f"{(sum(new_col1)):.3f}"
        g.edges[ed]["color"] = tuple((new_col0 + new_col1) / 2)
        g.edges[ed]["label"] = f"{(sum(dc)):.3f}"
    print(f"total_delta: {total_delta}")
    if total_delta < EPS:
        print("\nRESTART\n")
        _init_diff_graph(g)


def diffusion_example(**kwargs):
    """This function opens a popup showing how a graph diffusion can be rendered. You can run it from your shell as
    follows:

    ```
    python -m nx3d diffusion
    ```

    Args:
        kwargs: passed to Nx3D.__init__
    """
    g = nx.frucht_graph()
    pos = kwargs.pop("pos", None)
    _init_diff_graph(g)
    app = Nx3D(g, pos=pos, state_trans_func=_diffuse, **kwargs)
    app.run()
