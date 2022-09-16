import sys

import nx3d

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug = "debug" in sys.argv
        autolabel = "autolabel" in sys.argv
        verbose = "verbose" in sys.argv
        plot_axes = "plot_axes" in sys.argv
        cam_mouse_control = "cam_mouse_control" in sys.argv
    else:
        debug = False
    nx3d.demo(
        debug,
        autolabel=autolabel,
        verbose=verbose,
        plot_axes=plot_axes,
        cam_mouse_control=cam_mouse_control,
    )
