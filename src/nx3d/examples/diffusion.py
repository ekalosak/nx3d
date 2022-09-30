""" This source implements graph diffusion to demo the dynamic graph state support """
import random

import networkx as nx
import numpy as np

from nx3d.core import Nx3D

RATE = 0.05  # scale diffusion rate per update call
EPS = 0.18  # per node "not diffusing" game over parameter


def _init_diff_graph(g):
    """must init color val label"""
    for nd in g.nodes:
        elm = g.nodes[nd]
        color = [random.random() * 0.8, random.random() * 0.8, random.random() * 0.8, 1]
        elm["color"] = tuple(color)
        elm["label"] = f"{(sum(color) - 1):.4f}" if g.graph["show_labels"] else ""
    for ed in g.edges:
        col0 = np.array(g.nodes[ed[0]]["color"])
        col1 = np.array(g.nodes[ed[1]]["color"])
        color = (col0 + col1) / 2
        g.edges[ed]["color"] = tuple(color)
        g.edges[ed]["label"] = f"{(sum(color)):.3f}" if g.graph["show_labels"] else ""
    print(f"{len(g)} nodes")
    print(f"EPS={EPS}")
    print(f"Restart when total_delta < {EPS * len(g)}")


def _diffuse(g: nx.Graph, di: int, dt: float):
    """state transfer function for graph diffusion"""
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
        g.nodes[ed[0]]["label"] = (
            f"{(sum(new_col0)):.3f}" if g.graph["show_labels"] else ""
        )
        g.nodes[ed[1]]["color"] = tuple(new_col1)
        g.nodes[ed[1]]["label"] = (
            f"{(sum(new_col1)):.3f}" if g.graph["show_labels"] else ""
        )
        g.edges[ed]["color"] = tuple((new_col0 + new_col1) / 2)
        g.edges[ed]["label"] = f"{(sum(dc)):.3f}" if g.graph["show_labels"] else ""
    print(f"total_delta: {total_delta}")
    if total_delta < EPS * len(g):
        print("\nRESTART\n")
        _init_diff_graph(g)


def diffusion(g=None, nolabel=False, **kwargs):
    """This function opens a popup showing how a graph diffusion can be rendered. You can run it from your shell as
    follows:

    ``
    python -m nx3d diffusion
    ``

    Args:
        kwargs: passed to Nx3D.__init__
    """
    if not g:
        g = nx.frucht_graph()
    g.graph["show_labels"] = not nolabel
    _init_diff_graph(g)
    app = Nx3D(g, state_trans_func=_diffuse, **kwargs)
    app.run()
