from panda3d.core import Material, NodePath


def set_color(ob: NodePath, color):
    # FIXME this should replace the existing mat if any to be idempotent; can lead to memory leak? via scene graph
    # growth due to adding and adding mats w.o update.
    mat = Material()
    mat.setShininess(5.0)
    mat.setBaseColor(color)
    ob.setMaterial(mat, 1)
