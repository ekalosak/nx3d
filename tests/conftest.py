import networkx as nx
from pytest import fixture


@fixture
def g():
    return nx.frucht_graph()
