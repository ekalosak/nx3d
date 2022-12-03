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
    Arrow,
    CircularArc,
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


def remove_face(verts, mesh):
    for fc in faces(mesh):
        print(face)
        print(fc)
        return


# def glue(c1, c2) -> pv.PolyData:
#     """ glue the meshes together along some faces """
#     tf1 = faces(c1)[-2]  # top face of a pv.Cylinder is the penultimate
#     bf2 = faces(c2)[-1]  # bottom face of a pv.Cylinder is the last
#     nfvs = np.empty(c1.points[tf1].shape)
#     nfvs[:, :2] = c2.points[tf1, :2]
#     nfvs[:, 2] = np.average((c1.points[tf1, 2] + c2.points[bf2, 2]) / 2.)  # has the glued vaces verts
#     print(tf1)
#     print(c1.faces)
#     return
#     # vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 0.5, 0], [0, 0.5, 0]])
#     # mesh = pyvista.PolyData(vertices)
#     # faces = np.hstack([[3, 0, 1, 2], [3, 0, 3, 2]])
#     # mesh = pyvista.PolyData(vertices, faces)


def bent_cylinder(nsegments=3, radius=0.08):
    try:
        return CircularArc(
            [0, 0, 0], [0, 0, 1], [0, 0, 0.5], resolution=nsegments
        ).tube(radius=radius)
    except ValueError as e:
        raise ValueError(
            "Try adjusting nsegments, this may be a numerical error in CircularArc"
        ) from e


if __name__ == "__main__":
    ms = bent_cylinder(8)
    if 1:
        pl = pv.Plotter()
        pl.add_mesh(ms)
        pl.show_axes()
        pl.show(full_screen=False)


def bent_arrow(nsegments=3, **kwargs):
    ...


def make_edge(kind="g", height=1, radius=0.4, nsides=9) -> pv.PolyData:
    allowedkinds = ["g", "m", "d", "md"]
    if kind not in allowedkinds:
        raise ValueError(f"unsupported edge kind {kind}; must be one of {allowedkinds}")
    if kind == "g":
        ms = Cylinder(
            center=[0, 0, height / 2],
            direction=[0, 0, 1],
            height=height,
            radius=radius,
            resolution=nsides,
        )
    elif "d" in kind:
        ms = bent_arrow(
            direction=[0, 0, 1],
            tip_length=0.4,
            tip_radius=radius * 2,
            tip_resolution=nsides,
            shaft_radius=radius,
            shaft_resolution=nsides,
            scale=height,
        )
    else:
        ms = bent_cylinder(
            center=[0, 0, height / 2],
            direction=[0, 0, 1],
            height=height,
            radius=radius,
            resolution=nsides,
        )
    return ms
