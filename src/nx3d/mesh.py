""" This module provides procedural mesh generation """
import numpy as np
import pyvista as pv
from panda3d.core import (
    Geom,
    GeomLines,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
)
from pyvista.utilities.geometric_objects import Arrow, Cylinder, PlatonicSolid


def line(face: np.ndarray):
    """Make a Panda Geom object from a ndarray whose entries are the indices of the vertices."""
    prim = GeomLines(Geom.UHStatic)
    prim.addVertices(*face)
    prim.closePrimitive()
    return prim


def triangle(face):
    prim = GeomTriangles(Geom.UHStatic)
    prim.addVertices(*face)
    prim.closePrimitive()
    return prim


def polygon(face):
    prim = GeomTriangles(Geom.UHStatic)
    for vix in range(len(face) - 2):
        prim.addVertices(face[0], face[vix + 1], face[vix + 2])
    prim.closePrimitive()
    return prim


def pv_to_p3(mesh: pv.PolyData) -> GeomNode:
    """Map a PyVista mesh to a Panda mesh.
    See
        - https://docs.panda3d.org/1.10/python/programming/internal-structures/procedural-generation
        - https://docs.pyvista.org/api/core/_autosummary/pyvista.PolyData.html
    for details.
    """
    vdata = GeomVertexData("mesh", GeomVertexFormat.getV3n3c4(), Geom.UHStatic)
    vdata.setNumRows(mesh.points.shape[0])
    vertexw = GeomVertexWriter(vdata, "vertex")
    normalw = GeomVertexWriter(vdata, "normal")
    colorw = GeomVertexWriter(vdata, "color")
    for vertex in mesh.points:
        vertexw.addData3(*vertex)
        normalw.addData3(0, 0, 1)
        colorw.addData4(0, 0, 1, 1)
    geom = Geom(vdata)
    prim_ix = 0
    while prim_ix < len(mesh.faces):
        stride = mesh.faces[prim_ix]
        face = mesh.faces[prim_ix + 1 : prim_ix + 1 + stride]
        prim_ix = prim_ix + 1 + stride
        if stride < 2:
            raise ValueError(f"undexpected mesh stride {stride}")
        elif stride == 2:
            prim = line(face)
        elif stride == 3:
            prim = triangle(face)
        else:
            prim = polygon(face)
        geom.addPrimitive(prim)
    node = GeomNode("gnode")
    node.addGeom(geom)
    return node


def make_node(scale=1, marker=0) -> pv.PolyData:
    """create a unit scale mesh representing a node
    Args:
        - scale: radius of solid's bounding sphere
    """
    return PlatonicSolid(marker, radius=scale / 2, center=[0, 0, 0])


def make_edge(
    kind="undirected", height=1, radius=0.4, nsides=9, theta=None, bend=None
) -> pv.PolyData:
    kwargs = dict(
        center=[0, 0, height / 2],
        direction=[0, 0, 1],
        height=height,
        radius=radius,
        resolution=nsides,
    )
    if kind == "undirected":
        ms = Cylinder(**kwargs)
    elif kind == "directed":
        ms = Arrow(**kwargs)
    else:
        raise ValueError(
            f'unsupported edge kind {kind}; must be "directed" or "undirected"'
        )
    return ms
