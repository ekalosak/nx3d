from itertools import chain, repeat
from math import sqrt

import networkx as nx
import numpy as np
from networkx import Graph
from panda3d.core import Material, NodePath, Vec4


def set_color(ob: NodePath, color: Vec4):
    # FIXME this should replace the existing mat if any to be idempotent; can lead to memory leak? via scene graph
    # growth due to adding and adding mats w.o update.
    mat = Material()
    mat.setShininess(5.0)
    try:
        mat.setBaseColor(color)
    except TypeError as e:
        raise TypeError("try tuple(color)") from e
    ob.setMaterial(mat, 1)


def all_elements(g: Graph):
    """iterate over all the pass-by-reference elements of the graph i.e. all nodes and all edges"""
    for ob, kind in chain(zip(g.nodes, repeat("node")), zip(g.edges, repeat("edge"))):
        if kind == "node":
            elm = g.nodes[ob]
        else:
            elm = g.edges[ob]
        yield elm


def get_pos_scale(g):
    """heuristic for how far away nodes should be"""
    return 2.0 * sqrt(len(g.nodes))


def init_pos(g):
    """Set a 'pos' render attribute on all nodes in the graph.
    If the graph has tuples for nodes, they're assumed to be positions and will be used to set the render attribute.
    """
    scale = get_pos_scale(g)
    pos = nx.spring_layout(g, dim=3, scale=scale)
    for n, nd in g.nodes(data=True):
        if "pos" in nd:
            assert len(nd["pos"]) == 3, "render attribute position must be 3D"
            continue
        elif isinstance(n, tuple):
            if len(n) == 1:
                nd["pos"] = np.array([n[0], 0, 0])
            elif len(n) == 2:
                nd["pos"] = np.array([n[0], n[1], 0])
            else:
                nd["pos"] = np.array(n[:3])
        else:
            nd["pos"] = pos[n]
