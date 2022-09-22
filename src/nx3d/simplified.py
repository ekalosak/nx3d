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
    if kwargs.pop("diffusion", False):
        diffusion(**kwargs)
    elif kwargs.pop("life", False):
        game_of_life(**kwargs)
    else:
        g = nx.frucht_graph()
        if kwargs.pop("directed", False):
            g = g.to_directed()
        plot(g, **kwargs)
