from nx3d.examples import gameoflife


def test_grid_neighbors_2d(n):
    if n < 2:
        pass
    nbrs = []
    for nb in gameoflife._grid_neighbors_2d((0, 0), n):
        nbrs.append(nb)
        assert not any(x < 0 for x in nb)
    assert len(nbrs) == 2
    assert (1, 0) in nbrs
    assert (0, 1) in nbrs

    nbrs = []
    for nb in gameoflife._grid_neighbors_2d((n - 1, n - 1), n):
        nbrs.append(nb)
        assert not any(x >= n for x in nb)
    assert len(nbrs) == 2

    nbrs = []
    for nb in gameoflife._grid_neighbors_2d((n - 1, n - 1), n):
        nbrs.append(nb)
        assert not any(x >= n for x in nb)
    assert len(nbrs) == 2


def test_make_grid_2d(n):
    g = gameoflife._make_grid_2d(n)
