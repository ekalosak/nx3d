IN PROGRESS:

TODO:
- NX-0 P0 support for DiGraph and MultiDiGraph
  - DiGraph model, interface
  - MultiGraph model, interface
  - MultiDiGraph model, interface
- NX-2 P2 implement DEMO with state transformation
  - blocked by NX-11
  - blocked by NX-5
- NX-11 P2 allow plotting features to be controlled uisng graph attributes e.g. `g.nodes[nd]['color']`
- NX-19 P3 fix frame increment and time increment inputs to `state_trans_func`
  - di is always 0
  - dt is incorrect value i.e. task.time for delay task does not appear to be the delta time between executions
