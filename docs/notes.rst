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
