""" This source provides functionality for plotting nodes and edges of nx.Graph objects in 3D.
"""

from math import cos, pi, sin, sqrt
from pathlib import Path
from typing import Hashable, Optional, Union

import networkx as nx
import numpy as np
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import DirectionalLight, Material, NodePath, TextNode

EPS = 1e-6

Vector = Union[list[float], tuple[float, ...]]
Vec3 = tuple[float, float, float]
Vec4 = tuple[float, float, float, float]
Pos3 = dict[Hashable, np.ndarray]
default_edge = Path(__file__).parent / "data/unit_cylinder_base_at_0.egg"
default_node = Path(__file__).parent / "data/icosphere.egg"


class NxPlot(ShowBase):
    """This is the main class for plotting nx graphs.
    Args:
        graph: the graph to be plotted, currently only nx.Graph is supported.
        pos: the position dictionary mapping nodes to (x,y,z) tuples of floats.
    """

    def __init__(
        self,
        graph: nx.Graph,
        pos: Pos3,
        node_color: Union[Vec4, list[Vec4]],
        node_size: Union[float, Vec3, list[float], list[Vec3]],
        node_labels: dict,
        node_label_color: Vec4,
        edge_color: Union[Vec4, list[Vec4]],
        edge_size: Union[float, list[float]],
        edge_labels: dict,
        edge_label_color: Vec4,
        plot_axes=False,
        verbose=False,
        edge_fn=default_edge,
        node_fn=default_node,
        pos_update_function=None,
    ):
        ShowBase.__init__(self)
        self.disableMouse()
        self.g = graph
        self.verbose = verbose
        self.pos = pos
        self.pos_update_function = pos_update_function

        for v in self.pos.values():
            if len(v) != 3:
                raise ValueError(
                    "Positions must be 3-dimensional."
                    " Try using the `dim=3` kwarg for computing positions from networkx layout functions."
                )

        if plot_axes:
            self.add_axes(edge_fn)

        # add some lights TODO be thouhtful about lighting the scene
        for hpr in [(0, 0, 0), (90, 0, 90), (0, 90, -90)]:
            dlight = DirectionalLight(f"my dlight {hpr}")
            dlnp = self.render.attachNewNode(dlight)
            dlnp.setHpr(*hpr)
            self.render.setLight(dlnp)

        for nd in self.g.nodes:
            node_label = node_labels.get(nd)
            self.add_node(
                nd,
                egg_filepath=node_fn,
                color=node_color,
                scale=node_size,
                label=node_label,
                label_color=node_label_color,
            )

        for ed in self.g.edges:
            edge_label = edge_labels.get(ed)
            self.add_edge(
                ed,
                egg_filepath=edge_fn,
                color=edge_color,
                scale=edge_size,
                label=edge_label,
                label_color=edge_label_color,
            )

        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    def _make_text(
        self, node_path: NodePath, text_id: str, label: str, color: Vec4
    ) -> NodePath:
        text = TextNode(text_id)
        text.setText(label)
        text.setTextColor(*color)
        tnd: NodePath = self.render.attachNewNode(text)
        tnd.setBillboardAxis()  # face text towards camera
        return tnd

    def _set_color(self, node_path, color):
        myMaterial = Material()
        myMaterial.setShininess(5.0)
        myMaterial.setBaseColor(color)
        node_path.setMaterial(myMaterial, 1)

    def _make_object(
        self,
        egg_filepath: str,
        id_str: str,
        scale: float = 1.0,
        color: Optional[Vec4] = None,
        label: Optional[str] = None,
        label_color: Optional[Vec4] = None,
        verbose=False,
    ) -> tuple[NodePath, Optional[NodePath]]:
        if verbose:
            print(f"loading model: {egg_filepath}")
        ob = self.loader.loadModel(egg_filepath)
        if color:
            self._set_color(ob, color)
        if label:
            text_id = f"{id_str}_text"
            text_node = self._make_text(ob, text_id, label, label_color)
        else:
            text_node = None
        return ob, text_node

    def add_edge(
        self,
        ed,
        egg_filepath: str,
        color: Vector,
        scale: float,
        label: Optional[str] = None,
        label_color: Optional[Vec4] = None,
    ):
        edge, text = self._make_object(
            egg_filepath, str(ed), scale, color, label, label_color
        )
        assert isinstance(edge, NodePath)
        assert isinstance(text, NodePath) or text is None
        edge.reparentTo(self.render)

        p0, p1 = (self.pos[e] for e in ed)
        edge.setPos(*p0)
        dist = sqrt(((p0 - p1) ** 2).sum())
        edge.setScale(scale, scale, dist)
        if text:
            text.setScale(1 / scale, 1 / scale, 1 / dist)

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

        if text:
            text.reparentTo(edge)

        return edge

    def add_node(
        self,
        nd,
        egg_filepath: str,
        scale: Union[float, Vector],
        color: Vector,
        label: Optional[str] = None,
        label_color: Optional[Vec4] = None,
    ):
        node, text = self._make_object(
            egg_filepath, str(nd), scale, color, label, label_color
        )
        node.reparentTo(self.render)
        if text:
            text.reparentTo(node)
        node.setPos(*self.pos[nd])

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
        length = 30  # how far away to be
        speed = 8.0  # how fast to spin
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

    g = nx.grid_2d_graph(16)
    my_app = plot_nx3d(g)
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
        # pos_scale = 16
        pos_scale = 2.0 * sqrt(len(g.nodes))
        pos = nx.spring_layout(g, dim=3, scale=pos_scale)
    app = NxPlot(
        g,
        pos=pos,
        node_color=node_color,
        node_size=node_size,
        node_labels={nd: str(nd) for nd in g.nodes},
        node_label_color=node_color,
        edge_color=edge_color,
        edge_size=edge_size,
        edge_labels={ed: str(ed) for ed in g.edges},
        edge_label_color=edge_color,
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
