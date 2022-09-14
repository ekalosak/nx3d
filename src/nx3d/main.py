""" This source provides functionality for plotting nodes and edges of nx.Graph objects.
TODO
- inline documentation
- readthedocs
- configurable colors and sizes
- interactive camera controls
- node labels
- edge labels
- support for DiGraph and MultiDiGraph
- tests (for the trig at least)
- animation?
- save to file
  (https://docs.panda3d.org/1.10/python/reference/direct.showbase.ShowBase?highlight=screenshot#direct.showbase.ShowBase.ShowBase.movie)
"""

from math import cos, pi, sin, sqrt
from pathlib import Path
from typing import Union

import networkx as nx
import numpy as np
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import DirectionalLight, Material

EPS = 1e-6

Vector = Union[list[float], tuple[float, ...]]
default_edge = Path(__file__).parent / "data/unit_cylinder_base_at_0.egg"
default_node = Path(__file__).parent / "data/icosphere.egg"


class NxPlot(ShowBase):
    """This is the main class for plotting nx graphs. You should use the convenience functions that wrap this class for
    best results.
    """

    def __init__(
        self,
        graph: nx.Graph,
        pos=None,
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

        if pos is None:
            pos = nx.spring_layout(self.g, dim=3, scale=3, iterations=100)
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
            color = (0, 1, 0, 1)
            self.add_node(nd, fn=node_fn, color=color, scale=0.45)

        for ed in self.g.edges:
            color = (0, 0, 1, 1)
            self.add_edge(ed, color=color, fn=edge_fn)

        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    def add_edge(self, ed, fn, color):
        edge = self.loader.loadModel(fn)
        edge.reparentTo(self.render)
        myMaterial = Material()
        myMaterial.setShininess(5.0)
        myMaterial.setBaseColor(color)
        edge.setMaterial(myMaterial, 1)

        p0, p1 = (self.pos[e] for e in ed)
        edge.setPos(*p0)
        dist = sqrt(((p0 - p1) ** 2).sum())
        scale = (1, 1, dist)
        edge.setScale(*scale)

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


def plot_nx3d(g: nx.Graph, verbose=False, plot_axes=False):
    """Produce a panda3d.showbase.ShowBase.ShowBase object capable of rendering the nx.Graph.
    :param graph: The graph you'd like to plot.
    :type graph: nx.Graph
    :param debug: Set to debug mode
    :type debug: bool
    :return: Panda3D ShowBase object that runs the visualization
    :rtype: ShowBase
    """
    app = NxPlot(g, verbose=verbose, plot_axes=plot_axes)
    return app


def plot(g: nx.Graph, debug=False):
    """Plot my graph now! This is where you should start. Calling this function on your graph will cause a pop-up
    containing the visualization to appear.
    :param graph: The graph you'd like to plot.
    :type graph: nx.Graph
    :param debug: Set to debug mode
    :type debug: bool
    :return: None
    :rtype: NoneType
    """
    app = plot_nx3d(g, verbose=debug, plot_axes=debug)
    app.run()


def demo():
    """Runs a demo visualization."""
    g = nx.frucht_graph()
    plot(g)
