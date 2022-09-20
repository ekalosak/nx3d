from itertools import chain, repeat

from networkx import Graph
from panda3d.core import Material, NodePath, Vec4


def set_color(ob: NodePath, color: Vec4):
    # FIXME this should replace the existing mat if any to be idempotent; can lead to memory leak? via scene graph
    # growth due to adding and adding mats w.o update.
    mat = Material()
    mat.setShininess(5.0)
    mat.setBaseColor(color)
    ob.setMaterial(mat, 1)


def all_elements(g: Graph):
    """iterate over all the pass-by-reference elements of the graph i.e. all nodes and all edges"""
    for ob, kind in chain(zip(g.nodes, repeat("node")), zip(g.edges, repeat("edge"))):
        if kind == "node":
            elm = g.nodes[ob]
        else:
            elm = g.edges[ob]
        yield elm
