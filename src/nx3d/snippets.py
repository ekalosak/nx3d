import numpy as np
import pyvista as pv


def spline_demo():
    theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    z = np.linspace(-2, 2, 100)
    r = z**2 + 1
    x = r * np.sin(theta)
    y = r * np.cos(theta)
    points = np.column_stack((x, y, z))
    spline = pv.Spline(points, 1000)
    line = pv.Line()
    tube = line.tube(radius=0.02)
    stube = spline.tube(radius=0.2)
    stube.plot()
