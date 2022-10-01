""" This source provides functionality for plotting nodes and edges of nx.Graph objects in 3D.
"""

import os
import sys
from dataclasses import dataclass
from math import cos, isclose, pi, sin, sqrt, tan
from pathlib import Path
from typing import Any, Callable, Optional, Union

import networkx as nx
import numpy as np
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from loguru import logger
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
    WindowProperties,
    loadPrcFileData,
)

from nx3d import utils
from nx3d.types import Pos3

DO_LS = False
logger.remove()
if os.environ.get("TRACE"):
    logger.add(sys.stderr, level="TRACE")
    DO_LS = True
elif os.environ.get("DEBUG"):
    logger.add(sys.stderr, level="DEBUG")
elif os.environ.get("INFO"):
    logger.add(sys.stderr, level="INFO")


loadPrcFileData("", "background-color .03")

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
    speed_theta: float = 82.0
    speed_phi: float = 82.0
    speed_radius: float = 36.0
    lights = [
        ("directional", "nodes", {"hpr": (180, -20, 180), "color": 0.3}),
        ("directional", "edges", {"hpr": (180, -20, 0), "color": 0.1}),
        ("ambient", "both", {"color": 0.9}),
        ("point", "both", {"color": 0.5, "pos": (0, 0, 0)}),
    ]
    background_ambient_light_intensity: float = 1.0
    state_trans_delay: float = 1.0


