""" This source provides functionality for plotting nodes and edges of nx.Graph objects in 3D.
"""

from math import atan, cos, isclose, pi, sin, sqrt
from pathlib import Path
from typing import Any, Callable, Optional, Union

import networkx as nx
import numpy as np
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    KeyboardButton,
    NodePath,
    PointLight,
    TextNode,
)

from nx3d import utils
from nx3d.types import Pos3, Vec3, Vec4

FILES = {
    "node": Path(__file__).parent / "data/icosphere.egg",
    "edge": Path(__file__).parent / "data/cylinder.egg",
    "edge_directed": Path(__file__).parent / "data/cone.egg",
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

DEFAULTS = dict(
    node_shape=0.9,
    node_color=(0.4, 0, 0.3, 1),
    node_text_color=(0, 1, 0, 1),
    edge_radius=1.75,
    edge_color=(0.3, 0.3, 0.3, 0.5),
    edge_text_color=(0, 1, 0, 1),
    speed_theta=96.0,
    speed_phi=96.0,
    speed_radius=36.0,
    light_direct=[{"hpr": (0, -20, 0)}, {"hpr": (180, -20, 0)}],
    light_ambient=[{"intensity": 0.3}],
    light_point=[{"pos": (0, 0, 0)}],
)


class Nx3D(ShowBase):
    """This class provides a networkx.Graph-based API for a lightweight 3D visualization.

    Usage:
        ```
        g = nx.frucht_graph();
        app = Nx3D(g, autolabel=True);
        app.run();
        ```

    Configuration is applied in the following order:
        1. Graph attributes e.g. g.nodes[...]['color']
        2. Arguments to this function

    Args:
        g: The graph you'd like to plot.
        pos: Positions of the nodes in the graph. If None, spring_layout will be used.
        node_color: Default RGBA color for the nodes.
        node_shape: Default shapes of the nodes, either radius or XYZ dimensions.
        node_labels: Map from the graph's nodes to string labels.
        edge_color: Default RGBA color for the edges. Currently homogeneous colors only suppported.
        edge_radius: Default radius of the edges.
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

    Returns:
        ShowBase: The Panda3D object capable of rendering the graph
    """

    def __init__(
        self,
        graph: nx.Graph,
        pos: Optional[Pos3] = None,
        node_color: Vec4 = DEFAULTS["node_color"],
        node_shape: Union[float, Vec3] = DEFAULTS["node_shape"],
        node_labels: dict = {},
        node_label_color: Vec4 = DEFAULTS["node_text_color"],
        edge_color: Vec4 = DEFAULTS["edge_color"],
        edge_radius: Union[float, list[float]] = DEFAULTS["edge_radius"],
        edge_labels: dict = {},
        edge_label_color: Vec4 = DEFAULTS["edge_text_color"],
        plot_axes=False,
        verbose=False,
        autolabel=False,
        mouse=False,
        state_trans_freq: float = 1.0,
        state_trans_func: Optional[Callable[[nx.Graph, int, float], Any]] = None,
    ):
        ShowBase.__init__(self)
        self.g = graph
        self.verbose = verbose

        node_fp = FILES.get("node")
        if isinstance(self.g, nx.MultiDiGraph):
            edge_fp = FILES.get("edge_directed_bent")
        elif isinstance(self.g, nx.MultiGraph):
            edge_fp = FILES.get("edge_bent")
        elif isinstance(self.g, nx.DiGraph):
            edge_fp = FILES.get("edge_directed")
        else:
            edge_fp = FILES.get("edge")
        if edge_fp is None or node_fp is None:
            raise NotImplementedError

        if pos is None:
            pos_scale = 2.0 * sqrt(len(self.g.nodes))
            pos = nx.spring_layout(self.g, dim=3, scale=pos_scale)
        if not all(len(p) == 3 for p in pos.values()):
            raise ValueError("pos must be 3d, use the dim=3 kwarg in nx layouts")
        self.pos = pos
        if autolabel:
            if verbose and any([edge_labels, node_labels]):
                print("overwriting labels, set autolabel False if undesired")
            node_labels = {nd: str(nd) for nd in self.g.nodes}
            edge_labels = {ed: str(ed) for ed in self.g.edges}

        # add some lights
        for i, dl in enumerate(DEFAULTS["light_direct"]):
            hpr = dl["hpr"]
            dlight = DirectionalLight(f"directional_light_{i}")
            dlnp = self.render.attachNewNode(dlight)
            self.render.setLight(dlnp)
            dlnp.setHpr(*hpr)
        for i, al in enumerate(DEFAULTS["light_ambient"]):
            intensity = al["intensity"]
            alight = AmbientLight(f"ambient_light_{i}")
            alnp = self.render.attachNewNode(alight)
            self.render.setLight(alnp)
            alnp.setColor(intensity)
        for i, pl in enumerate(DEFAULTS["light_point"]):
            pos = pl["pos"]
            plight = PointLight(f"point_light_{i}")
            plnp = self.render.attachNewNode(plight)
            self.render.setLight(plnp)
            plnp.setPos(*pos)

        for i, nd in enumerate(self.g.nodes):
            pid = f"node_{i}"
            model: NodePath = self._init_panda3d_model(pid, node_fp)
            model.reparentTo(self.render)
            model.setScale(node_shape)
            utils.set_color(model, node_color)
            model.setPos(*self.pos[nd])
            tpid = f"node_{i}_text"
            label = node_labels.get(nd)
            text, text_ = self._init_panda3d_text(tpid, label, node_label_color)
            text.reparentTo(model)
            text.setScale(tuple(1 / sc for sc in model.getScale()))
            text.setZ(model.getBounds().getRadius() * 1.1)
            self.g.nodes[nd]["model"] = model
            self.g.nodes[nd]["text_np"] = text
            self.g.nodes[nd]["text_tn"] = text_

        for i, ed in enumerate(self.g.edges):
            pid = f"edge_{i}"
            model: NodePath = self._init_panda3d_model(pid, edge_fp)
            model.reparentTo(self.render)
            utils.set_color(model, edge_color)
            # TODO use model.lookAt(node)
            # rotate into place
            p0, p1 = (self.pos[e] for e in ed)
            model.setPos(*p0)
            dist = sqrt(((p0 - p1) ** 2).sum())
            model.setScale(edge_radius, edge_radius, dist)
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
            model.setP(pitch)
            heading = -np.arctan(d[0] / d[1])
            heading = heading / pi * 180
            model.setH(heading)

            tpid = f"edge_{i}_text"
            label = edge_labels.get(ed)
            text, text_ = self._init_panda3d_text(tpid, label, edge_label_color)
            text.reparentTo(self.render)
            text.setPos(tuple((p0 + p1) / 2.0))
            self.g.edges[ed]["model"] = model
            self.g.edges[ed]["text_np"] = text
            self.g.edges[ed]["text_tn"] = text_

        self._init_gui(mouse)
        if plot_axes:
            self._init_axes(edge_fp)
        if not mouse:
            self._init_keyboard_camera()
        self._init_state_update(state_trans_freq, state_trans_func)

    def _init_state_update(
        self,
        state_trans_freq,
        state_trans_func,
    ):
        self.state_trans_func = state_trans_func
        if self.verbose:
            print(f"state_trans_func {self.state_trans_func}")
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
        self.taskMgr.doMethodLater(0.1, self.guiUpdateTask, "GuiUpdate")

    def _init_keyboard_camera(self):
        self.disableMouse()
        bd = self.render.getBounds()
        rad = np.linalg.norm(bd.getApproxCenter()) + bd.getRadius()
        fov = min(self.camLens.fov)  # angle in degrees
        radians_fov = fov / 180 * pi
        self.initial_camera_radius = rad / atan(radians_fov) * 1.8
        self.camera.setPos(0, -self.initial_camera_radius, 0)
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
        self.state_trans_func(self.g, task.frame, task.time)
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
        rot = "camera rotation: "
        pos = "camera position: "
        rot_ = rot + str(self.camera.getHpr())
        pos_ = pos + str(self.camera.getPos())
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
        speed_rad = DEFAULTS["speed_radius"]
        speed_phi = DEFAULTS["speed_phi"]
        speed_theta = DEFAULTS["speed_theta"]
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
