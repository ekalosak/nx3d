""" This source provides functionality for plotting nodes and edges of nx.Graph objects in 3D.
"""

from dataclasses import dataclass
from math import cos, isclose, pi, sin, sqrt, tan
from pathlib import Path
from typing import Any, Callable, Optional, Union

import networkx as nx
import numpy as np
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from numpy import linalg
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    KeyboardButton,
    NodePath,
    PointLight,
    TextNode,
    Vec3,
    Vec4,
)

from nx3d import utils
from nx3d.types import Pos3

FILES = {
    "node": Path(__file__).parent / "data/icosphere.bam",
    "edge": Path(__file__).parent / "data/undirected_edge_3.bam",
    "edge_directed": Path(__file__).parent / "data/bent_directed_edge_3.bam",
    "edge_bent": Path(__file__).parent / "data/bent_undirected_edge_3.bam",
    "edge_directed_bent": Path(__file__).parent / "data/bent_directed_edge_3.bam",
}

KEYBOARD_CONTROLLS = """
wasd - move camera around
io - zoom in and out
"""
MOUSE_CONTROLLS = """
mouse1 drag - move
mouse2 drag - zoom
mouse3 drag - rotate
"""

EPS = 1e-6  # numerical non-zero
UPS = 32  # updates per second to state


@dataclass
class Defaults:
    node_size: float = 1.0
    node_color: Vec4 = (0.4, 0, 0.3, 1)
    node_label_color: Vec4 = (0, 1, 0, 1)
    edge_color: Vec4 = (0.3, 0.3, 0.3, 0.5)
    edge_label_color: Vec4 = (0, 1, 0, 1)
    speed_theta: float = 96.0
    speed_phi: float = 96.0
    speed_radius: float = 36.0
    light_direct = [{"hpr": (0, -20, 0)}, {"hpr": (180, -20, 0)}]
    light_ambient = [{"intensity": 0.3}]
    light_point = [{"pos": (0, 0, 0)}]
    state_trans_freq: float = 1.0


