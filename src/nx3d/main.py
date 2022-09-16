""" This source provides functionality for plotting nodes and edges of nx.Graph objects in 3D.
"""

from math import cos, pi, sin, sqrt
from pathlib import Path
from typing import Any, Callable, Hashable, Optional, Union

import networkx as nx
import numpy as np
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import DirectionalLight, Material, NodePath, TextNode

KEYBOARD_CONTROLLS = """
wasd - move camera around
qe - zoom in and out
r - reset
"""
MOUSE_CONTROLLS = """
mouse1 drag - move
mouse2 drag - zoom
mouse3 drag - rotate
r - reset
"""


EPS = 1e-6

Vector = Union[list[float], tuple[float, ...]]
Vec3 = tuple[float, float, float]
Vec4 = tuple[float, float, float, float]
Colors = Union[Vec4, list[Vec4]]
Shapes = Union[float, Vec3, list[float], list[Vec3]]
Pos3 = dict[Hashable, np.ndarray]

# NOTE using dict for default node rather than dataclass because @dataclass(kw_only) is 3.10, want to support 3.9
default_node = {
    "filepath": Path(__file__).parent / "data/icosphere.egg",
    "shape": 0.45,
    "color": (0.3, 0, 0.3, 1),
    "text_color": (1, 1, 1, 1),
}
default_edge = {
    "filepath": Path(__file__).parent / "data/unit_cylinder_base_at_0.egg",
    "radius": 0.75,
    "color": (0.2, 0.2, 0.2, 1),
    "text_color": (0, 1, 1, 1),
}


