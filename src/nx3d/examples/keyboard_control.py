import time

import networkx as nx

import nx3d

FPS = 32.0


def keyboard_control(g=nx.erdos_renyi_graph(45, 0.05)):
    """A simple interactive example that lets the user dim and brighten the node colors with the ``y`` and ``u`` keys."""
    app = nx3d.Nx3D(g)  # note that this will initialize g.nodes[...]['color']
    while 1:
        app.taskMgr.step()
        time.sleep(1 / FPS)
        k = app.flush_latest_keystroke()
        if k == "u":
            for _, nd in g.nodes(data=True):
                nd["color"] = tuple(c * 1.1 for c in nd["color"])
        elif k == "y":
            for _, nd in g.nodes(data=True):
                nd["color"] = tuple(c * 0.9 for c in nd["color"])


if __name__ == "__main__":
    keyboard_control()
