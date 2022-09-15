""" This source provides functionality for plotting nodes and edges of nx.Graph objects in 3D.
"""

from math import cos, pi, sin, sqrt
from pathlib import Path
from typing import Hashable, Optional, Union

import networkx as nx
import numpy as np
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import DirectionalLight, Material

EPS = 1e-6

Vector = Union[list[float], tuple[float, ...]]
Vec3 = tuple[float, float, float]
Vec4 = tuple[float, float, float, float]
Pos3 = dict[Hashable, np.ndarray]
default_edge = Path(__file__).parent / "data/unit_cylinder_base_at_0.egg"
default_node = Path(__file__).parent / "data/icosphere.egg"


class NxPlot(ShowBase):
    """This is the main class for plotting nx graphs. You should use the convenience functions that wrap this class for
    best results. The purpose of this Python package is to help you avoid having to deal directly with Panda3D, and
    using this class directly voids that.
    """

    def __init__(
        self,
        graph: nx.Graph,
        pos: Pos3,
        node_color: Vec4,
        node_size: Union[float, Vec3],
        edge_color: Vec4,
        edge_size: float,
        plot_axes=False,
        verbose=False,
        edge_fn=default_edge,
        node_fn=default_node,
    ):
        ShowBase.__init__(self)
        self.disableMouse()
        self.g = graph
        self.verbose = verbose

        if plot_axes:
            self.add_axes(edge_fn)

        for v in pos.values():
            if len(v) != 3:
                raise ValueError(
                    "Positions must be 3-dimensional."
                    " Try using the `dim=3` kwarg for computing positions from networkx layout functions."
                )
        self.pos = pos

        for hpr in [(0, 0, 0), (90, 0, 90), (0, 90, -90)]:
            dlight = DirectionalLight(f"my dlight {hpr}")
            dlnp = self.render.attachNewNode(dlight)
            dlnp.setHpr(*hpr)
            self.render.setLight(dlnp)

        for nd in self.g:
            self.add_node(nd, fn=node_fn, color=node_color, scale=node_size)

        for ed in self.g.edges:
            self.add_edge(ed, fn=edge_fn, color=edge_color, scale=edge_size)

        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    def add_edge(self, ed, fn: str, color: Vector, scale: float):
        edge = self.loader.loadModel(fn)
        edge.reparentTo(self.render)
        myMaterial = Material()
        myMaterial.setShininess(5.0)
        myMaterial.setBaseColor(color)
        edge.setMaterial(myMaterial, 1)

        p0, p1 = (self.pos[e] for e in ed)
        edge.setPos(*p0)
        dist = sqrt(((p0 - p1) ** 2).sum())
        scale_ = (scale, scale, dist)
        edge.setScale(*scale_)

        d = np.array(p1 - p0, dtype=float)
        for ix in np.argwhere(d == 0):
            d[ix] = EPS

        if self.verbose:
            print()
            print(f"color {color}")
            print(f"p0 {p0}")
            print(f"p1 {p1}")
            print(f"p1 - p0 {d}")
            print(f"dist {dist}")

        # FIRST pitch
        # The pitch rotates the Z-axis-aligned cylinder so that the far end of the cylinder is XY-coplanar with the
        # target node. The triangle is that having a height of d[2] and a hypotenuse of dist. Setting the height to d[2]
        # ensures that the tip of the hypotenuse will be co-XY-planar with the p1 node.
        if d[1] > 0:
            pitch = -np.arccos(d[2] / dist)
            assert pitch < 0
        else:
            pitch = np.arccos(d[2] / dist)
            assert pitch > 0
        pitch = pitch / pi * 180
        if self.verbose:
            print(f"pitch {pitch}")
        edge.setP(pitch)

        # SECOND heading
        # The heading rotates the cylinder end along an arc embedded in the XY plane at z=p1[2]. The angle is that of
        # the XY projected triangle formed by p0 and p1.
        heading = -np.arctan(d[0] / d[1])
        heading = heading / pi * 180
        if self.verbose:
            print(f"heading {heading}")
        edge.setH(heading)

        return edge

    def add_node(
        self,
        nd,
        fn: str,
        scale: Union[float, Vector],
        color: Vector,
    ):
        node = self.loader.loadModel(fn)
        node.reparentTo(self.render)
        node.setScale(scale)
        node.setPos(*self.pos[nd])

        myMaterial = Material()
        myMaterial.setShininess(5.0)
        myMaterial.setBaseColor(color)
        node.setMaterial(myMaterial, 1)

    def add_axes(self, fn):
        """put 3 cylinders in r:x:small, g:y:med, b:z:big; for debugging"""
        self.zax = self.loader.loadModel(fn)
        self.zax.reparentTo(self.render)
        self.zax.setColor(*(0, 0, 1, 1))
        self.zax.setScale(1)
        self.zax.setPos(0, 0, 0)
        self.xax = self.loader.loadModel(fn)
        self.xax.reparentTo(self.render)
        self.xax.setColor(*(1, 0, 0, 1))
        self.xax.setScale(0.8, 0.8, 1)
        self.xax.setPos(0, 0, 0)
        self.xax.setR(90)
        self.yax = self.loader.loadModel(fn)
        self.yax.reparentTo(self.render)
        self.yax.setColor(*(0, 1, 0, 1))
        self.yax.setScale(0.9, 0.9, 1)
        self.yax.setPos(0, 0, 0)
        self.yax.setP(-90)

    def spinCameraTask(self, task):
        length = 20  # how far away to be
        speed = 25.0  # how fast to spin
        angleDegrees = task.time * speed
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(
            length * sin(angleRadians), -length * cos(angleRadians), length / 2.0
        )
        self.camera.setHpr(angleDegrees, -length * 1.2, 0)
        return Task.cont


