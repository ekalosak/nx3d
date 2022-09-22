import pytest

from nx3d.examples import gameoflife


def test_grid_neighbors_2d(n):
    if n < 2:
        pass
    nbrs = []
    for nb in gameoflife._grid_neighbors_2d((0, 0), n):
        nbrs.append(nb)
        assert not any(x < 0 for x in nb)
    assert len(nbrs) == 3
    assert (1, 0) in nbrs
    assert (0, 1) in nbrs
    assert (1, 1) in nbrs

    nbrs = []
    for nb in gameoflife._grid_neighbors_2d((n - 1, n - 1), n):
        nbrs.append(nb)
        assert not any(x >= n for x in nb)
    assert len(nbrs) == 3

    if n < 3:
        pass
    nbrs = []
    for nb in gameoflife._grid_neighbors_2d((0, 1), n):
        nbrs.append(nb)
        assert not any(x < 0 for x in nb)
    assert len(nbrs) == 5

    nbrs = []
    for nb in gameoflife._grid_neighbors_2d((1, 1), n):
        nbrs.append(nb)
    assert len(nbrs) == 8


def test_make_grid_2d(n):
    _ = gameoflife._make_grid_2d(n)


@pytest.mark.parametrize("kind", gameoflife.BOARD_KINDS)
def test_make_board(n, kind):
    g = gameoflife._make_board(kind, n)
    for nd in g:
        assert g.nodes[nd]["val"] == 0


@pytest.mark.parametrize("kind", gameoflife.BOARD_KINDS)
def test_do_life_0(n, kind):
    g = gameoflife._make_board(kind, n)
    g.nodes[(0, 0)]["val"] = 1
    gameoflife._do_life(g, 0, 0)
    for nd in g:
        assert g.nodes[nd]["val"] == 0


@pytest.mark.parametrize("kind", gameoflife.BOARD_KINDS)
def test_do_life_1(n, kind):
    g = gameoflife._make_board(kind, n)
    if n < 2:
        pass
    g.nodes[(0, 0)]["val"] = 1
    g.nodes[(1, 0)]["val"] = 1
    g.nodes[(2, 0)]["val"] = 1
    gameoflife._do_life(g, 0, 0)
    assert g.nodes[(0, 0)]["val"] == 0
    assert g.nodes[(1, 0)]["val"] == 1
    assert g.nodes[(2, 0)]["val"] == 0
    gameoflife._do_life(g, 0, 0)
    for nd in g:
        assert g.nodes[nd]["val"] == 0


@pytest.mark.parametrize("kind", gameoflife.BOARD_KINDS)
def test_do_life_2(n, kind):
    g = gameoflife._make_board(kind, n)
    g.nodes[(0, 0)]["val"] = 1
    g.nodes[(2, 0)]["val"] = 1
    g.nodes[(1, 2)]["val"] = 1
    gameoflife._do_life(g, 0, 0)
    assert g.nodes[(0, 0)]["val"] == 0
    assert g.nodes[(2, 0)]["val"] == 0
    assert g.nodes[(1, 2)]["val"] == 0
    assert g.nodes[(1, 1)]["val"] == 1
    gameoflife._do_life(g, 0, 0)
    for nd in g:
        assert g.nodes[nd]["val"] == 0
