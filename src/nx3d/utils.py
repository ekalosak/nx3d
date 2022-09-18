from panda3d.core import Material, NodePath

def set_color(ob: NodePath, color):
    mat = Material()
    mat.setShininess(5.0)
    mat.setBaseColor(color)
    ob.setMaterial(mat, 1)
