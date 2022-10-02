# Sun Oct 2 2022
22.10.4
- game of life on a graph
- edge case handling in core.py for when node are on top of each other i.e. p1 == p0
- small refactoring in core.py

# Sat Oct 1 2022
22.10.3
- updated description

22.10.2 - Interactivity
- added loguru as a dependency; env vars DEBUG, INFO, and TRACE configure via core.py
- learned about existing alternatives for 3d nx.graph plotting; added to docs/index.rst
- added nofilter and nogui options to Nx3D init
- added window property config options to Nx3D init
- added keyboard input passthrough; see docs/usage.rst
- added example for keyboard input passthrough
- moved gifs to docs/data/
- moved limitations docs page to index
- expanded and unlinked docs/notes.rst
- revised docs/usage.rst; added section on interactivity

# Fri Sep 24 2022
22.10.1 - Complete nx support
- implemented multi di graph

22.10.0
- implemented multi-graph
- edge radius no longer supported due to difficulty scaling bent edges
- added time to gui
- refactor of camera initialization
- added v3 3D models

# Wed Sep 22 2022
22.9.10
- added scipy as a dependency to handle sparse solvers for positions when there are > 500 nodes (see networkx spring layout source)
- moved issue tracking from text to github issues
- added a variety of "markers" for nodes (rather than just the icosahedron)
- refactored examples to handle n>1 examples
- working 2d grid game of life example
- docs got a full makeover
- implemented digraph support

# Sun Sep 19 2022
22.9.9
- no longer deepcopying the graph passed to the plotting function
- using nx graph attributes to track desired 3d model state
- added CI and tests

22.9.8
- implemented edge attribute interface for 'label' and 'color'

22.9.7
- implemented state transition function so now dynamic graphs are renderable
- implemented graph diffusion example to demo state transition functionality
- try `python -m nx3d diffusion`

# Sat Sep 18 2022
22.9.6
- refactored and set up for DiGraph support
- lighting improvements
- debugged edge and node labels, colors
- renamed main class from NxPlot to Nx3D

# Sat Sep 17 2022
22.9.5
- revved version to propagate README fix, essentially a no-op

22.9.4
- BREAKING CHANGE: removed plot_nx3d in favor of using the NxPlot class directly
- implemented keyboard and mouse camera controlls
- implemented GUI
- implemented undocumented but tiny CLI
- added lots of debugging features
- lighting improvements
- node labels implemented, buggy
- edge labels implemented, buggy
- label colors implemented, buggy

# Thurs Sep 15 2022
22.9.3
- Updated with ReadTheDocs webhooks, no change in functionality but revved to push the updated README to PyPi

22.9.2
- Removed metadata from `__init__.py`; all that goes in pyproject.toml
- Added docs/
- Configurable colors and sizes

# Wed Sep 14 2022
22.9.1
- Fixing packaging
- Looser requirements for dependencies rather than arbitrarily specifying latest
- Added `__main__.py`
- Added metadata and explicit imports to `__init__.py`

22.9.0
- First release with minimum viable featureset:
  - plots nodes
  - plots edges