class Nx3D(ShowBase):
    """This class provides a networkx.Graph-based API for a lightweight 3D visualization.

    Usage:
        ```
        g = nx.frucht_graph();
        app = Nx3D(g, autolabel=True);
        app.run();
        ```

    Configuration is applied in the following order:
        1. Render attributes on the nodes and edges e.g. g.nodes[...]['color']
        2. Arguments to this function

    The render attributes are:
        - 'color': panda3d.Vec4 with values in [0, 1]
        - 'pos': panda3d.Vec3 in x y z order
        - 'label': str
        - 'label_color': Vec4
        - 'pos': Vec3, note that dynamic positions aren't supported yet, see https://github.com/ekalosak/nx3d/issues/19

        for nodes there is an extra one:
            - 'shape': Vec3, same note as pos

    Note that these render attributes will typically be overwritten in place.

    For more info, see :doc:`usage`.

    Args:
        g: The graph you'd like to plot.
        pos: Positions of the nodes in the graph. If None, spring_layout will be used.
        node_color: Default RGBA color for the nodes.
        node_size: Default size of the nodes.
        node_labels: Map from the graph's nodes to string labels.
        edge_color: Default RGBA color for the edges. Currently homogeneous colors only suppported.
        edge_labels: Map from the graph's edges to string labels.
        lights: Configure the lighting in your scene, see Default for example
        state_trans_delay: How often, in seconds, to apply the <state_trans_func>.
        state_trans_func: A state transfer function for <g>'s state.
            Set attributes on graph components to update the render. If not None, the graph's nodes and edges must be
            annotated with 'color' and 'label' entries in the annotation dictionary i.e. g.nodes[nd]['color'] must exist for
            all nodes.
        nofilter: Don't use any filters - can help your framerate for large graphs.
        nogui: Don't show help or diagnostic information on screen - for a cleaner look.
        plot_axes: Show the XYZ axes in the 3D scene
        autolabel: Use the string representation of both the nx.Graph's nodes and edges as labels.
            Autolabel supercedes autolabel_nodes and autolabel_edges when True.
        autolabel_nodes: Use the string representation of the nx.Graph's nodes as labels.
        autolabel_edges: Use the string representation of the nx.Graph's edges as labels.
        mouse: Use mouse control rather than keyboard control.
        windowsize: Tuple of height, width of the popup window.
        windowtitle: Title of the popup window.
        kwargs: Passed to the base class ShowBase.

    Returns:
        panda3d.ShowBase: The Panda3D object capable of rendering the graph
        https://docs.panda3d.org/1.10/python/reference/direct.showbase.ShowBase?highlight=showbase#module-direct.showbase.ShowBase
    """

    def __init__(
        self,
        graph: Union[nx.Graph, nx.DiGraph] = nx.tutte_graph(),
        pos: Optional[Pos3] = None,
        node_color: Vec4 = Defaults.node_color,
        node_size: float = Defaults.node_size,
        node_labels: dict = {},
        node_label_color: Vec4 = Defaults.node_label_color,
        edge_color: Vec4 = Defaults.edge_color,
        edge_labels: dict = {},
        edge_label_color: Vec4 = Defaults.edge_label_color,
        lights: list[tuple[str, str, dict]] = Defaults.lights,
        state_trans_delay: float = Defaults.state_trans_delay,
        state_trans_func: Optional[Callable[[nx.Graph, int, float], Any]] = None,
        nofilter=False,
        nogui=False,
        plot_axes=False,
        autolabel=False,
        autolabel_nodes=False,
        autolabel_edges=False,
        mouse=False,
        windowsize=(650, 450),
        windowtitle="Nx3D",
        **kwargs,
    ):
        ShowBase.__init__(self, **kwargs)
        logger.info("")
        self.g = graph
        self.time_elapsed = 0.0
        self._latest_key = None

        if self.win:
            properties = WindowProperties()
            properties.setTitle(windowtitle)
            properties.setSize(*windowsize)
            properties.setOrigin(0, 0)
            self.win.requestProperties(properties)

        self._init_filepaths()
        if autolabel:
            autolabel_nodes = autolabel_edges = True
        self._init_positions(pos)
        self._init_render_attrs(
            node_color,
            edge_color,
            node_labels,
            edge_labels,
            node_label_color,
            edge_label_color,
            autolabel_edges,
            autolabel_nodes,
        )
        self._init_lights(lights)
        self._init_models()
        self._init_camera()
        if not nofilter:
            self._init_filters()
        if not nogui:
            self._init_gui(mouse)
        self._init_keyboard_input()
        if plot_axes:
            self._init_axes(FILES["edge"])
        if not mouse:
            self._init_keyboard_camera()
        self._init_state_update_task(state_trans_delay, state_trans_func)

    def _init_render_attrs(
        self,
        node_color,
        edge_color,
        node_labels,
        edge_labels,
        node_label_color,
        edge_label_color,
        autolabel_edges,
        autolabel_nodes,
    ):
        self.node_labels, self.edge_labels = self._preprocess_labels(
            node_labels, edge_labels, autolabel_edges, autolabel_nodes
        )
        graph = self.g
        for n, nd in graph.nodes(data=True):
            nd["color"] = nd.get("color", node_color)
            nd["shape"] = nd.get("shape", node_color)
            nd["label"] = nd.get("label", self.node_labels.get(n, ""))
            nd["label_color"] = nd.get("label_color", node_label_color)
        for u, v, ed in graph.edges.data():
            ed["color"] = ed.get("color", edge_color)
            ed["label"] = ed.get("label", self.edge_labels.get((u, v), ""))
            ed["label_color"] = ed.get("label_color", edge_label_color)

    def _init_positions(self, pos):
        graph = self.g
        if pos is None:
            if all("pos" in graph.nodes[n] for n in graph):
                logger.debug("graph positions pre-initialized")
                pos = {n: graph.nodes[n]["pos"] for n in graph}
            else:
                logger.debug(
                    "graph positions not _all_ pre-initialized creating default pos"
                )
                if len(graph) > 256:
                    logger.warning(
                        f"initializing positions may take a while for large graphs n>256, len(g)={len(graph)}"
                    )
                pos_scale = 2.0 * sqrt(len(graph.nodes))
                pos = nx.spring_layout(graph, dim=3, scale=pos_scale)
                for n, nd in graph.nodes(data=True):
                    nd["pos"] = pos[n]
        if not all(len(p) == 3 for p in pos.values()):
            raise ValueError("pos must be 3d, use the dim=3 kwarg in nx layouts")
        assert all(
            "pos" in graph.nodes[n] for n in graph
        ), "_init_positions failed to assign positions to all nx nodes"
        self.initial_pos = pos

    def _init_lights(self, lights):
        # see Defaults.lights for configuration examples
        al = AmbientLight("al")
        al.setColor(Defaults.background_ambient_light_intensity)
        aln = self.render.attachNewNode(al)
        self.render.setLight(aln)
        self.node_lights = []
        self.edge_lights = []
        for i, (kind, target, config) in enumerate(lights):
            light_name = f"{kind}_light_{i}"
            if kind == "directional":
                light = DirectionalLight(light_name)
            elif kind == "ambient":
                light = AmbientLight(light_name)
            elif kind == "point":
                light = PointLight(light_name)
            else:
                raise ValueError(f"light kind={kind} not supported")
            color = config.get("color")
            if color:
                light.setColor(color)
            light_node = self.render.attachNewNode(light)
            hpr = config.get("hpr")
            if hpr:
                light_node.setHpr(*hpr)
            pos = config.get("pos")
            if pos:
                light_node.setPos(pos)
            if target == "nodes":
                self.node_lights.append(light_node)
            elif target == "edges":
                self.edge_lights.append(light_node)
            elif target == "both":
                self.node_lights.append(light_node)
                self.edge_lights.append(light_node)
            else:
                raise ValueError(f"nodes, edges, or both; got target={target}")

    def _init_nodes(self):
        logger.info("")
        graph = self.g
        for i, (n, nd) in enumerate(graph.nodes(data=True)):
            pid = f"node_{i}"
            try:
                node: NodePath = self._init_panda3d_model(
                    pid, self.node_fp, self.node_lights
                )
            except AttributeError:
                logger.error("call _init_lights before _init_models")
            node.reparentTo(self.render)
            utils.set_color(node, nd["color"])
            node.setPos(*nd["pos"])
            tpid = f"node_{i}_text"
            text, text_ = self._init_panda3d_text(tpid, nd["label"], nd["label_color"])
            text.reparentTo(node)
            text.setScale(tuple(1 / sc for sc in node.getScale()))
            text.setZ(node.getBounds().getRadius() * 1.1)
            nd["model"] = node
            nd["text_np"] = text
            nd["text_tn"] = text_
            logger.debug(f"self.g.nodes[{n}] == {nd}")

    def _init_edges(self):
        logger.info("")
        graph = self.g
        for i, e in enumerate(graph.edges):
            if isinstance(graph, nx.MultiGraph):
                u, v, ek = e
            else:
                u, v = e
            pid = f"edge_{i}"
            edge: NodePath = self._init_panda3d_model(
                pid, self.edge_fp, self.edge_lights
            )
            edge.reparentTo(self.render)
            utils.set_color(edge, graph.edges[e]["color"])
            # rotate into place
            pu = graph.nodes[u]["pos"]
            pv = graph.nodes[v]["pos"]
            edge.setPos(*pu)
            dist = linalg.norm(pu - pv)
            edge.setScale(1, 1, dist / 2)  # models have Z size of 2
            d = np.array(pv - pu, dtype=float)
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
                max_k = max([k for _, _, k in graph.edges])
                edge.setH(edge, ek / max_k * 90)
            # TODO use lookAt
            tpid = f"edge_{i}_text"
            text, text_ = self._init_panda3d_text(
                tpid, graph.edges[e]["label"], graph.edges[e]["label_color"]
            )
            text.reparentTo(self.render)
            text.setPos(tuple((pu + pv) / 2.0))
            graph.edges[e]["model"] = edge
            graph.edges[e]["text_np"] = text
            graph.edges[e]["text_tn"] = text_

    def _init_models(self):
        logger.info("")
        self._init_nodes()
        self._init_edges()

    def _init_filters(self, bloom=True, cartoon=False):
        if not self.cam:
            return
        logger.info("")
        filters = CommonFilters(self.win, self.cam)
        if bloom:
            filters.setBloom()
        if cartoon:
            filters.setCartoonInk()

    def _preprocess_labels(
        self, node_labels, edge_labels, autolabel_edges, autolabel_nodes
    ):
        logger.info("")
        if autolabel_nodes or autolabel_edges and any([edge_labels, node_labels]):
            logger.info("overwriting labels, set autolabel False if undesired")
        if autolabel_nodes:
            node_labels = {nd: str(nd) for nd in self.g.nodes}
        if autolabel_edges:
            edge_labels = {ed: str(ed) for ed in self.g.edges}
        return node_labels, edge_labels

    def _init_filepaths(self):
        logger.info("")
        self.node_fp = FILES.get("node")
        if isinstance(self.g, nx.MultiDiGraph):
            self.edge_fp = FILES.get("edge_directed_bent")
        elif isinstance(self.g, nx.MultiGraph):
            self.edge_fp = FILES.get("edge_bent")
        elif isinstance(self.g, nx.DiGraph):
            self.edge_fp = FILES.get("edge_directed")
        else:
            self.edge_fp = FILES.get("edge")
        if self.edge_fp is None or self.node_fp is None:
            raise NotImplementedError

    def _init_keyboard_input(self):
        """register event handler for keyboard presses, update self._latest_key with keyboard input when called
        https://docs.panda3d.org/1.10/python/programming/hardware-support/keyboard-support#keystroke-events
        """
        if self.camera:
            self.buttonThrowers[0].node().setKeystrokeEvent("keystroke")
            self.accept("keystroke", self.latestKeyboardEvent)
        else:
            logger.debug("not initializing keystroke listener")

    def _init_camera(self):
        self.disableMouse()
        bd = self.render.getBounds()
        try:
            rad = np.linalg.norm(bd.getApproxCenter()) + bd.getRadius()
        except AssertionError:
            assert os.getenv("DEBUG") is not None
            rad = 5.0
        fov = min(self.camLens.fov) if self.camLens else 45
        radians_fov = fov / 180 * pi
        self.initial_camera_radius = rad / tan(radians_fov) * 1.75
        if self.camera:
            self.camera.setPos(0, -self.initial_camera_radius, 0)
        self.enableMouse()

    def _init_state_update_task(
        self,
        state_trans_delay,
        state_trans_func,
    ):
        self.state_trans_func = state_trans_func
        self.taskMgr.doMethodLater(
            state_trans_delay, self.stateUpdateTask, "StateUpdate"
        )

    def _init_panda3d_model(
        self,
        pid: str,
        egg_filepath: Path,
        lights=[],
        scale: Union[float, Vec3] = 1.0,
        color: Optional[Vec4] = None,
    ):
        logger.info(f"loading model: {egg_filepath}")
        mod0 = self.loader.loadModel(egg_filepath)
        if DO_LS:
            mod0.ls()
        mod0.setLightOff()
        for lt in lights:
            mod0.setLight(lt)
        mod = NodePath(pid)
        mod0.reparentTo(mod)
        mod.setScale(scale)
        if color:
            print(f"color={color}")
            utils.set_color(mod, color)
        return mod

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

    def latestKeyboardEvent(self, keyname):
        """record latest keystroke"""
        self._latest_key = keyname

    def stateUpdateTask(self, task):
        """main state update loop"""
        if self.state_trans_func:
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

    def flush_latest_keystroke(self) -> Optional[str]:
        """
        Returns:
            This function returns the latest keystroke (e.g. 'r') pressed by the user. If you call it before the user
            presses another key (or before they press any) you will get None.

        See https://docs.panda3d.org/1.10/python/programming/hardware-support/keyboard-support#keystroke-events for more
        information on the keystroke monitoring event system.
        """
        k = self._latest_key
        self._latest_key = None
        return k