class NxPlot(ShowBase):
    """The main class for plotting networkx graphs using panda3d.

    NxPlot is a panda3d object capable of rendering the nx.Graph.
    Use the object as follows:

    g = nx.frucht_graph();
    app = NxPlot(g);
    app.run();

    Args:
        g: The graph you'd like to plot.
        pos: Positions of the nodes in the graph. If None, spring_layout will be used.
        node_color: RGBA color for the nodes. Currently homogeneous colors only suppported.
        node_shape: Shapes of the nodes, either radius or XYZ dimensions, singular or plural.
        node_labels: Map from the graph's nodes to string labels.
        edge_color: RGBA color for the edges. Currently homogeneous colors only suppported.
        edge_radius: Radius of the edges, singular or plural.
        edge_labels: Map from the graph's edges to string labels.
        plot_axes: Show the XYZ axes in the 3D scene
        verbose: Print diagnostic information to stdout.
        autolabel: Use the string representation of the nx.Graphs' nodes and edges as labels.
        graph_state_func: This function will be called every <state_trans_freq> seconds to update the internal nx.Graph.
        state_trans_freq: How often, in seconds, to apply the graph_state_func.

    Returns:
        ShowBase: The Panda3D object capable of rendering the graph
    """

    def __init__(
        self,
        graph: nx.Graph,
        pos: Optional[Pos3] = None,
        node_color: Colors = default_node["color"],
        node_shape: Shapes = default_node["shape"],
        node_labels: dict = {},
        node_label_color: Colors = default_node["text_color"],
        edge_color: Colors = default_edge["color"],
        edge_radius: Union[float, list[float]] = default_edge["radius"],
        edge_labels: dict = {},
        edge_label_color: Colors = default_edge["text_color"],
        plot_axes=False,
        verbose=False,
        autolabel=False,
        cam_mouse_control=False,
        node_fn=default_node["filepath"],
        edge_fn=default_edge["filepath"],
        graph_state_func: Optional[Callable[[nx.Graph], Any]] = None,
        graph_trans_frq: Optional[float] = None,
        initial_camera_speed=24.0,
    ):
        ShowBase.__init__(self)

        self.g = graph
        self.verbose = verbose
        self.graph_state_func = graph_state_func
        self.cam_speed = initial_camera_speed
        if pos is None:
            pos_scale = 2.0 * sqrt(len(self.g.nodes))
            pos = nx.spring_layout(self.g, dim=3, scale=pos_scale)
            self.pos = pos
        if autolabel:
            if verbose and any([x for x in [edge_labels, node_labels]]):
                print(
                    "overwriting node and edge labels, set autolabel to False if undesired"
                )
            node_labels = {nd: str(nd) for nd in self.g.nodes}
            edge_labels = {ed: str(ed) for ed in self.g.edges}

        for v in self.pos.values():
            if len(v) != 3:
                raise ValueError(
                    "Positions must be 3-dimensional."
                    " Try using the `dim=3` kwarg for computing positions from networkx layout functions."
                )

        if plot_axes:
            self.add_axes(edge_fn)

        # add some lights
        for hpr in [(0, 0, 0), (0, 0, 180), (180, 180, 180), (180, 0, 180)]:
            dlight = DirectionalLight(f"my dlight {hpr}")
            dlnp = self.render.attachNewNode(dlight)
            self.render.setLight(dlnp)
            dlnp.setHpr(*hpr)

        for nd in self.g.nodes:
            node_label = node_labels.get(nd)
            self._add_node(
                nd,
                egg_filepath=node_fn,
                color=node_color,
                scale=node_shape,
                label=node_label,
                label_color=node_label_color,
            )

        for ed in self.g.edges:
            edge_label = edge_labels.get(ed)
            self._add_edge(
                ed,
                egg_filepath=edge_fn,
                color=edge_color,
                scale=edge_radius,
                label=edge_label,
                label_color=edge_label_color,
            )

        self._init_gui(cam_mouse_control)
        if cam_mouse_control:
            self._init_mouse_camera()
        else:
            self._init_keyboard_camera()

    def _init_keyboard_camera(self):
        self.disableMouse()
        self.taskMgr.add(self.keyboardCameraTask, "KeyboardCameraTask")

    def _init_mouse_camera(self):
        graph_bounds = self.render.getBounds()
        radius = graph_bounds.getRadius()
        self.cam.setY(-radius)

    def _init_gui(self, cam_mouse_control, scale=0.07):
        help_text = MOUSE_CONTROLLS if cam_mouse_control else KEYBOARD_CONTROLLS
        help_text = help_text.strip()
        text = TextNode("gui")
        text.setText(help_text)
        textNodePath = self.render2d.attachNewNode(text)
        textNodePath.setScale(0.07)
        textNodePath.setPos(-1, 0, 0.9)
        self.gui = textNodePath

    def _make_text(
        self, node_path: NodePath, text_id: str, label: str, color: Vec4
    ) -> NodePath:
        text = TextNode(text_id)
        text.setText(label)
        tnd: NodePath = self.render.attachNewNode(text)
        tnd.setBillboardAxis()  # face text towards camera
        self._set_color(tnd, color)
        return tnd

    def _set_color(self, node_path, color):
        mat = Material()
        mat.setShininess(5.0)
        mat.setBaseColor(color)
        node_path.setMaterial(mat, 1)

    def _make_graph_component(
        self,
        egg_filepath: str,
        id_str: str,
        scale: float = 1.0,
        color: Optional[Vec4] = None,
        label: Optional[str] = None,
        label_color: Optional[Vec4] = None,
        verbose=False,
    ) -> tuple[NodePath, Optional[NodePath]]:
        """construct a 3D graph element representing (edge, edge_label) or (node, node_label)"""
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

    def _add_edge(
        self,
        ed,
        egg_filepath: str,
        color: Vector,
        scale: float,
        label: Optional[str] = None,
        label_color: Optional[Vec4] = None,
    ):
        edge, text = self._make_graph_component(
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

    def _add_node(
        self,
        nd,
        egg_filepath: str,
        scale: Union[float, Vector],
        color: Vector,
        label: Optional[str] = None,
        label_color: Optional[Vec4] = None,
    ):
        node, text = self._make_graph_component(
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

    def guiUpdateTask(self, task):
        ...

    def keyboardCameraTask(self, task):
        length = self.render.getBounds().getRadius()
        angleDegrees = task.time * self.cam_speed
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(
            length * sin(angleRadians),
            -length * cos(angleRadians),
            0,
        )
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont


def plot(g: nx.Graph, debug=False, **kwargs):
    """Plot my graph now!

    This is where you should start. Calling this function on your graph will cause a pop-up
    containing the visualization to appear.

    Args:
        g (nx.Graph): The graph you'd like to plot.
        debug (bool): Set to debug mode, entailing rendered and stdout debugging information, negates other debug-like args
        kwargs: Passed to main class initialization

    Returns:
        None
    """
    if debug:
        for kw in ["verbose", "plot_axes", "autolabel", "cam_mouse_control"]:
            kwargs[kw] = not kwargs.get(kw, False)
    # FIXME
    kwargs["cam_mouse_control"] = 0
    app = NxPlot(g, **kwargs)
    app.run()


def demo(debug=False, **kwargs):
    """Runs a demo visualization. Good for checking that your installation worked."""
    g = nx.frucht_graph()
    plot(g, debug, **kwargs)
