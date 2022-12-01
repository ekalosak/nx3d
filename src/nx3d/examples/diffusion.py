""" This source implements graph diffusion to demo the dynamic graph state support """
import random
from math import log

try:
    import matplotlib as mpl
except ImportError:
    pass
import networkx as nx
import numpy as np
from loguru import logger

from nx3d.core import Nx3D

DIFFUSION_RATE = 0.05  # scale diffusion rate per update call
DIFFUSION_STEP_PER_SEC = 10
EPS = 0.2  # when all diffusions steps are under EPS, reset


def _init_diff_graph(g, color_init="uniform"):
    """init color and label render attributes"""
    allowed_color_init = ["uniform", "equitable"]
    if color_init not in allowed_color_init:
        raise ValueError(
            f"color_init={color_init} not allowed, must be one of {allowed_color_init}"
        )
    if color_init == "equitable":
        try:
            mpl
        except NameError:
            logger.warning(
                f'color_init={color_init} requires matplotlib; using "uniform" instead (which does not)'
            )
            color_init = "uniform"
        else:
            ncolor = int(log(len(g))) + 3
            rainbows = mpl.colormaps["rainbow"].resampled(ncolor)
            color_index = nx.equitable_color(g, num_colors=ncolor)
    g.graph["nstep"] = 0
    if "show_labels" not in g.graph:
        g.graph["show_labels"] = True
    for n, nd in g.nodes(data=True):
        if color_init == "equitable":
            nd["color"] = rainbows(color_index[n])
        elif color_init == "uniform":
            nd["color"] = tuple([random.random(), random.random(), random.random(), 1])
        nd["label"] = ""
    for u, v, ed in g.edges(data=True):
        col0 = np.array(g.nodes[u]["color"])
        col1 = np.array(g.nodes[v]["color"])
        color = (col0 + col1) / 2
        logger.trace(f"color {type(color)} {color}")
        ed["color"] = tuple(color)
        ed["label"] = ""
    logger.info(f"{len(g)} nodes")
    logger.info(f"EPS={EPS}")
    logger.info(f"Restart when total_delta < {EPS * log(len(g))}")


def _diffuse(
    g: nx.Graph, di: int, dt: float, eps=EPS, diffusion_rate=DIFFUSION_RATE, nstep=None
):
    """state transfer function for graph diffusion
    Args:
        eps: reset when diffusion across all edges is less than eps
        diffusion_rate: coefficient of diffusion (how much color bleeds at each step)
    """
    out = [str(di), f"{dt:.1f}"]  # noqa: F841
    deltas = []
    for e in g.edges:
        col0 = np.array(g.nodes[e[0]]["color"])
        col1 = np.array(g.nodes[e[1]]["color"])
        dc = col0 - col1
        deltas.append(abs(dc).sum())
        new_col0 = col0 - dc * diffusion_rate
        new_col1 = col1 + dc * diffusion_rate
        g.nodes[e[0]]["color"] = tuple(new_col0)
        g.nodes[e[0]]["label"] = (
            f"{(sum(new_col0)):.1f}" if g.graph["show_labels"] else ""
        )
        g.nodes[e[1]]["color"] = tuple(new_col1)
        g.nodes[e[1]]["label"] = (
            f"{(sum(new_col1)):.1f}" if g.graph["show_labels"] else ""
        )
        g.edges[e]["color"] = tuple((new_col0 + new_col1) / 2)
        g.edges[e]["label"] = f"{(abs(sum(dc))):.1f}" if g.graph["show_labels"] else ""
    logger.debug(f"total_delta: {sum(deltas)}")
    reset = False
    if all(delta < eps for delta in deltas):
        reset = True
    elif nstep and g.graph["nstep"] == nstep:
        reset = True
    if reset:
        _init_diff_graph(g)
    else:
        g.graph["nstep"] += 1


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
