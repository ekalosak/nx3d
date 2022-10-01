""" This source implements graph diffusion to demo the dynamic graph state support """
import random
from math import log

import networkx as nx
import numpy as np
from loguru import logger

from nx3d.core import Nx3D

DIFFUSION_RATE = 0.05  # scale diffusion rate per update call
DIFFUSION_STEP_PER_SEC = 4
EPS = 0.3  # per node "not diffusing" game over parameter


def _init_diff_graph(g):
    """init color and label render attributes"""
    for nd in g.nodes:
        elm = g.nodes[nd]
        color = [random.random() * 0.8, random.random() * 0.8, random.random() * 0.8, 1]
        elm["color"] = tuple(color)
        elm["label"] = ""
    for ed in g.edges:
        col0 = np.array(g.nodes[ed[0]]["color"])
        col1 = np.array(g.nodes[ed[1]]["color"])
        color = (col0 + col1) / 2
        g.edges[ed]["color"] = tuple(color)
        g.edges[ed]["label"] = ""
    logger.info(f"{len(g)} nodes")
    logger.info(f"EPS={EPS}")
    logger.info(f"Restart when total_delta < {EPS * log(len(g))}")


def _diffuse(g: nx.Graph, di: int, dt: float):
    """state transfer function for graph diffusion"""
    out = [str(di), f"{dt:.1f}"]  # noqa: F841
    total_delta = 0.0
    for ed in g.edges:
        col0 = np.array(g.nodes[ed[0]]["color"])
        col1 = np.array(g.nodes[ed[1]]["color"])
        dc = col0 - col1
        total_delta += abs(dc).sum()
        new_col0 = col0 - dc * DIFFUSION_RATE
        new_col1 = col1 + dc * DIFFUSION_RATE
        g.nodes[ed[0]]["color"] = tuple(new_col0)
        g.nodes[ed[0]]["label"] = (
            f"{(sum(new_col0)):.1f}" if g.graph["show_labels"] else ""
        )
        g.nodes[ed[1]]["color"] = tuple(new_col1)
        g.nodes[ed[1]]["label"] = (
            f"{(sum(new_col1)):.1f}" if g.graph["show_labels"] else ""
        )
        g.edges[ed]["color"] = tuple((new_col0 + new_col1) / 2)
        g.edges[ed]["label"] = f"{(abs(sum(dc))):.1f}" if g.graph["show_labels"] else ""
    logger.debug(f"total_delta: {total_delta}")
    if total_delta < EPS * log(len(g)):
        logger.success("Restarting...")
        _init_diff_graph(g)


def diffusion(g, **kwargs):
    """This function opens a popup showing how a graph diffusion can be rendered. You can run it from your shell as
    follows:

    ``
    python -m nx3d diffusion
    ``

    Args:
        kwargs: passed to Nx3D.__init__
    """
    _init_diff_graph(g)
    app = Nx3D(
        g,
        state_trans_func=_diffuse,
        state_trans_delay=1.0 / DIFFUSION_STEP_PER_SEC,
        **kwargs,
    )
    app.run()
