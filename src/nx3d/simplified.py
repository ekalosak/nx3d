import networkx as nx

from nx3d.core import Nx3D
from nx3d.examples import diffusion_example


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
        for kw in ["verbose", "plot_axes", "autolabel", "mouse"]:
            kwargs[kw] = not kwargs.get(kw, False)
    app = Nx3D(g, **kwargs)
    app.run()


def demo(**kwargs):
    """Runs a demo visualization. Good for checking that your installation worked."""
    if kwargs.pop("diffusion", False):
        diffusion_example(**kwargs)
    else:
        g = nx.frucht_graph()
        plot(g, **kwargs)
