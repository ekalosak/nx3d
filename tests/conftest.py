import networkx as nx
import pytest

g_data = [
    nx.frucht_graph(),
    nx.grid_2d_graph(8, 8),
]


@pytest.fixture(params=g_data)
def g(request):
    return request.param


@pytest.fixture(params=[1, 2, 4, 8, 16])
def n(request) -> int:
    return request.param


@pytest.fixture(params=[(2, 2), (3, 3), (8, 8), (3, 3, 3)])
def dim(request):
    return request.param
