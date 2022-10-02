import nx3d


def test_import():
    ...


def test_instantiation(g):
    app = nx3d.Nx3D(g, windowType="none")
    app.destroy()
