Developer Notes
================================================
These are my notes, they may be helpful to people hacking on nx3d - if you are trying to use the package, you've come
too far.

3D modeling
-----------------------------

Blender -> nx3d
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You have two choices for getting Blender (free 3D modeling tool) models into Panda3D. Their docs cover it under 'Panda3D
Tools'. One is using the Blender 2.7 YABEE extension to export to .egg; the other a commandline tool to convert .blend
to .bam.  Don't mess with YABEE, it is apt to crash.

Units and dimensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In Blender base units,
- radius of edges is 0.2
- height of edges is 2
- radius of node is 1

Lighting
-----------------------------
- models MAY come with their own lights! To handle this, there is a _model.setLightOff() in _init_panda3d_model.
- default lighting is an ambient light with color (1, 1, 1, 1)

Sources:
- https://discourse.panda3d.org/t/cant-find-docs-about-pandas-default-lighting/11328/5
- https://discourse.panda3d.org/t/how-to-disable-the-ambient-light-in-a-panda3d-environment/15755

Window properties
-----------------------------
- https://arsthaumaturgis.github.io/Panda3DTutorial.io/tutorial/tut_lesson01.html

Debugging
-----------------------------

Examine the 3d models while the app is running
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from panda3d.core import loadPrcFileData
loadPrcFileData("", "want-directtools #t")
loadPrcFileData("", "want-tk #t")
