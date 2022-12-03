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
from pyvista import PolyDataFilters as F
from pyvista.utilities.geometric_objects import (
    CircularArc,
    Cone,
    Cylinder,
    PlatonicSolid,
)


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


def make_node(radius=0.5, marker=0) -> pv.PolyData:
    return PlatonicSolid(marker, radius=radius, center=[0, 0, 0])


def faces(ms):
    ix = 0
    faces = []
    while ix < len(ms.faces):
        stride = ms.faces[ix]
        face = ms.faces[ix + 1 : ix + 1 + stride]
        faces.append(face)
        ix += 1 + stride
    return faces


def bent_cylinder(nsegments=8, nsides=8, radius=0.08, with_arc=False):
    ca = CircularArc([0, 0, 0], [0, 0, 1], [0, 0, 0.5], resolution=nsegments)
    try:
        ct = ca.tube(radius=radius, n_sides=nsides)
    except ValueError as e:
        raise ValueError(
            "Try adjusting nsegments, this may be a numerical error in CircularArc"
        ) from e
    return (ct, ca) if with_arc else ct


def bent_arrow(nsegments=8.0, nsides=8, radius=0.16, tip_length=0.4, **kwargs):
    tube, arc = bent_cylinder(nsegments, nsides, radius, **kwargs, with_arc=True)
    start, end = arc.points[-2], arc.points[-4]
    direction = start - end
    center = (start + end) / 2.0
    cone = Cone(
        center=center,
        direction=direction,
        height=tip_length,
        radius=radius * (1 + tip_length),
        capping=True,
        angle=None,
        resolution=nsides,
    )
    stem = F.boolean_difference(tube.triangulate(), cone.triangulate()).connectivity(
        largest=True
    )
    return stem + cone


def make_edge(kind="g", nsegments=8, nsides=8, radius=0.4) -> pv.PolyData:
    allowedkinds = ["g", "m", "d", "md"]
    if kind not in allowedkinds:
        raise ValueError(f"unsupported edge kind {kind}; must be one of {allowedkinds}")
    if kind == "g":
        ms = Cylinder(
            center=[0, 0, 0.5],
            direction=[0, 0, 1],
            height=1.0,
            radius=radius,
            resolution=nsides,
        )
        # ms = bent_cylinder(1, nsides, radius)
    elif "d" in kind:
        ms = bent_arrow(nsegments, nsides, radius, 1.9)
    else:
        ms = bent_cylinder(nsegments, nsides, radius)
    assert ms is not None
    return ms


if __name__ == "__main__":
    print("--- start demo")
    ms = bent_arrow(8, tip_length=0.3)
    pl = pv.Plotter()
    pl.add_mesh(ms)
    pl.show_axes()
    pl.show(full_screen=False)
    print("--- end demo")