class Nx3D(ShowBase):
    """This class provides a networkx.Graph-based API for a lightweight 3D visualization.

    Usage:
        ```
        g = nx.frucht_graph();
        app = Nx3D(g, autolabel=True);
        app.run();
        ```

    Configuration is applied in the following order:
        1. Special graph attributes e.g. g.nodes[...]['color']
        2. Arguments to this function

    The special graph attributes are:
        - 'color': panda3d.Vec4 with values in [0, 1]
        - 'pos': panda3d.Vec3 in x y z order
        - 'label': str
        - 'label_color': Vec4
        - 'pos': Vec3, note that dynamic positions aren't supported yet, see https://github.com/ekalosak/nx3d/issues/19
        for nodes:
            - 'shape': Vec3, same note as pos

    Note that these special attributes will be overwritten in place, especially when provided a state_trans_func.

    For more info, see :doc:`usage`.

    Args:
        g: The graph you'd like to plot.
        pos: Positions of the nodes in the graph. If None, spring_layout will be used.
        node_color: Default RGBA color for the nodes.
        node_size: Default size of the nodes.
        node_labels: Map from the graph's nodes to string labels.
        edge_color: Default RGBA color for the edges. Currently homogeneous colors only suppported.
        edge_labels: Map from the graph's edges to string labels.
        plot_axes: Show the XYZ axes in the 3D scene
        verbose: Print diagnostic information to stdout.
        autolabel: Use the string representation of the nx.Graphs' nodes and edges as labels.
        mouse: Use mouse control rather than keyboard control.
        state_trans_freq: How often, in seconds, to apply the <state_trans_func>.
        state_trans_func: A state transfer function for <g>'s state.
            Set attributes on graph components to update the render. If not None, the graph's nodes and edges must be
            annotated with 'color' and 'label' entries in the annotation dictionary i.e. g.nodes[nd]['color'] must exist for
            all nodes.
        kwargs: Passed to the base class ShowBase.

    Returns:
        panda3d.ShowBase: The Panda3D object capable of rendering the graph
        https://docs.panda3d.org/1.10/python/reference/direct.showbase.ShowBase?highlight=showbase#module-direct.showbase.ShowBase
    """

    def __init__(
        self,
        graph: Union[nx.Graph, nx.DiGraph],
        pos: Optional[Pos3] = None,
        node_color: Vec4 = Defaults.node_color,
        node_size: float = Defaults.node_size,
        node_labels: dict = {},
        node_label_color: Vec4 = Defaults.node_label_color,
        edge_color: Vec4 = Defaults.edge_color,
        edge_labels: dict = {},
        edge_label_color: Vec4 = Defaults.edge_label_color,
        plot_axes=False,
        verbose=False,
        autolabel=False,
        mouse=False,
        state_trans_freq: float = Defaults.state_trans_freq,
        state_trans_func: Optional[Callable[[nx.Graph, int, float], Any]] = None,
        **kwargs,
    ):
        ShowBase.__init__(self, **kwargs)
        self.g = graph
        self.verbose = verbose
        self.time_elapsed = 0.0

        # init file paths
        node_fp = FILES.get("node")
        if isinstance(graph, nx.MultiDiGraph):
            edge_fp = FILES.get("edge_directed_bent")
        elif isinstance(graph, nx.MultiGraph):
            edge_fp = FILES.get("edge_bent")
        elif isinstance(graph, nx.DiGraph):
            edge_fp = FILES.get("edge_directed")
        else:
            edge_fp = FILES.get("edge")
        if edge_fp is None or node_fp is None:
            raise NotImplementedError

        # init labels
        if autolabel:
            if verbose and any([edge_labels, node_labels]):
                print("overwriting labels, set autolabel False if undesired")
            node_labels = {nd: str(nd) for nd in graph.nodes}
            edge_labels = {ed: str(ed) for ed in graph.edges}

        # init positions
        if pos is None:
            if all("pos" in graph.nodes[nd] for nd in graph):
                pos = {nd: graph.nodes[nd]["pos"] for nd in graph}
            else:
                if verbose:
                    print("creating default pos")
                    if len(graph) > 256:
                        print("this may take a while for large graphs")
                pos_scale = 2.0 * sqrt(len(graph.nodes))
                pos = nx.spring_layout(graph, dim=3, scale=pos_scale)
        if not all(len(p) == 3 for p in pos.values()):
            raise ValueError("pos must be 3d, use the dim=3 kwarg in nx layouts")

        # init graph attributes
        for nd in graph.nodes:
            graph.nodes[nd]["pos"] = graph.nodes[nd].get("pos", pos[nd])
            graph.nodes[nd]["color"] = graph.nodes[nd].get("color", node_color)
            graph.nodes[nd]["shape"] = graph.nodes[nd].get("shape", node_color)
            graph.nodes[nd]["label"] = graph.nodes[nd].get(
                "label", node_labels.get(nd, "")
            )
            graph.nodes[nd]["label_color"] = graph.nodes[nd].get(
                "label_color", node_label_color
            )
        for ed in graph.edges:
            graph.edges[ed]["color"] = graph.edges[ed].get("color", edge_color)
            graph.edges[ed]["label"] = graph.edges[ed].get(
                "label", edge_labels.get(ed, "")
            )
            graph.edges[ed]["label_color"] = graph.edges[ed].get(
                "label_color", edge_label_color
            )

        self.initial_pos = {nd: graph.nodes[nd]["pos"] for nd in graph.nodes}

        # init lights
        for i, dl in enumerate(Defaults.light_direct):
            hpr = dl["hpr"]
            dlight = DirectionalLight(f"directional_light_{i}")
            dlnp = self.render.attachNewNode(dlight)
            self.render.setLight(dlnp)
            dlnp.setHpr(*hpr)
        for i, al in enumerate(Defaults.light_ambient):
            intensity = al["intensity"]
            alight = AmbientLight(f"ambient_light_{i}")
            alnp = self.render.attachNewNode(alight)
            self.render.setLight(alnp)
            alnp.setColor(intensity)
        for i, pl in enumerate(Defaults.light_point):
            pos = pl["pos"]
            plight = PointLight(f"point_light_{i}")
            plnp = self.render.attachNewNode(plight)
            self.render.setLight(plnp)
            plnp.setPos(*pos)

        # init 3d models
        for i, nd in enumerate(graph.nodes):
            pid = f"node_{i}"
            node: NodePath = self._init_panda3d_model(pid, node_fp)
            node.reparentTo(self.render)
            utils.set_color(node, graph.nodes[nd]["color"])
            node.setPos(*graph.nodes[nd]["pos"])
            tpid = f"node_{i}_text"
            text, text_ = self._init_panda3d_text(
                tpid, graph.nodes[nd]["label"], graph.nodes[nd]["label_color"]
            )
            text.reparentTo(node)
            text.setScale(tuple(1 / sc for sc in node.getScale()))
            text.setZ(node.getBounds().getRadius() * 1.1)
            graph.nodes[nd]["model"] = node
            graph.nodes[nd]["text_np"] = text
            graph.nodes[nd]["text_tn"] = text_

        for i, ed in enumerate(graph.edges):
            if isinstance(graph, nx.MultiGraph):
                n0, n1, nk = ed
            else:
                n0, n1 = ed
            pid = f"edge_{i}"
            edge: NodePath = self._init_panda3d_model(pid, edge_fp)
            edge.reparentTo(self.render)
            utils.set_color(edge, graph.edges[ed]["color"])
            # rotate into place
            p0 = graph.nodes[n0]["pos"]
            p1 = graph.nodes[n1]["pos"]
            edge.setPos(*p0)
            dist = linalg.norm(p0 - p1)
            edge.setScale(1, 1, dist / 2)  # models have Z size of 2
            d = np.array(p1 - p0, dtype=float)
            for ix in np.argwhere(d == 0):
                d[ix] = EPS
            if d[1] > 0:
                pitch = -np.arccos(d[2] / dist)
                assert pitch < 0
            else:
                pitch = np.arccos(d[2] / dist)
                assert pitch > 0
            pitch = pitch / pi * 180
            edge.setP(pitch)
            heading = -np.arctan(d[0] / d[1])
            heading = heading / pi * 180
            edge.setH(heading)
            if isinstance(graph, nx.MultiGraph):
                edge.setH(edge, nk / graph.graph["k"] * 360)

            # TODO use lookAt

            tpid = f"edge_{i}_text"
            text, text_ = self._init_panda3d_text(
                tpid, graph.edges[ed]["label"], graph.edges[ed]["label_color"]
            )
            text.reparentTo(self.render)
            text.setPos(tuple((p0 + p1) / 2.0))
            graph.edges[ed]["model"] = edge
            graph.edges[ed]["text_np"] = text
            graph.edges[ed]["text_tn"] = text_

        self._init_camera()
        self._init_gui(mouse)
        if plot_axes:
            self._init_axes(FILES["edge"])
        if not mouse:
            self._init_keyboard_camera()
        self._init_state_update_task(state_trans_freq, state_trans_func)

    def _init_camera(self):
        self.disableMouse()
        bd = self.render.getBounds()
        rad = np.linalg.norm(bd.getApproxCenter()) + bd.getRadius()
        fov = min(self.camLens.fov) if self.camLens else 45
        radians_fov = fov / 180 * pi
        self.initial_camera_radius = rad / tan(radians_fov) * 1.75
        if self.camera:
            self.camera.setPos(0, -self.initial_camera_radius, 0)
        self.enableMouse()

    def _init_state_update_task(
        self,
        state_trans_freq,
        state_trans_func,
    ):
        self.state_trans_func = state_trans_func
        if self.state_trans_func:
            self.taskMgr.doMethodLater(
                state_trans_freq, self.stateUpdateTask, "StateUpdate"
            )

    def _init_panda3d_model(
        self,
        pid: str,
        egg_filepath: Path,
        scale: Union[float, Vec3] = 1.0,
        color: Optional[Vec4] = None,
    ):
        if self.verbose:
            print(f"loading model: {egg_filepath}")
        _model = self.loader.loadModel(egg_filepath)
        model = NodePath(pid)
        _model.reparentTo(model)
        model.setScale(scale)
        if color:
            utils.set_color(model, color)
        return model

    def _init_panda3d_text(
        self,
        text_id: str,
        label: Optional[str] = None,
        color: Optional[Vec4] = None,
    ) -> NodePath:
        if label is None:
            label = ""
        _text = TextNode(text_id)
        _text.setText(label)
        text: NodePath = self.render.attachNewNode(_text)
        text.setBillboardPointEye()  # face text towards camera
        utils.set_color(text, color)
        return text, _text

    def _init_gui(self, mouse: bool, scale=0.07):
        help_text = MOUSE_CONTROLLS if mouse else KEYBOARD_CONTROLLS
        help_text = help_text.strip()
        self.gui_fixed_lines = []
        self.gui_updatable_lines = {}
        for i, line in enumerate(help_text.split("\n")):
            label = self._make_gui_text(line, i, scale, color=(1, 1, 0, 1))
            self.gui_fixed_lines.append(label)
        self.taskMgr.add(self.guiUpdateTask, "GuiUpdate")

    def _init_keyboard_camera(self):
        self.disableMouse()
        self.cam_radius = self.initial_camera_radius
        self.cam_theta = 0.0
        self.cam_phi = 0.0
        self.taskMgr.add(self.keyboardCameraTask, "KeyboardCameraTask")

    def _init_axes(self, fn):
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

    def _make_gui_text(self, text: str, i: int, scale=0.07, color=(1, 1, 1, 1)):
        """Make gui line <i>
        https://github.com/panda3d/panda3d/blob/master/samples/asteroids/main.py#L86
        """
        return OnscreenText(
            text=text,
            parent=self.a2dTopLeft,
            pos=(scale, -0.06 * i - 0.1),
            fg=color,
            align=TextNode.ALeft,
            shadow=(0, 0, 0, 0.5),
            scale=scale,
        )

    def stateUpdateTask(self, task):
        """main state update loop"""
        if self.verbose:
            print(f"stateUpdateTask from {task.name}")
        self.state_trans_func(self.g, task.frame, task.delayTime)
        for elm in utils.all_elements(self.g):
            assert all(isinstance(x, NodePath) for x in (elm["model"], elm["text_np"]))
            assert isinstance(elm["text_tn"], TextNode)
            assert all(isinstance(c, (float, int)) for c in elm["color"])
            assert len(elm["color"]) == 4
            assert isinstance(elm["label"], str)
            utils.set_color(elm["model"], elm["color"])
            elm["text_tn"].setText(elm["label"])
        return Task.again

    def guiUpdateTask(self, task):
        """write diagnostic info to gui"""
        if self.camera is None:
            return
        rot = "camera rotation: "
        pos = "camera position: "
        tim = "time: "
        rot_ = rot + str(self.camera.getHpr())
        pos_ = pos + str(self.camera.getPos())
        self.time_elapsed += task.time
        tim_ = tim + f"{self.time_elapsed:.0f}sec"
        # FIXME init rot and pos in _init_gui
        if rot not in self.gui_updatable_lines:
            self.gui_updatable_lines[rot] = self._make_gui_text(
                rot_, len(self.gui_fixed_lines), 0.07
            )
        else:
            self.gui_updatable_lines[rot].setText(rot_)
        if pos not in self.gui_updatable_lines:
            self.gui_updatable_lines[pos] = self._make_gui_text(
                pos_, len(self.gui_fixed_lines) + 1, 0.07
            )
        else:
            self.gui_updatable_lines[pos].setText(pos_)
        if tim not in self.gui_updatable_lines:
            self.gui_updatable_lines[tim] = self._make_gui_text(
                tim_, len(self.gui_fixed_lines) + 2, 0.07
            )
        else:
            self.gui_updatable_lines[tim].setText(tim_)
        return task.again

    def keyboardCameraTask(self, task):
        """handle keyboard input that spins the camera"""
        # first adjust camera speed
        left_button = KeyboardButton.ascii_key("a")
        right_button = KeyboardButton.ascii_key("d")
        up_button = KeyboardButton.ascii_key("w")
        down_button = KeyboardButton.ascii_key("s")
        in_button = KeyboardButton.ascii_key("i")
        out_button = KeyboardButton.ascii_key("o")
        is_down = self.mouseWatcherNode.is_button_down
        dt = globalClock.get_dt()  # noqa: F821
        speed_rad = Defaults.speed_radius
        speed_phi = Defaults.speed_phi
        speed_theta = Defaults.speed_theta
        delta_rad = 0
        delta_phi = 0
        delta_theta = 0
        if is_down(left_button):
            delta_theta += speed_theta * dt
        if is_down(right_button):
            delta_theta -= speed_theta * dt
        if is_down(up_button):
            delta_phi += speed_phi * dt
        if is_down(down_button):
            delta_phi -= speed_phi * dt
        if is_down(in_button):
            delta_rad -= speed_rad * dt
        if is_down(out_button):
            delta_rad += speed_rad * dt
        # calculate new radius
        self.cam_radius = max(self.cam_radius + delta_rad, 2.5)
        # NOTE angles are in degrees unless labeled as radians
        # calculate phi
        self.cam_phi = self.cam_phi + delta_phi
        radians_phi = self.cam_phi * pi / 180
        # calculate heading
        self.cam_theta += delta_theta
        radians_theta = self.cam_theta * pi / 180
        # apply translation
        x = self.cam_radius * sin(radians_theta) * cos(radians_phi)
        y = -self.cam_radius * cos(radians_theta) * cos(radians_phi)
        z = self.cam_radius * sin(radians_phi)
        self.camera.setPos(x, y, z)
        assert isclose(
            sqrt(sum(self.camera.getPos() ** 2)), self.cam_radius, abs_tol=0.1
        )
        # apply rotation
        self.camera.setP(-self.cam_phi)
        self.camera.setH(self.cam_theta)
        return Task.cont
