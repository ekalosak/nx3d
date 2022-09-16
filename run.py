import networkx as nx

import nx3d

g = nx.grid_2d_graph(16, 24)
my_app = nx3d.plot_nx3d(g)
my_app.run()
