Limitations
==============================
The major known limitations are listed on this page. For more detail, see the issue tracker.


large graphs
------------------------------
Currently, this project will start to clip (non-smooth 3d visuals) when the graph has >250 nodes on my 5yr old macbook.

graph attribute control
------------------------------
``nx3d`` doesn't have all the same controls that Matplotlib does. While you can set size, label, color, and position -
some attributes like marker kind aren't yet available. See `this
milestone<https://github.com/ekalosak/nx3d/milestone/3`_ for progress on these features.
