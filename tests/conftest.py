import networkx as nx
import pytest


@pytest.fixture
def g():
    return nx.frucht_graph()


# @pytest.fixture(params=[1, 2, 4, 8, 16])
@pytest.fixture(params=[4])
def n(request) -> int:
    return request.param