def plot_nx3d(
    g: nx.Graph,
    pos: Optional[Pos3] = None,
    node_color: Vec4 = (0.35, 0, 1, 1),
    node_size: Union[float, Vec3] = 0.65,
    edge_color: Vec4 = (0.2, 0.2, 0.2, 1),
    edge_size: float = 1.0,
    verbose=False,
    plot_axes=False,
):
    """Produce a panda3d object capable of rendering the nx.Graph.

    Use the return object as follows:
    .. highlight:: python
    .. code-block:: python

        my_app = plot_nx3d(...)
        my_app.run()

    Args:
        g: The graph you'd like to plot.
        pos: Positions of the nodes in the graph. If None, spring_layout will be used.
        node_color: RGBA color for the nodes. Currently homogeneous colors only suppported.
        node_size: Size of the nodes, either radius or XYZ dimensions.
        edge_color: RGBA color for the edges. Currently homogeneous colors only suppported.
        edge_size: Radius of the edges.
        verbose: Print diagnostic information to stdout.
        plot_axes: Show the XYZ axes in the 3D scene

    Returns:
        ShowBase: The Panda3D object that contains the (graphics) scene to be rendered
    """
    if pos is None:
        pos = nx.spring_layout(g, dim=3, scale=3, iterations=100)
    app = NxPlot(
        g,
        pos=pos,
        node_color=node_color,
        node_size=node_size,
        edge_color=edge_color,
        edge_size=edge_size,
        verbose=verbose,
        plot_axes=plot_axes,
    )
    return app


def plot(g: nx.Graph, debug=False):
    """Plot my graph now!

    This is where you should start. Calling this function on your graph will cause a pop-up
    containing the visualization to appear.

    Args:
        g (nx.Graph): The graph you'd like to plot.
        debug (bool): Set to debug mode, including diagnostic information printed to stdout and XYZ axes

    Returns:
        None
    """
    app = plot_nx3d(g, verbose=debug, plot_axes=debug)
    app.run()


def demo():
    """Runs a demo visualization. Good for checking that your installation worked."""
    g = nx.frucht_graph()
    plot(g, debug=0)
