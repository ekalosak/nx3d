""" This source provides the simplified plotting functionality you can use if you don't want to deal with base classes
or overmuch customization. """
import networkx as nx

from nx3d.core import Nx3D
from nx3d.examples import diffusion, game_of_life


def plot(g: nx.Graph, debug=False, **kwargs):
    """Plot my graph now!

    This is where you should start. Calling this function on your graph will cause a pop-up
    containing the visualization to appear.

    Args:
        g (nx.Graph): The graph you'd like to plot.
        debug (bool): Set to debug mode, entailing rendered and stdout debugging information, negates other debug-like args
        kwargs: Passed to main class initialization, see Nx3D's docs for more info.

    Returns:
        None
    """
    if debug:
        for kw in ["verbose", "plot_axes", "autolabel", "mouse"]:
            kwargs[kw] = not kwargs.get(kw, False)
    app = Nx3D(g, **kwargs)
    app.run()


def demo(**kwargs):
    """Runs a demo visualization. Good for checking that your installation worked."""
    if kwargs.pop("pete", 0):
        g = nx.petersen_graph()
    elif kwargs.pop("tutt", 0):
        g = nx.tutte_graph()
    elif kwargs.pop("sedg", 0):
        g = nx.sedgewick_maze_graph()
    elif kwargs.pop("tetr", 0):
        g = nx.tetrahedral_graph()
    elif kwargs.pop("comp", 0):
        g = nx.complete_graph(13)
    elif kwargs.pop("compbi", 0):
        g = nx.complete_bipartite_graph(3, 5)
    elif kwargs.pop("barb", 0):
        g = nx.barbell_graph(10, 10)
    elif kwargs.pop("loll", 0):
        g = nx.lollipop_graph(10, 20)
    elif kwargs.pop("erdo", 0):
        g = nx.erdos_renyi_graph(45, 0.05)
    elif kwargs.pop("watt", 0):
        g = nx.watts_strogatz_graph(30, 3, 0.1)
    elif kwargs.pop("bara", 0):
        g = nx.barabasi_albert_graph(30, 3)
    elif kwargs.pop("lobs", 0):
        g = nx.random_lobster(8, 0.6, 0.2)
    else:
        g = nx.frucht_graph()

    if kwargs.pop("mul", False):
        _g = nx.MultiGraph(k=2)
        _g.add_nodes_from(g)
        for i in range(2):
            _g.add_edges_from(g.edges)
        g = _g
    if kwargs.pop("dir", False):
        g = g.to_directed()
    if isinstance(g, nx.MultiGraph):
        for e in g.edges:
            ek = e[2]
            mc = max([k for _, _, k in g.edges])
            c = (ek + 0.5) / (mc + 2)
            g.edges[e]["color"] = (c, c * 1.1, c, 1)
    else:
        c = 0.5 / 3
        for e in g.edges:
            g.edges[e]["color"] = (c, c * 1.1, c, 1)

    # The examples can optionally use these graph attributes as config - not common to the Nx3D that they pass kwargs to
    g.graph["show_labels"] = not kwargs.pop("nolabel", 1)

    if kwargs.pop("diffusion", False):
        diffusion(g, windowtitle="Nx3D - diffusion demo", **kwargs)
    elif kwargs.pop("life", False):
        game_of_life(windowtitle="Nx3D - Game of Life demo", **kwargs)
    else:
        plot(g, **kwargs)
